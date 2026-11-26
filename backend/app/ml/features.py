"""Compute wallet features from normalized Parquet using DuckDB."""

from pathlib import Path

import duckdb
import polars as pl
from app.pipeline.storage import get_parquet_paths

NUMERICAL_FEATURE_NAMES = [
    "transaction_count",
    "input_transaction_count",
    "output_transaction_count",
    "total_input_amount",
    "total_output_amount",
    "average_transaction_amount",
    "transaction_amount_stddev",
    "wallet_degree",
    "unique_counterparty_count",
    "input_output_ratio",
    "activity_duration_seconds",
    "mean_time_gap_seconds",
    "burstiness",
    "amount_fragmentation_score",
    "unique_ip_count",
    "unique_asn_count",
    "unique_country_count",
    "network_observation_count",
    "mean_fee",
    "max_fee",
    "mean_inputs",
    "mean_outputs",
    "script_type_count",
    "night_activity_ratio",
]


def extract_wallet_features(storage_dir: Path | None = None) -> pl.DataFrame:
    """Aggregate one row per wallet, ordering timestamps before computing gaps."""
    paths = get_parquet_paths(storage_dir)
    with duckdb.connect() as conn:
        conn.read_parquet(str(paths["transactions"])).create_view("tx")
        conn.read_parquet(str(paths["wallets"])).create_view("wallets")
        return conn.sql("""
            WITH sides AS (
                SELECT txid, unnest(input_addresses) AS addr, unnest(input_amounts) AS amount FROM tx
                UNION ALL
                SELECT txid, unnest(output_addresses), unnest(output_amounts) FROM tx
            ), per_tx AS (
                SELECT addr, txid, sum(amount) AS volume FROM sides GROUP BY addr, txid
            ), events AS (
                SELECT p.*, t.* EXCLUDE (txid), epoch(timestamp::TIMESTAMPTZ) AS seconds
                FROM per_tx p JOIN tx t USING (txid)
            ), gaps AS (
                SELECT *, seconds - lag(seconds) OVER (PARTITION BY addr ORDER BY seconds, txid) AS gap
                FROM events
            ), obs AS (
                SELECT addr, count(DISTINCT ip) AS unique_ip_count FROM (
                    SELECT addr, unnest([src_ip, dst_ip]) AS ip FROM events
                ) GROUP BY addr
            ), pairs AS (
                SELECT DISTINCT unnest(input_addresses) AS source, output_addresses AS targets FROM tx
            ), directed AS (
                SELECT source, unnest(targets) AS target FROM pairs
            ), neighbors AS (
                SELECT source AS addr, target AS neighbor FROM directed
                UNION SELECT target, source FROM directed
            ), degree AS (
                SELECT addr, count(*) AS peers FROM neighbors WHERE addr <> neighbor GROUP BY addr
            ), agg AS (
                SELECT addr, avg(volume) AS average_transaction_amount,
                    stddev_pop(volume) AS transaction_amount_stddev,
                    max(seconds)-min(seconds) AS activity_duration_seconds,
                    coalesce(avg(gap),0) AS mean_time_gap_seconds,
                    coalesce((stddev_pop(gap)-avg(gap))/nullif(stddev_pop(gap)+avg(gap),0),0) AS burstiness,
                    avg(1.0 - 1.0 / greatest(output_count,1)) AS amount_fragmentation_score,
                    count(DISTINCT ASN) AS unique_asn_count, count(DISTINCT geo_country) AS unique_country_count,
                    count(*) AS network_observation_count, avg(fee) AS mean_fee, max(fee) AS max_fee,
                    avg(input_count) AS mean_inputs, avg(output_count) AS mean_outputs,
                    count(DISTINCT script_type) AS script_type_count,
                    avg((hour(timezone('UTC', timestamp::TIMESTAMPTZ)) < 6)::INT) AS night_activity_ratio
                FROM gaps GROUP BY addr
            )
            SELECT w.*, agg.* EXCLUDE (addr), obs.unique_ip_count,
                coalesce(degree.peers,0) AS wallet_degree, coalesce(degree.peers,0) AS unique_counterparty_count,
                (w.total_input_amount+0.00000001)/(w.total_output_amount+0.00000001) AS input_output_ratio
            FROM wallets w JOIN agg ON w.wallet_address=agg.addr JOIN obs USING (addr)
            LEFT JOIN degree USING (addr) ORDER BY w.wallet_address
        """).pl()
