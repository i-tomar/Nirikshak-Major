"""Run and publish the offline wallet analysis."""

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from time import perf_counter

import polars as pl
from app.ml.anomaly import AnomalyModel
from app.ml.clustering import run_behavioral_clustering
from app.ml.features import extract_wallet_features
from app.ml.risk import rank_leads
from app.schemas.analysis import AnalysisStatusResponse, AnalysisSummary

ANALYSIS_DIR = Path(__file__).resolve().parents[2] / "data" / "analysis"
ANALYSIS_LOCK = Lock()


def get_analysis_paths(directory: Path = ANALYSIS_DIR) -> dict[str, Path]:
    return {
        name: directory / filename
        for name, filename in {
            "features": "wallet_features.parquet",
            "anomalies": "wallet_anomalies.parquet",
            "leads": "investigative_leads.parquet",
            "summary": "analysis_summary.json",
        }.items()
    }


def has_analysis_data() -> bool:
    return all(path.is_file() for path in get_analysis_paths().values())


def get_analysis_status() -> AnalysisStatusResponse:
    if not has_analysis_data():
        return AnalysisStatusResponse(has_analysis=False)
    summary = AnalysisSummary.model_validate_json(
        get_analysis_paths()["summary"].read_bytes()
    )
    return AnalysisStatusResponse(has_analysis=True, **summary.model_dump())


def run_full_analysis() -> AnalysisSummary:
    """Compute all outputs before replacing any previously published tables."""
    with ANALYSIS_LOCK, TemporaryDirectory(dir=ANALYSIS_DIR.parent) as tmp:
        start = perf_counter()
        staged = get_analysis_paths(Path(tmp))
        features = extract_wallet_features()
        if features.is_empty():
            raise ValueError("The normalized dataset contains no wallets")
        anomalies = AnomalyModel().fit_score(features)
        leads = rank_leads(features, anomalies)
        median_count = float(features["transaction_count"].median())
        leads = (
            leads.with_row_index("rank", offset=1)
            .with_columns(
                pl.concat_str(
                    [
                        pl.lit("ALT-"),
                        pl.col("rank").cast(pl.String).str.pad_start(4, "0"),
                        pl.lit("-"),
                        pl.col("wallet_address").str.slice(0, 8),
                    ]
                ).alias("alert_id"),
                pl.struct(
                    category=pl.lit("activity"),
                    feature=pl.lit("transaction_count"),
                    value=pl.col("transaction_count"),
                    baseline=pl.lit(median_count),
                    explanation=pl.format(
                        "Observed {} transactions. The dataset median is {}.",
                        pl.col("transaction_count"),
                        pl.lit(median_count),
                    ),
                )
                .struct.json_encode()
                .alias("reason"),
            )
            .with_columns(
                pl.concat_str([pl.lit("["), pl.col("reason"), pl.lit("]")]).alias(
                    "reasons_json"
                )
            )
            .drop("reason")
        )
        for name, table in (
            ("features", features),
            ("anomalies", anomalies),
            ("leads", leads),
        ):
            table.write_parquet(staged[name], compression="zstd")
        profiles, assignments = run_behavioral_clustering(features, leads=leads)
        assignments.write_parquet(Path(tmp) / "wallet_clusters.parquet")
        (Path(tmp) / "cluster_profiles.json").write_text(
            profiles.model_dump_json(), encoding="utf-8"
        )
        paths = get_analysis_paths()
        counts = dict(leads.group_by("risk_level").len().iter_rows())
        summary = AnalysisSummary(
            status="SUCCESS",
            analyzed_at=datetime.now(UTC).isoformat(),
            wallets_analyzed=len(features),
            anomalies_detected=int(anomalies["is_outlier"].sum()),
            critical_risk_leads=counts.get("CRITICAL", 0),
            high_risk_leads=counts.get("HIGH", 0),
            medium_risk_leads=counts.get("MEDIUM", 0),
            low_risk_leads=counts.get("LOW", 0),
            analysis_duration_seconds=perf_counter() - start,
            output_files={k: str(v) for k, v in paths.items()},
            clustering_enabled=True,
            cluster_count=profiles.total_clusters,
            clustered_wallets=len(features),
            silhouette_score_k6=profiles.diagnostics.selected_k_silhouette,
        )
        staged["summary"].write_text(summary.model_dump_json(), encoding="utf-8")
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        for filename in ("wallet_clusters.parquet", "cluster_profiles.json"):
            (Path(tmp) / filename).replace(ANALYSIS_DIR / filename)
        for key, path in staged.items():
            path.replace(paths[key])
        return summary
