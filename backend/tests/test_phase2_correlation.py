"""Runtime correlation tests with out-of-order and unmatched observations."""

import json
from pathlib import Path

import polars as pl
from app.graph.builder import build_investigation_graph
from app.main import app
from app.pipeline.correlation import build_correlations
from app.pipeline.storage import get_parquet_paths
from app.pipeline.streaming import ingest_file
from fastapi.testclient import TestClient


def _tables(root: Path) -> dict[str, Path]:
    paths = get_parquet_paths(root)
    pl.DataFrame(
        {
            "txid": ["tx-a", "tx-b"],
            "timestamp": ["2025-01-01T00:00:00Z", "2025-01-01T00:20:00Z"],
        }
    ).write_parquet(paths["transactions"])
    pl.DataFrame(
        {
            "txid": ["tx-b", None, "tx-a", None, "tx-a", None],
            "timestamp": [
                "2025-01-01T00:20:00Z",
                "2025-01-01T00:00:10Z",
                "2025-01-01T00:00:00Z",
                "2025-01-01T00:10:01Z",
                "2025-01-01T00:00:00Z",
                "2025-01-01T00:10:00Z",
            ],
            "src_ip": [
                "198.51.100.1",
                "203.0.113.4",
                "198.51.100.1",
                "203.0.113.5",
                "198.51.100.1",
                "203.0.113.6",
            ],
            "dst_ip": [
                "192.0.2.2",
                "192.0.2.3",
                "192.0.2.1",
                "192.0.2.4",
                "192.0.2.1",
                "192.0.2.5",
            ],
            "ASN": ["AS1", "AS2", "AS1", "AS3", "AS1", "AS4"],
        }
    ).write_parquet(paths["network_observations"])
    pl.DataFrame(
        {
            "txid": ["tx-a", "tx-b"],
            "wallet_address": ["wa", "wb"],
            "timestamp": ["2025-01-01T00:00:00Z", "2025-01-01T00:20:00Z"],
        }
    ).write_parquet(paths["tx_inputs"])
    pl.DataFrame(
        {
            "txid": ["tx-a", "tx-b"],
            "wallet_address": ["oa", "ob"],
            "timestamp": ["2025-01-01T00:00:00Z", "2025-01-01T00:20:00Z"],
        }
    ).write_parquet(paths["tx_outputs"])
    return paths


def test_window_duplicate_and_shared_links(tmp_path: Path):
    paths = _tables(tmp_path)
    assert build_correlations(tmp_path, window_seconds=600) > 0
    links = pl.read_parquet(paths["correlations"])
    wa = links.filter(pl.col("wallet_address") == "wa")
    assert (
        wa.filter(
            (pl.col("rule_name") == "asof_window")
            & (pl.col("target_id") == "203.0.113.4")
        ).height
        == 1
    )
    assert links.filter(pl.col("target_id") == "203.0.113.5").is_empty()
    assert (
        wa.filter(
            (pl.col("rule_name") == "asof_window")
            & (pl.col("target_id") == "203.0.113.6")
        ).height
        == 1
    )
    assert (
        wa.filter(
            (pl.col("rule_name") == "txid_join")
            & (pl.col("target_id") == "198.51.100.1")
        ).height
        == 1
    )
    assert (
        wa.filter(
            (pl.col("rule_name") == "shared_ip")
            & (pl.col("target_id") == "198.51.100.1")
        ).height
        >= 1
    )
    assert (
        float(
            str(
                wa.filter(
                    (pl.col("rule_name") == "first_seen_relay")
                    & (pl.col("target_id") == "198.51.100.1")
                )["confidence"].max()
            )
        )
        <= 0.30
    )
    assert (
        wa.filter(pl.col("rule_name") == "first_seen_relay")["caveat"]
        .str.contains("not necessarily")
        .all()
    )
    assert links.select(pl.col("rule_version").unique()).item() == "1"
    before = links.sort(links.columns)
    build_correlations(tmp_path, window_seconds=600)
    assert before.equals(pl.read_parquet(paths["correlations"]).sort(links.columns))


def test_wallet_api_returns_bounded_provenance(monkeypatch, tmp_path: Path):
    paths = _tables(tmp_path)
    build_correlations(tmp_path, window_seconds=600)
    import app.routers.correlations as route

    monkeypatch.setattr(route, "get_parquet_paths", lambda: paths)
    with TestClient(app) as client:
        response = client.get("/api/correlations/wa?limit=2")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 2
        assert len(body["links"]) == 2
        assert all(link["wallet_address"] == "wa" for link in body["links"])
        assert all(link["rule_name"] and link["caveat"] for link in body["links"])
        assert client.get("/api/correlations/wa?limit=201").status_code == 422
        assert client.get("/api/correlations/%27%20OR%201%3D1--").json()["total"] == 0


def test_graph_consumes_typed_correlation_edges(tmp_path: Path):
    source = tmp_path / "one.ndjson"
    source.write_text(
        json.dumps(
            {
                "txid": "a" * 64,
                "timestamp": "2025-01-01T00:00:00Z",
                "src_ip": "198.51.100.1",
                "dst_ip": "192.0.2.1",
                "src_port": 8333,
                "dst_port": 8333,
                "input_addresses": ["wa"],
                "output_addresses": ["oa"],
                "input_amounts": [1.0],
                "output_amounts": [0.9],
                "fee": 0.1,
                "script_type": "P2WPKH",
                "asn": "AS1",
            }
        ),
        encoding="utf-8",
    )
    data = tmp_path / "normalized"
    assert ingest_file(source, data)["valid_rows"] == 1
    graph, stats = build_investigation_graph(
        storage_dir=data,
        analysis_dir=tmp_path / "analysis",
        graph_dir=tmp_path / "graph",
        force_rebuild=True,
    )
    edge = graph["wallet:wa"]["ip:198.51.100.1"]
    assert edge["type"] == "correlation"
    assert edge["rule_name"] == "txid_join"
    assert edge["evidence_type"] == "direct"
    assert stats["correlation_edges"] > 0
