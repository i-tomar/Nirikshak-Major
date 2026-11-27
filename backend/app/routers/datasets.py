import json
import logging
import os
import time
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path, PureWindowsPath
from tempfile import TemporaryDirectory
from typing import Annotated, Any
from uuid import uuid4

import duckdb
import polars as pl
from app.graph.builder import (
    build_investigation_graph,
    get_graph_stats,
    has_graph_data,
    invalidate_graph_cache,
)
from app.ml.analyzer import (
    get_analysis_paths,
    has_analysis_data,
    run_full_analysis,
)
from app.pipeline.loader import (
    calculate_dataset_summary,
)
from app.pipeline.normalizer import normalize_dataset
from app.pipeline.storage import (
    get_dataset_analytics_summary,
    get_parquet_paths,
    get_storage_dir,
    has_normalized_data,
    save_normalized_tables,
)
from app.pipeline.streaming import IngestResult, ingest_file
from app.schemas.transaction import (
    ActiveDatasetStatus,
    BitcoinTransactionRecord,
    DatasetSummary,
    DatasetUploadResponse,
    StorageInfo,
)
from defusedxml.common import DefusedXmlException  # type: ignore[import-untyped]  # defusedxml has no typing marker.
from defusedxml.ElementTree import ParseError  # type: ignore[import-untyped]  # defusedxml safely raises this parser error.
from fastapi import APIRouter, File, HTTPException, UploadFile, status

UPLOAD_CHUNK_BYTES = 1024 * 1024
ARCHIVE_SIGNATURES = (
    b"PK\x03\x04",
    b"PK\x05\x06",
    b"\x1f\x8b",
    b"7z\xbc\xaf\x27\x1c",
    b"Rar!",
)
ALLOWED_UPLOAD_TYPES = {
    ".csv": {"text/csv", "application/vnd.ms-excel", "text/plain"},
    ".json": {"application/json", "text/json"},
    ".ndjson": {"application/x-ndjson", "application/json"},
    ".xml": {"application/xml", "text/xml"},
}


def upload_limit_bytes() -> int:
    """Read a configurable positive MiB upload limit."""
    raw = os.getenv("NIRIKSHAK_UPLOAD_MAX_MB", "500")
    try:
        size = int(raw)
    except ValueError as exc:
        raise ValueError("NIRIKSHAK_UPLOAD_MAX_MB must be a positive integer") from exc
    if size < 1:
        raise ValueError("NIRIKSHAK_UPLOAD_MAX_MB must be positive")
    return size * 1024 * 1024


def sniff_upload(header: bytes, suffix: str) -> None:
    """Reject archives, binary input and a mismatch with the declared extension."""
    if (
        any(signature in header for signature in ARCHIVE_SIGNATURES)
        or header[257:262] == b"ustar"
    ):
        raise HTTPException(status_code=400, detail="Archive uploads are not supported")
    if b"\x00" in header:
        raise HTTPException(
            status_code=400, detail="Binary dataset content is not supported"
        )
    try:
        text = header.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400, detail="Dataset must be UTF-8 text"
        ) from exc
    first = text.lstrip()
    if suffix == ".csv":
        matches = (
            "txid" in first.splitlines()[0].lower() and "," in first.splitlines()[0]
        )
    elif suffix in {".json", ".ndjson"}:
        matches = first.startswith(("{", "["))
    else:
        matches = first.startswith("<") and not first.startswith("<!DOCTYPE")
    if not matches:
        raise HTTPException(
            status_code=400, detail="Dataset content does not match its format"
        )


router = APIRouter()

MANIFEST_FILE = (
    Path(__file__).resolve().parent.parent.parent / "data" / "active_dataset.json"
)
CANONICAL_DEMO_CSV = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "demo"
    / "nirikshak_demo_15k.csv"
)
LEGACY_BENCHMARK_CSV = (
    Path(__file__).resolve().parent.parent.parent / "data" / "demo_transactions.csv"
)


def process_dataset_end_to_end(
    valid_records: list[BitcoinTransactionRecord],
    filename: str,
    detected_format: str,
    total_rows: int,
    rejected_records: list[dict[str, Any]],
    validation_status: str,
    val_ms: float,
) -> DatasetUploadResponse:
    """
    Executes the genuine end-to-end data processing lifecycle:
    1. Normalization & Parquet storage (Polars)
    2. ML Feature extraction, Isolation Forest, Risk Engine, Behavioral Clustering
    3. Multi-layer NetworkX graph compilation
    4. Process-level in-memory cache invalidation
    5. Active dataset manifest compilation with real measured stage durations
    """

    summary = calculate_dataset_summary(valid_records) if valid_records else None
    storage_info: StorageInfo | None = None
    stage_timings: dict[str, Any] = {"validation": val_ms}
    analysis_dict: dict[str, Any] | None = None
    graph_dict: dict[str, Any] | None = None
    pipeline_status = "SUCCESS"

    if valid_records and validation_status != "FAILED":
        try:
            # Stage 2: Normalization & Parquet Storage
            t_norm = time.perf_counter()
            tables = normalize_dataset(valid_records)
            written_paths = save_normalized_tables(tables)
            norm_ms = round((time.perf_counter() - t_norm) * 1000.0, 2)
            stage_timings["normalization"] = norm_ms

            sdir = get_storage_dir()
            storage_info = StorageInfo(
                normalized=True,
                storage_dir=str(sdir),
                transactions_file=written_paths.get("transactions", ""),
                wallets_file=written_paths.get("wallets", ""),
                network_observations_file=written_paths.get("network_observations", ""),
                table_counts={
                    "transactions": len(tables["transactions"]),
                    "wallets": len(tables["wallets"]),
                    "network_observations": len(tables["network_observations"]),
                },
            )

            # Stage 3: ML Analysis (Features, Isolation Forest, Risk Scoring, Behavioral Clustering)
            t_ml = time.perf_counter()
            analysis_summary = run_full_analysis()
            ml_ms = round((time.perf_counter() - t_ml) * 1000.0, 2)
            stage_timings["analysis"] = ml_ms
            analysis_dict = {
                "wallets_analyzed": analysis_summary.wallets_analyzed,
                "anomalies_detected": analysis_summary.anomalies_detected,
                "critical_risk_leads": analysis_summary.critical_risk_leads,
                "high_risk_leads": analysis_summary.high_risk_leads,
                "cluster_count": analysis_summary.cluster_count,
                "duration_seconds": analysis_summary.analysis_duration_seconds,
            }

            # Stage 4: Multi-Layer NetworkX Graph Construction & Cache Invalidation
            t_graph = time.perf_counter()
            invalidate_graph_cache()
            G, graph_stats = build_investigation_graph(force_rebuild=True)
            graph_ms = round((time.perf_counter() - t_graph) * 1000.0, 2)
            stage_timings["graph_compilation"] = graph_ms
            graph_dict = {
                "total_nodes": graph_stats.get("total_nodes", len(G.nodes)),
                "total_edges": graph_stats.get("total_edges", len(G.edges)),
                "wallet_nodes": graph_stats.get("wallet_nodes", 0),
                "transaction_nodes": graph_stats.get("transaction_nodes", 0),
            }

            total_elapsed = round(val_ms + norm_ms + ml_ms + graph_ms, 2)
            stage_timings["total"] = total_elapsed
            stage_timings["validation_ms"] = val_ms
            stage_timings["normalization_ms"] = norm_ms
            stage_timings["analysis_ms"] = ml_ms
            stage_timings["graph_build_ms"] = graph_ms
            stage_timings["total_ms"] = total_elapsed

            # Write Active Dataset Manifest atomically
            manifest_payload = {
                "has_dataset": True,
                "filename": filename,
                "detected_format": detected_format,
                "total_transactions": len(tables["transactions"]),
                "total_wallets": len(tables["wallets"]),
                "anomalies_detected": analysis_summary.anomalies_detected,
                "high_risk_leads": analysis_summary.high_risk_leads,
                "critical_risk_leads": analysis_summary.critical_risk_leads,
                "cluster_count": analysis_summary.cluster_count,
                "graph_nodes": graph_dict["total_nodes"],
                "graph_edges": graph_dict["total_edges"],
                "stage_timings_ms": stage_timings,
                "analyzed_at": datetime.now(UTC).isoformat(),
            }
            try:
                with open(MANIFEST_FILE, "w", encoding="utf-8") as mf:
                    json.dump(manifest_payload, mf, indent=2)
            except (OSError, TypeError, ValueError):
                logging.getLogger(__name__).warning(
                    "Could not persist dataset manifest"
                )

        except (OSError, ValueError, TypeError):
            pipeline_status = "FAILED"
            logging.getLogger(__name__).exception("Dataset processing failed")
            stage_timings["error"] = "Dataset processing failed"

    return DatasetUploadResponse(
        filename=filename,
        detected_format=detected_format,
        total_rows=total_rows,
        valid_rows=len(valid_records),
        rejected_rows=len(rejected_records),
        validation_status=validation_status,
        summary=summary,
        rejected_details=rejected_records[:50],
        storage=storage_info,
        pipeline_status=pipeline_status,
        stage_timings_ms=stage_timings,
        analysis_summary=analysis_dict,
        graph_summary=graph_dict,
    )


def respond_to_streamed_upload(
    result: IngestResult, filename: str, detected_format: str, elapsed_ms: float
) -> DatasetUploadResponse:
    """Expose measured data-layer results and run small-dataset analysis."""
    total = int(result["total_rows"])
    valid = int(result["valid_rows"])
    rejected = int(result["rejected_rows"])
    digest = str(result["source_sha256"])
    geoip_sources = result["geoip_sources"]
    logging.getLogger(__name__).info("Upload GeoIP sources: %s", geoip_sources)
    paths = get_parquet_paths()
    rejected_preview = pl.read_parquet(paths["rejected"]).head(50).to_dicts()
    if not valid:
        return DatasetUploadResponse(
            filename=filename,
            detected_format=detected_format,
            total_rows=total,
            valid_rows=0,
            rejected_rows=rejected,
            validation_status="FAILED",
            rejected_details=rejected_preview,
            pipeline_status="FAILED",
            source_sha256=digest,
            geoip_sources=geoip_sources,
            stage_timings_ms={"validation_ms": elapsed_ms},
            analysis_summary=None,
            graph_summary=None,
        )
    analytics = get_dataset_analytics_summary()
    summary = DatasetSummary(
        total_transactions=valid,
        unique_wallets=int(analytics["wallets"]),
        unique_ips=int(analytics["unique_ips"]),
        total_btc_volume=float(analytics["total_btc"]),
        time_range_start=str(analytics["time_range"]["start"]),
        time_range_end=str(analytics["time_range"]["end"]),
    )
    storage = StorageInfo(
        normalized=True,
        storage_dir=str(get_storage_dir()),
        transactions_file=str(paths["transactions"]),
        wallets_file=str(paths["wallets"]),
        network_observations_file=str(paths["network_observations"]),
        table_counts={
            name: int(pl.scan_parquet(path).select(pl.len()).collect().item())
            for name, path in paths.items()
        },
    )
    stages: dict[str, float] = {
        "validation_ms": elapsed_ms,
        "normalization_ms": elapsed_ms,
    }
    analysis_dict: dict[str, Any] | None = None
    graph_dict: dict[str, Any] | None = None
    pipeline_status = "PARTIAL"
    if valid <= 50_000:
        t_ml = time.perf_counter()
        analysis = run_full_analysis()
        stages["analysis_ms"] = round((time.perf_counter() - t_ml) * 1000, 2)
        analysis_dict = {
            "wallets_analyzed": analysis.wallets_analyzed,
            "anomalies_detected": analysis.anomalies_detected,
            "critical_risk_leads": analysis.critical_risk_leads,
            "high_risk_leads": analysis.high_risk_leads,
            "cluster_count": analysis.cluster_count,
            "duration_seconds": analysis.analysis_duration_seconds,
        }
        t_graph = time.perf_counter()
        invalidate_graph_cache()
        graph, graph_stats = build_investigation_graph(force_rebuild=True)
        stages["graph_build_ms"] = round((time.perf_counter() - t_graph) * 1000, 2)
        graph_dict = {
            "total_nodes": graph_stats.get("total_nodes", len(graph.nodes)),
            "total_edges": graph_stats.get("total_edges", len(graph.edges)),
        }
        pipeline_status = "SUCCESS"
    stages["total_ms"] = round(sum(stages.values()), 2)
    manifest = {
        "has_dataset": True,
        "filename": filename,
        "detected_format": detected_format,
        "total_transactions": valid,
        "total_wallets": int(analytics["wallets"]),
        "source_sha256": digest,
        "geoip_sources": geoip_sources,
        "stage_timings_ms": stages,
        "analyzed_at": datetime.now(UTC).isoformat() if analysis_dict else None,
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return DatasetUploadResponse(
        filename=filename,
        detected_format=detected_format,
        total_rows=total,
        valid_rows=valid,
        rejected_rows=rejected,
        validation_status="PASSED" if not rejected else "PARTIAL",
        summary=summary,
        rejected_details=rejected_preview,
        storage=storage,
        pipeline_status=pipeline_status,
        stage_timings_ms=stages,
        analysis_summary=analysis_dict,
        graph_summary=graph_dict,
        source_sha256=digest,
        geoip_sources=geoip_sources,
    )


@router.post(
    "/upload", response_model=DatasetUploadResponse, status_code=status.HTTP_200_OK
)
async def upload_dataset(
    file: Annotated[
        UploadFile, File(description="Bitcoin transaction dataset (.csv or .json)")
    ],
):
    """
    Ingest, validate, normalize, analyze, cluster, and compile the graph end-to-end
    for an uploaded Bitcoin transaction dataset.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    if "/" in file.filename or "\\" in file.filename or ".." in file.filename:
        raise HTTPException(status_code=400, detail="Invalid upload filename")
    filename = Path(PureWindowsPath(file.filename).name).name
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_UPLOAD_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported dataset format",
        )
    if (
        file.content_type
        and file.content_type.split(";", 1)[0].lower()
        not in ALLOWED_UPLOAD_TYPES[suffix]
    ):
        raise HTTPException(
            status_code=400, detail="Upload content type does not match its format"
        )
    detected_format = suffix.lstrip(".")
    upload_dir = Path(__file__).resolve().parents[2] / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=upload_dir) as temporary:
        stored_path = Path(temporary) / f"{uuid4().hex}{suffix}"
        digest = sha256()
        size = 0
        header = b""
        previous_tail = b""
        with stored_path.open("wb") as output:
            while chunk := await file.read(UPLOAD_CHUNK_BYTES):
                size += len(chunk)
                if size > upload_limit_bytes():
                    raise HTTPException(
                        status_code=413, detail="Upload size limit exceeded"
                    )
                if len(header) < 4096:
                    header += chunk[: 4096 - len(header)]
                if any(
                    signature in previous_tail + chunk
                    for signature in ARCHIVE_SIGNATURES
                ):
                    raise HTTPException(
                        status_code=400, detail="Archive uploads are not supported"
                    )
                previous_tail = chunk[-7:]
                digest.update(chunk)
                output.write(chunk)
        if not size or not header.strip():
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        sniff_upload(header, suffix)
        start = time.perf_counter()
        try:
            result = ingest_file(stored_path, source_name=filename)
        except (
            ValueError,
            UnicodeDecodeError,
            OSError,
            duckdb.Error,
            DefusedXmlException,
            ParseError,
        ) as exc:
            logging.getLogger(__name__).warning(
                "Dataset ingestion rejected", exc_info=exc
            )
            raise HTTPException(
                status_code=400, detail="Invalid dataset content"
            ) from exc
        if digest.hexdigest() != result["source_sha256"]:
            raise RuntimeError("Upload digest changed during ingestion")
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    if int(result["total_rows"]) == 0:
        raise HTTPException(status_code=400, detail="Dataset contains zero records")
    return respond_to_streamed_upload(result, filename, detected_format, elapsed_ms)


@router.post(
    "/load-benchmark",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_200_OK,
)
def load_benchmark_dataset():
    """
    Load the official SIH26146 demonstration dataset (15,000 transactions) directly
    from backend/data/demo/nirikshak_demo_15k.csv and run the exact same end-to-end processing pipeline.
    """
    target_csv = (
        CANONICAL_DEMO_CSV if CANONICAL_DEMO_CSV.exists() else LEGACY_BENCHMARK_CSV
    )
    if not target_csv.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demonstration dataset not found",
        )

    started = time.perf_counter()
    result = ingest_file(target_csv, source_name=target_csv.name)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return respond_to_streamed_upload(result, target_csv.name, "csv", elapsed_ms)


@router.get(
    "/active", response_model=ActiveDatasetStatus, status_code=status.HTTP_200_OK
)
def get_active_dataset_status():
    """
    Retrieve current system-wide active dataset state and stage execution timings.
    """
    if MANIFEST_FILE.exists():
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as mf:
                data = json.load(mf)
                return ActiveDatasetStatus(**data)
        except (OSError, ValueError, TypeError):
            logging.getLogger(__name__).warning("Could not read dataset manifest")

    # Fallback: check if normalized and analysis data exist on disk
    if has_normalized_data() and has_analysis_data():
        try:
            analytics = get_dataset_analytics_summary()
            summary_path = get_analysis_paths()["summary"]
            with open(summary_path, "r", encoding="utf-8") as sf:
                analysis_summary = json.load(sf)

            graph_stats = get_graph_stats() if has_graph_data() else {}
            fallback_filename = (
                CANONICAL_DEMO_CSV.name
                if CANONICAL_DEMO_CSV.exists()
                else "nirikshak_demo_15k.csv"
            )
            return ActiveDatasetStatus(
                has_dataset=True,
                filename=fallback_filename,
                total_transactions=analytics.get("transactions", 0),
                total_wallets=analytics.get("wallets", 0),
                anomalies_detected=analysis_summary.get("anomalies_detected", 0),
                high_risk_leads=analysis_summary.get("high_risk_leads", 0),
                critical_risk_leads=analysis_summary.get("critical_risk_leads", 0),
                cluster_count=analysis_summary.get("cluster_count", 6),
                graph_nodes=graph_stats.get("total_nodes", 0),
                graph_edges=graph_stats.get("total_edges", 0),
                analyzed_at=analysis_summary.get("analyzed_at"),
            )
        except (OSError, ValueError, TypeError):
            logging.getLogger(__name__).warning("Could not read analysis summary")

    return ActiveDatasetStatus(has_dataset=False)
