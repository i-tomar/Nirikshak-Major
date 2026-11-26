"""
NIRIKSHAK AI — Investigative Leads & Alerts Router (Phase 4)

Endpoints:
- GET /api/alerts: Retrieve ranked, prioritized investigative leads with configurable filters.
- GET /api/alerts/{id}: Inspect full lead dossier, including Why-Flagged evidence and sub-scores.
"""

import json

import duckdb
from app.ml.analyzer import get_analysis_paths, has_analysis_data
from app.ml.evidence import EvidenceReason
from app.schemas.analysis import (
    AlertDetailResponse,
    AlertItem,
    AlertsListResponse,
)
from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter()


@router.get("", response_model=AlertsListResponse, status_code=status.HTTP_200_OK)
def list_alerts(
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of leads to return"
    ),
    min_risk_score: float = Query(
        0.0, ge=0.0, le=100.0, description="Minimum risk score threshold"
    ),
    risk_level: str | None = Query(
        None, description="Filter by risk tier: CRITICAL, HIGH, MEDIUM, LOW"
    ),
):
    """
    Retrieve ranked investigative leads sorted deterministically by risk score and anomaly score.
    """
    if not has_analysis_data():
        return AlertsListResponse(
            total_leads=0,
            filtered_count=0,
            returned_count=0,
            leads=[],
        )

    leads_path = get_analysis_paths()["leads"].resolve().as_posix()
    tier = risk_level.strip().upper() if risk_level else None
    query_args = [leads_path, min_risk_score, tier, tier]
    with duckdb.connect() as con:
        total_leads_row = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)", [leads_path]
        ).fetchone()
        total_leads = int(total_leads_row[0]) if total_leads_row else 0
        filtered_count_row = con.execute(
            """SELECT COUNT(*) FROM read_parquet(?)
               WHERE risk_score >= ? AND (? IS NULL OR upper(risk_level) = ?)""",
            query_args,
        ).fetchone()
        filtered_count = int(filtered_count_row[0]) if filtered_count_row else 0
        df_results = con.execute(
            """SELECT alert_id, rank, wallet_address, risk_score, risk_level,
                      anomaly_score, anomaly_percentile, transaction_count,
                      total_input_amount + total_output_amount AS total_volume,
                      unique_ip_count, unique_country_count, reasons_json
               FROM read_parquet(?)
               WHERE risk_score >= ? AND (? IS NULL OR upper(risk_level) = ?)
               ORDER BY rank LIMIT ?""",
            [*query_args, limit],
        ).fetch_df()

    items: list[AlertItem] = []
    for _, r in df_results.iterrows():
        reasons_list = json.loads(r["reasons_json"]) if r["reasons_json"] else []
        primary_reason = (
            reasons_list[0]["explanation"]
            if reasons_list
            else f"Entity flagged with {r['risk_level']} risk priority."
        )

        items.append(
            AlertItem(
                alert_id=str(r["alert_id"]),
                rank=int(r["rank"]),
                wallet_address=str(r["wallet_address"]),
                risk_score=float(r["risk_score"]),
                risk_level=str(r["risk_level"]),
                anomaly_score=float(r["anomaly_score"]),
                anomaly_percentile=float(r["anomaly_percentile"]),
                transaction_count=int(r["transaction_count"]),
                total_volume=round(float(r["total_volume"]), 4),
                unique_ip_count=int(r["unique_ip_count"]),
                unique_country_count=int(r["unique_country_count"]),
                primary_reason=primary_reason,
            )
        )

    return AlertsListResponse(
        total_leads=total_leads,
        filtered_count=filtered_count,
        returned_count=len(items),
        leads=items,
    )


@router.get(
    "/{alert_id}", response_model=AlertDetailResponse, status_code=status.HTTP_200_OK
)
def get_alert_detail(alert_id: str):
    """
    Retrieve full investigative dossier for a specific lead by alert ID or wallet address.
    """
    if not has_analysis_data():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis results available. Run /api/analysis/run first.",
        )

    leads_path = get_analysis_paths()["leads"].resolve().as_posix()
    clean_id = alert_id.strip()
    with duckdb.connect() as con:
        df = con.execute(
            """SELECT * FROM read_parquet(?)
               WHERE alert_id = ? OR wallet_address = ? LIMIT 1""",
            [leads_path, clean_id, clean_id],
        ).fetch_df()
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investigative lead not found"
        )

    r = df.iloc[0].to_dict()
    reasons_raw = json.loads(r.get("reasons_json", "[]"))
    reasons = [EvidenceReason(**res) for res in reasons_raw]

    subscores = {
        "anomaly": float(r.get("sub_anomaly_score", 0.0)),
        "activity": float(r.get("sub_activity_score", 0.0)),
        "network": float(r.get("sub_network_score", 0.0)),
        "behavior": float(r.get("sub_behavior_score", 0.0)),
    }

    feature_metrics = {
        "transaction_count": int(r.get("transaction_count", 0)),
        "input_transaction_count": int(r.get("input_transaction_count", 0)),
        "output_transaction_count": int(r.get("output_transaction_count", 0)),
        "total_input_amount": float(r.get("total_input_amount", 0.0)),
        "total_output_amount": float(r.get("total_output_amount", 0.0)),
        "wallet_degree": int(r.get("wallet_degree", 0)),
        "unique_counterparties": int(r.get("unique_counterparty_count", 0)),
        "burstiness": float(r.get("burstiness", 0.0)),
        "amount_fragmentation_score": float(r.get("amount_fragmentation_score", 0.0)),
    }

    transaction_summary = {
        "total_transactions": int(r.get("transaction_count", 0)),
        "total_input_btc": float(r.get("total_input_amount", 0.0)),
        "total_output_btc": float(r.get("total_output_amount", 0.0)),
        "first_seen": str(r.get("first_seen", "")),
        "last_seen": str(r.get("last_seen", "")),
    }

    network_summary = {
        "unique_ip_count": int(r.get("unique_ip_count", 0)),
        "unique_country_count": int(r.get("unique_country_count", 0)),
        "unique_asn_count": int(r.get("unique_asn_count", 0)),
    }

    return AlertDetailResponse(
        alert_id=str(r["alert_id"]),
        rank=int(r["rank"]),
        wallet_address=str(r["wallet_address"]),
        risk_score=float(r["risk_score"]),
        risk_level=str(r["risk_level"]),
        anomaly_score=float(r["anomaly_score"]),
        anomaly_percentile=float(r["anomaly_percentile"]),
        subscores=subscores,
        reasons=reasons,
        feature_metrics=feature_metrics,
        transaction_summary=transaction_summary,
        network_summary=network_summary,
    )
