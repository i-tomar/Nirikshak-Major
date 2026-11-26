"""Phase 0 API security regressions."""

from urllib.parse import quote
from uuid import UUID

import polars as pl
from app.main import allow_origins, app
from app.routers import alerts, analysis
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
