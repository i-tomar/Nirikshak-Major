"""Phase 0 API security regressions."""

from hashlib import sha256
from urllib.parse import quote
from uuid import UUID

import polars as pl
from app.main import allow_origins, app
from app.pipeline.normalizer import normalize_dataset
from app.routers import alerts, analysis, investigations
from app.schemas.transaction import BitcoinTransactionRecord
from fastapi.testclient import TestClient


def test_internal_error_uses_request_id(monkeypatch, caplog):
    secret = r"SELECT private_data FROM test_table at C:\private\dataset.csv"

    def fail():
        raise RuntimeError(secret)

    monkeypatch.setattr(analysis, "has_normalized_data", lambda: True)
    monkeypatch.setattr(analysis, "run_full_analysis", fail)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/api/analysis/run")
    assert response.status_code == 500
    payload = response.json()
    assert payload["detail"] == "Internal server error"
    assert UUID(payload["request_id"]).hex == response.headers["X-Request-ID"]
    assert secret in caplog.text
    assert payload["request_id"] in caplog.text
    assert all(term not in response.text for term in ("SELECT", "private", "Traceback"))


def test_docs_and_cors_defaults():
    with TestClient(app) as client:
        for path in ("/docs", "/redoc", "/openapi.json"):
            assert client.get(path).status_code == 404
        for origin in allow_origins:
            response = client.get("/api/health", headers={"Origin": origin})
            assert response.headers["Access-Control-Allow-Origin"] == origin
        response = client.get(
            "/api/health", headers={"Origin": "https://unconfigured.invalid"}
        )
        assert "Access-Control-Allow-Origin" not in response.headers


def test_alert_queries_handle_unmatched_literals(monkeypatch, tmp_path):
    leads_path = tmp_path / "leads.parquet"
    pl.DataFrame(
        [
            {
                "alert_id": "ALT-0001",
                "rank": 1,
                "wallet_address": "wallet-fixture",
                "risk_score": 75.0,
                "risk_level": "HIGH",
                "anomaly_score": 0.8,
                "anomaly_percentile": 90.0,
                "transaction_count": 2,
                "total_input_amount": 1.0,
                "total_output_amount": 0.9,
                "unique_ip_count": 1,
                "unique_country_count": 1,
                "reasons_json": "[]",
            }
        ]
    ).write_parquet(leads_path)
    monkeypatch.setattr(alerts, "get_analysis_paths", lambda: {"leads": leads_path})
    monkeypatch.setattr(alerts, "has_analysis_data", leads_path.is_file)

    with TestClient(app) as client:
        leads = client.get("/api/alerts", params={"limit": 1})
        assert leads.status_code == 200
        assert leads.json()["returned_count"] == 1
        for value in ("O'Brien", "未知", "x" * 2048):
            collection = client.get("/api/alerts", params={"risk_level": value})
            assert collection.status_code == 200
            assert collection.json()["leads"] == []
            detail = client.get("/api/alerts/" + quote(value, safe=""))
            assert detail.status_code == 404
            assert detail.json() == {"detail": "Investigative lead not found"}
        assert client.get("/api/alerts", params={"limit": 1}).json() == leads.json()


def test_alert_sql_payloads_remain_literal_and_preserve_parquet(monkeypatch, tmp_path):
    """Exercise HTTP inputs against real DuckDB reads and immutable fixture files."""
    leads_path = tmp_path / "leads.parquet"
    other_path = tmp_path / "other.parquet"
    base = {
        "rank": 1,
        "risk_score": 75.0,
        "risk_level": "HIGH",
        "anomaly_score": 0.8,
        "anomaly_percentile": 90.0,
        "transaction_count": 2,
        "total_input_amount": 1.0,
        "total_output_amount": 0.9,
        "unique_ip_count": 1,
        "unique_country_count": 1,
        "reasons_json": "[]",
    }
    pl.DataFrame(
        [{**base, "alert_id": "ALT-0001", "wallet_address": "wallet-fixture"}]
    ).write_parquet(leads_path)
    pl.DataFrame(
        [{**base, "alert_id": "SECRET-0001", "wallet_address": "secret-wallet"}]
    ).write_parquet(other_path)
    before = {
        path: sha256(path.read_bytes()).hexdigest() for path in (leads_path, other_path)
    }
    monkeypatch.setattr(alerts, "get_analysis_paths", lambda: {"leads": leads_path})
    monkeypatch.setattr(alerts, "has_analysis_data", leads_path.is_file)
    payloads = (
        "' OR '1'='1",
        "' OR 1=1 --",
        "'; DROP TABLE x; --",
        f"' UNION SELECT * FROM read_parquet('{other_path.as_posix()}') --",
        "'; SELECT * FROM x; --",
        "'/*comment*/ OR 1=1 --",
        "\x00",
        "＇ OR １=１ --",
        "a" * 10_000,
        "../../private/leads.parquet",
        "..\\..\\private\\leads.parquet",
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        positive = client.get("/api/alerts/ALT-0001")
        assert positive.status_code == 200
        assert positive.json()["wallet_address"] == "wallet-fixture"
        for payload in payloads:
            for params in (
                {"risk_level": payload, "limit": 1},
                {"min_risk_score": payload, "limit": 1},
                {"limit": payload},
            ):
                response = client.get("/api/alerts", params=params)
                assert response.status_code in (200, 400, 404, 422)
                body = response.text
                assert "secret-wallet" not in body and "SECRET-0001" not in body
                assert all(
                    x not in body
                    for x in ("Traceback", "SELECT *", str(tmp_path), ".parquet")
                )
                if response.status_code == 200:
                    data = response.json()
                    assert data["returned_count"] <= 1
                    assert data["leads"] == []
            response = client.get("/api/alerts/" + quote(payload, safe=""))
            assert response.status_code in (400, 404, 422)
            assert "wallet-fixture" not in response.text
            assert "secret-wallet" not in response.text
            assert all(
                x not in response.text
                for x in ("Traceback", "SELECT *", str(tmp_path), ".parquet")
            )
            assert {
                path: sha256(path.read_bytes()).hexdigest() for path in before
            } == before
        assert (
            client.get("/api/alerts", params={"limit": 1}).json()["returned_count"] == 1
        )


def test_investigation_duckdb_inputs_do_not_reflect_or_change_data(
    monkeypatch, tmp_path
):
    record = BitcoinTransactionRecord(
        timestamp="2025-01-01T00:00:00Z",
        src_ip="192.0.2.1",
        dst_ip="192.0.2.2",
        src_port=8333,
        dst_port=8333,
        txid="a" * 64,
        input_addresses=["wallet-fixture"],
        output_addresses=["wallet-output"],
        input_amounts=[1.0],
        output_amounts=[0.9],
        fee=0.1,
        script_type="P2WPKH",
        geo_country="US",
        ASN="AS64500",
    )
    paths = {
        name: tmp_path / f"{name}.parquet"
        for name in ("transactions", "wallets", "network_observations")
    }
    for name, table in normalize_dataset([record]).items():
        if name in paths:
            table.write_parquet(paths[name])
    before = {path: sha256(path.read_bytes()).hexdigest() for path in paths.values()}
    monkeypatch.setattr(investigations, "has_normalized_data", lambda: True)
    monkeypatch.setattr(investigations, "get_parquet_paths", lambda: paths)
    monkeypatch.setattr(investigations, "has_analysis_data", lambda: False)
    payloads = (
        "' OR '1'='1",
        "' OR 1=1 --",
        "'; DROP TABLE x; --",
        "' UNION SELECT * FROM read_parquet('other.parquet') --",
        "'; SELECT 1; --",
        "\x00",
        "＇ OR １=１ --",
        "x" * 10_000,
        "../../private/leads.parquet",
        "..\\..\\private\\leads.parquet",
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        valid = client.get("/api/investigations/wallet-fixture")
        assert valid.status_code == 200
        assert valid.json()["wallet"]["address"] == "wallet-fixture"
        for payload in payloads:
            response = client.get("/api/investigations/" + quote(payload, safe=""))
            assert response.status_code in (400, 404, 422)
            assert "wallet-fixture" not in response.text
            assert all(
                x not in response.text
                for x in ("Traceback", "SELECT", str(tmp_path), ".parquet")
            )
            for param in ("tx_limit", "net_limit"):
                rejected = client.get(
                    "/api/investigations/wallet-fixture", params={param: payload}
                )
                assert rejected.status_code == 422
                assert all(
                    x not in rejected.text
                    for x in ("Traceback", "SELECT", str(tmp_path), ".parquet")
                )
            assert {
                path: sha256(path.read_bytes()).hexdigest() for path in before
            } == before
