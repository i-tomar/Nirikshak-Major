"""
NIRIKSHAK AI — Data Normalization Pipeline (Phase 3)

Converts validated BitcoinTransactionRecord objects into three core normalized Polars DataFrames:
1. transactions: Transaction-level facts, amounts, aggregated volumes, and counts.
2. wallets: Aggregated wallet entity metrics (transactions, in/out volume, first/last seen).
3. network_observations: Network-layer broadcast observations tied to txids.
"""

from collections import defaultdict
from typing import TypedDict

import polars as pl
from app.pipeline.geoip import GeoIPResolver
from app.schemas.transaction import BitcoinTransactionRecord


class WalletAccumulator(TypedDict):
    input_txs: set[str]
    output_txs: set[str]
    total_input_amount: float
    total_output_amount: float
    timestamps: list[str]


def new_wallet_accumulator() -> WalletAccumulator:
    return {
        "input_txs": set(),
        "output_txs": set(),
        "total_input_amount": 0.0,
        "total_output_amount": 0.0,
        "timestamps": [],
    }


def normalize_transactions(records: list[BitcoinTransactionRecord]) -> pl.DataFrame:
    """
    Build normalized transactions DataFrame from validated records.
    """
    rows = []
    for r in records:
        rows.append(
            {
                "txid": r.txid,
                "timestamp": r.timestamp,
                "fee": float(r.fee),
                "script_type": r.script_type,
                "input_addresses": r.input_addresses,
                "output_addresses": r.output_addresses,
                "input_amounts": [float(x) for x in r.input_amounts],
                "output_amounts": [float(x) for x in r.output_amounts],
                "total_input_amount": round(sum(r.input_amounts), 8),
                "total_output_amount": round(sum(r.output_amounts), 8),
                "input_count": len(r.input_addresses),
                "output_count": len(r.output_addresses),
                "src_ip": r.src_ip,
                "dst_ip": r.dst_ip,
                "src_port": int(r.src_port),
                "dst_port": int(r.dst_port),
                "geo_country": r.geo_country,
                "ASN": r.ASN,
            }
        )

    schema: dict[str, type[pl.DataType] | pl.DataType] = {
        "txid": pl.Utf8,
        "timestamp": pl.Utf8,
        "fee": pl.Float64,
        "script_type": pl.Utf8,
        "input_addresses": pl.List(pl.Utf8),
        "output_addresses": pl.List(pl.Utf8),
        "input_amounts": pl.List(pl.Float64),
        "output_amounts": pl.List(pl.Float64),
        "total_input_amount": pl.Float64,
        "total_output_amount": pl.Float64,
        "input_count": pl.Int64,
        "output_count": pl.Int64,
        "src_ip": pl.Utf8,
        "dst_ip": pl.Utf8,
        "src_port": pl.Int64,
        "dst_port": pl.Int64,
        "geo_country": pl.Utf8,
        "ASN": pl.Utf8,
    }
    return pl.DataFrame(rows, schema=schema)


def normalize_wallets(records: list[BitcoinTransactionRecord]) -> pl.DataFrame:
    """
    Derive wallet/address-level analytical DataFrame.
    Calculates transaction counts, in/out volumes, and observation time spans.
    """
    wallets_info: defaultdict[str, WalletAccumulator] = defaultdict(
        new_wallet_accumulator
    )

    for r in records:
        for addr, amt in zip(r.input_addresses, r.input_amounts):
            wallets_info[addr]["input_txs"].add(r.txid)
            wallets_info[addr]["total_input_amount"] += amt
            wallets_info[addr]["timestamps"].append(r.timestamp)
        for addr, amt in zip(r.output_addresses, r.output_amounts):
            wallets_info[addr]["output_txs"].add(r.txid)
            wallets_info[addr]["total_output_amount"] += amt
            wallets_info[addr]["timestamps"].append(r.timestamp)

    wallet_rows = []
    for addr in sorted(wallets_info.keys()):
        info = wallets_info[addr]
        all_txs = info["input_txs"] | info["output_txs"]
        wallet_rows.append(
            {
                "wallet_address": addr,
                "transaction_count": len(all_txs),
                "input_transaction_count": len(info["input_txs"]),
                "output_transaction_count": len(info["output_txs"]),
                "total_input_amount": round(info["total_input_amount"], 8),
                "total_output_amount": round(info["total_output_amount"], 8),
                "first_seen": min(info["timestamps"]),
                "last_seen": max(info["timestamps"]),
            }
        )

    schema = {
        "wallet_address": pl.Utf8,
        "transaction_count": pl.Int64,
        "input_transaction_count": pl.Int64,
        "output_transaction_count": pl.Int64,
        "total_input_amount": pl.Float64,
        "total_output_amount": pl.Float64,
        "first_seen": pl.Utf8,
        "last_seen": pl.Utf8,
    }
    return pl.DataFrame(wallet_rows, schema=schema)


def normalize_network_observations(
    records: list[BitcoinTransactionRecord],
) -> pl.DataFrame:
    """
    Build network-layer observations DataFrame correlated by txid.
    """
    rows = []
    for r in records:
        rows.append(
            {
                "timestamp": r.timestamp,
                "txid": r.txid,
                "src_ip": r.src_ip,
                "dst_ip": r.dst_ip,
                "src_port": int(r.src_port),
                "dst_port": int(r.dst_port),
                "geo_country": r.geo_country,
                "ASN": r.ASN,
            }
        )

    schema = {
        "timestamp": pl.Utf8,
        "txid": pl.Utf8,
        "src_ip": pl.Utf8,
        "dst_ip": pl.Utf8,
        "src_port": pl.Int64,
        "dst_port": pl.Int64,
        "geo_country": pl.Utf8,
        "ASN": pl.Utf8,
    }
    return pl.DataFrame(rows, schema=schema)


def normalize_dataset(
    records: list[BitcoinTransactionRecord],
) -> dict[str, pl.DataFrame]:
    """
    Convert validated BitcoinTransactionRecords into normalized analytical Polars DataFrames:
    - transactions
    - wallets
    - network_observations
    """
    inputs = []
    outputs = []
    source_metadata: dict[str, tuple[str | None, str | None]] = {}
    distinct_ips: set[str] = set()
    for record in records:
        for address, amount in zip(
            record.input_addresses, record.input_amounts, strict=True
        ):
            inputs.append(
                {
                    "txid": record.txid,
                    "timestamp": record.timestamp,
                    "wallet_address": address,
                    "amount": amount,
                }
            )
        for address, amount in zip(
            record.output_addresses, record.output_amounts, strict=True
        ):
            outputs.append(
                {
                    "txid": record.txid,
                    "timestamp": record.timestamp,
                    "wallet_address": address,
                    "amount": amount,
                }
            )
        source_metadata[record.src_ip] = (record.geo_country, record.ASN)
        distinct_ips.update((record.src_ip, record.dst_ip))
    io_schema = {
        "txid": pl.Utf8,
        "timestamp": pl.Utf8,
        "wallet_address": pl.Utf8,
        "amount": pl.Float64,
    }
    rejected_schema = {
        "line": pl.Int64,
        "txid": pl.Utf8,
        "error": pl.Utf8,
        "source_file_name": pl.Utf8,
        "source_sha256": pl.Utf8,
    }
    with GeoIPResolver() as resolver:
        enriched = [
            resolver.lookup(ip, *source_metadata.get(ip, (None, None)))
            for ip in sorted(distinct_ips)
        ]
    enrichment_schema = {
        "ip": pl.Utf8,
        "country": pl.Utf8,
        "asn": pl.Utf8,
        "as_org": pl.Utf8,
        "source": pl.Utf8,
    }
    return {
        "transactions": normalize_transactions(records),
        "wallets": normalize_wallets(records),
        "network_observations": normalize_network_observations(records),
        "tx_inputs": pl.DataFrame(inputs, schema=io_schema),
        "tx_outputs": pl.DataFrame(outputs, schema=io_schema),
        "rejected": pl.DataFrame(schema=rejected_schema),
        "ip_enrichment": pl.DataFrame(enriched, schema=enrichment_schema),
    }
