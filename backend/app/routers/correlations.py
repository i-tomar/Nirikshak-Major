"""Bounded wallet network correlation evidence API."""

from typing import Any

import duckdb
from app.pipeline.storage import get_parquet_paths
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/{wallet}")
def wallet_correlations(
    wallet: str,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0, le=1_000_000),
) -> dict[str, Any]:
    """Return each network link, including rule, confidence and caveat."""
    if not wallet or len(wallet) > 256:
        raise HTTPException(status_code=400, detail="Invalid wallet identifier")
    path = get_parquet_paths()["correlations"]
    if not path.exists():
        raise HTTPException(status_code=404, detail="Correlation data is unavailable")
    with duckdb.connect(":memory:") as connection:
        connection.read_parquet(str(path)).create_view("correlations")
        rows = connection.execute(
            """SELECT wallet_address,target_type,target_id,txid,observation_txid,
              observation_timestamp,rule_name,rule_version,window_seconds,evidence_type,
              confidence,is_direct,caveat,data_source FROM correlations
              WHERE wallet_address = ?
              ORDER BY observation_timestamp,target_type,target_id,rule_name,txid
              LIMIT ? OFFSET ?""",
            [wallet, limit, offset],
        ).fetchall()
        columns = [item[0] for item in connection.description]
        total = connection.execute(
            "SELECT count(*) FROM correlations WHERE wallet_address = ?", [wallet]
        ).fetchone()
    return {
        "wallet_address": wallet,
        "total": int(total[0]) if total else 0,
        "limit": limit,
        "offset": offset,
        "links": [dict(zip(columns, row, strict=True)) for row in rows],
    }
