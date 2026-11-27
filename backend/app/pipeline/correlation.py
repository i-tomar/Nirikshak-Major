"""Deterministic wallet to network evidence joins over normalized Parquet."""

import os
from pathlib import Path

import duckdb

from app.pipeline.storage import get_parquet_paths

RULE_VERSION = "1"
FIRST_RELAY_CAVEAT = "First observed relay is not necessarily the transaction origin; NAT, VPNs and relay timing obscure origin."


def correlation_window_seconds() -> int:
    """Return a bounded, configurable maximum observation delay."""
    value = int(os.getenv("NIRIKSHAK_CORRELATION_WINDOW_SECONDS", "600"))
    if not 1 <= value <= 86400:
        raise ValueError("Correlation window must be 1..86400 seconds")
    return value


def build_correlations(
    storage_dir: str | Path | None = None, window_seconds: int | None = None
) -> int:
    """Build typed links without a Python object per observation or wallet."""
    window = correlation_window_seconds() if window_seconds is None else window_seconds
    if not 1 <= window <= 86400:
        raise ValueError("Correlation window must be 1..86400 seconds")
    paths = get_parquet_paths(storage_dir)
    for name in ("transactions", "network_observations", "tx_inputs", "tx_outputs"):
        if not paths[name].exists():
            raise FileNotFoundError("Required normalized table is missing")
    connection = duckdb.connect(":memory:")
    connection.execute("SET TimeZone='UTC'")
    for name in ("transactions", "network_observations", "tx_inputs", "tx_outputs"):
        connection.read_parquet(str(paths[name])).create_view(name)
    if paths["ip_enrichment"].exists():
        connection.read_parquet(str(paths["ip_enrichment"])).create_view(
            "ip_enrichment"
        )
    else:
        connection.execute("CREATE TEMP TABLE ip_enrichment(ip VARCHAR, asn VARCHAR)")
    connection.execute("""
        CREATE TEMP VIEW wallet_events AS
        SELECT DISTINCT txid, wallet_address, try_cast(timestamp AS TIMESTAMPTZ) AS event_time
        FROM (
          SELECT txid, wallet_address, timestamp FROM tx_inputs
          UNION ALL SELECT txid, wallet_address, timestamp FROM tx_outputs
        )
    """)
    connection.execute(
        "CREATE TEMP VIEW transaction_events AS SELECT DISTINCT txid, event_time FROM wallet_events"
    )
    connection.execute("""
        CREATE TEMP VIEW observations AS
        SELECT row_number() OVER (ORDER BY timestamp, coalesce(txid,''), src_ip, dst_ip) AS observation_id,
          txid AS observation_txid, try_cast(timestamp AS TIMESTAMPTZ) AS observed_at,
          src_ip, dst_ip, ASN
        FROM (SELECT DISTINCT txid, timestamp, src_ip, dst_ip, ASN FROM network_observations)
        WHERE try_cast(timestamp AS TIMESTAMPTZ) IS NOT NULL
    """)
    connection.execute(
        """
        CREATE TEMP TABLE matched AS
        SELECT w.wallet_address, w.txid, o.observation_txid, o.observation_id,
          o.observed_at, o.src_ip, o.dst_ip, o.ASN,
          'txid_join' AS match_rule, 0 AS window_seconds, 0.95 AS confidence, true AS is_direct
        FROM observations o JOIN wallet_events w ON o.observation_txid = w.txid
        UNION ALL
        SELECT w.wallet_address, w.txid, o.observation_txid, o.observation_id,
          o.observed_at, o.src_ip, o.dst_ip, o.ASN,
          'asof_window' AS match_rule, ? AS window_seconds, 0.55 AS confidence, false AS is_direct
        FROM (SELECT * FROM observations WHERE observation_txid IS NULL OR observation_txid = '') o
        ASOF JOIN transaction_events e ON o.observed_at >= e.event_time
        JOIN wallet_events w ON e.txid = w.txid
        WHERE date_diff('second', e.event_time, o.observed_at) <= ?
    """,
        [window, window],
    )
    connection.execute("""
        CREATE TEMP VIEW links AS
        SELECT DISTINCT wallet_address, txid, observation_txid, observation_id, observed_at,
          src_ip AS target_id, 'ip' AS target_type, match_rule, window_seconds, confidence, is_direct, true AS is_src
        FROM matched WHERE src_ip IS NOT NULL AND src_ip <> ''
        UNION
        SELECT DISTINCT wallet_address, txid, observation_txid, observation_id, observed_at,
          dst_ip, 'ip', match_rule, window_seconds, confidence, is_direct, false
        FROM matched WHERE dst_ip IS NOT NULL AND dst_ip <> ''
        UNION
        SELECT DISTINCT m.wallet_address, m.txid, m.observation_txid, m.observation_id, m.observed_at,
          coalesce(e.asn, m.ASN), 'asn', m.match_rule, m.window_seconds, m.confidence * 0.8, false, false
        FROM matched m LEFT JOIN ip_enrichment e ON m.src_ip=e.ip
        WHERE coalesce(e.asn, m.ASN) IS NOT NULL AND coalesce(e.asn, m.ASN) <> ''
        UNION
        SELECT DISTINCT m.wallet_address, m.txid, m.observation_txid, m.observation_id, m.observed_at,
          e.asn, 'asn', m.match_rule, m.window_seconds, m.confidence * 0.8, false, false
        FROM matched m JOIN ip_enrichment e ON m.dst_ip=e.ip
        WHERE e.asn IS NOT NULL AND e.asn <> ''
    """)
    connection.execute("""
        CREATE TEMP VIEW annotated AS
        SELECT *, count(DISTINCT wallet_address) OVER (PARTITION BY target_type, target_id) AS linked_wallets,
          dense_rank() OVER (PARTITION BY txid ORDER BY observed_at, observation_id) AS relay_order
        FROM links
    """)
    connection.execute(
        """
        COPY (
          SELECT wallet_address, target_type, target_id, txid, observation_txid,
            strftime(observed_at, '%Y-%m-%dT%H:%M:%S.%fZ') AS observation_timestamp,
            match_rule AS rule_name, ? AS rule_version, window_seconds,
            CASE WHEN target_type='asn' THEN 'contextual' WHEN is_direct THEN 'direct' ELSE 'inferred' END AS evidence_type,
            confidence, is_direct, 'Observed network infrastructure is not proof of wallet control.' AS caveat,
            'unlabelled_upload' AS data_source
          FROM annotated
          UNION ALL
          SELECT wallet_address, target_type, target_id, txid, observation_txid,
            strftime(observed_at, '%Y-%m-%dT%H:%M:%S.%fZ'),
            CASE WHEN target_type='ip' THEN 'shared_ip' ELSE 'shared_asn' END,
            ?, window_seconds, 'inferred', least(confidence, 0.45), false,
            'Shared infrastructure may serve unrelated users.', 'unlabelled_upload'
          FROM annotated WHERE linked_wallets > 1
          UNION ALL
          SELECT wallet_address, target_type, target_id, txid, observation_txid,
            strftime(observed_at, '%Y-%m-%dT%H:%M:%S.%fZ'),
            'first_seen_relay', ?, window_seconds, 'contextual', least(confidence, 0.30), false,
            ?, 'unlabelled_upload'
          FROM annotated WHERE target_type='ip' AND is_src AND relay_order=1 AND match_rule='txid_join'
          ORDER BY wallet_address, target_type, target_id, txid, rule_name, observation_timestamp
        ) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)
    """,
        [
            RULE_VERSION,
            RULE_VERSION,
            RULE_VERSION,
            FIRST_RELAY_CAVEAT,
            str(paths["correlations"]),
        ],
    )
    count = connection.execute(
        "SELECT count(*) FROM read_parquet(?)", [str(paths["correlations"])]
    ).fetchone()
    connection.close()
    return int(count[0]) if count else 0
