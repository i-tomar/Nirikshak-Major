import csv
import io
import json
from pathlib import Path
from typing import Any

from app.schemas.transaction import (
    SCHEMA_VERSION,
    BitcoinTransactionRecord,
    DatasetSummary,
)
from defusedxml.ElementTree import iterparse  # type: ignore[import-untyped]  # defusedxml lacks a typing marker.
from pydantic import ValidationError

MAX_FIELD_LENGTH = 65_536
MAX_LIST_ITEMS = 1_024
MAX_NESTING_DEPTH = 16


def _bounded(value: Any, depth: int = 0) -> None:
    """Reject parser values that would expand memory or error responses excessively."""
    if depth > MAX_NESTING_DEPTH:
        raise ValueError("Record nesting limit exceeded")
    if isinstance(value, str) and len(value) > MAX_FIELD_LENGTH:
        raise ValueError("Field length limit exceeded")
    if isinstance(value, list):
        if len(value) > MAX_LIST_ITEMS:
            raise ValueError("List size limit exceeded")
        for item in value:
            _bounded(item, depth + 1)
    if isinstance(value, dict):
        if len(value) > MAX_LIST_ITEMS:
            raise ValueError("Object size limit exceeded")
        for item in value.values():
            _bounded(item, depth + 1)


def parse_list_field(value: Any, item_type: type = str) -> list[Any]:
    """Safely parse list fields from CSV (which may be JSON-encoded or already lists)."""
    _bounded(value)
    if isinstance(value, list):
        return [item_type(x) for x in value]
    if isinstance(value, str):
        v = value.strip()
        if (v.startswith("[") and v.endswith("]")) or (
            v.startswith("(") and v.endswith(")")
        ):
            try:
                parsed = json.loads(v)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, list):
                _bounded(parsed)
                return [item_type(x) for x in parsed]
        # Fallback: delimiter-separated (comma, semicolon, or pipe)
        for sep in [";", "|", ","]:
            if sep in v:
                parts = [x.strip() for x in v.split(sep) if x.strip()]
                _bounded(parts)
                return [item_type(x) for x in parts]
        if v:
            return [item_type(v)]
    return []


def parse_csv_content(
    content: str,
) -> tuple[list[BitcoinTransactionRecord], list[dict[str, Any]]]:
    """
    Parse and validate Bitcoin transaction records from CSV string content.
    Returns: (valid_records, rejected_records_info)
    """
    f = io.StringIO(content)
    reader = csv.DictReader(f)
    if not reader.fieldnames:
        return [], [
            {"line": 1, "txid": "none", "error": "Empty CSV or missing header row"}
        ]

    valid_records: list[BitcoinTransactionRecord] = []
    rejected_records: list[dict[str, Any]] = []

    for line_num, row in enumerate(reader, start=2):
        if not any(row.values()):
            continue
        try:
            _bounded(row)
            raw_record = {
                "timestamp": (row.get("timestamp") or "").strip(),
                "src_ip": (row.get("src_ip") or "").strip(),
                "dst_ip": (row.get("dst_ip") or "").strip(),
                "src_port": int(row.get("src_port") or 0),
                "dst_port": int(row.get("dst_port") or 8333),
                "txid": (row.get("txid") or "").strip(),
                "input_addresses": parse_list_field(
                    row.get("input_addresses", "[]"), str
                ),
                "output_addresses": parse_list_field(
                    row.get("output_addresses", "[]"), str
                ),
                "input_amounts": parse_list_field(
                    row.get("input_amounts", "[]"), float
                ),
                "output_amounts": parse_list_field(
                    row.get("output_amounts", "[]"), float
                ),
                "fee": float(row.get("fee_btc") or row.get("fee") or 0.0),
                "script_type": (row.get("script_type") or "P2WPKH").strip(),
                "geo_country": (row.get("geo_country") or "US").strip(),
                "ASN": str(
                    row.get("asn")
                    if row.get("asn") is not None and row.get("asn") != ""
                    else (row.get("ASN") or "")
                ).strip(),
            }
            record = BitcoinTransactionRecord.model_validate(raw_record)
            valid_records.append(record)
        except (ValidationError, ValueError, TypeError) as err:
            rejected_records.append(
                {
                    "line": line_num,
                    "txid": (row.get("txid") or f"unknown_line_{line_num}").strip()
                    if row
                    else f"line_{line_num}",
                    "error": str(err),
                }
            )

    return valid_records, rejected_records


def parse_json_content(
    content: str,
) -> tuple[list[BitcoinTransactionRecord], list[dict[str, Any]]]:
    """
    Parse and validate Bitcoin transaction records from JSON string content.
    Accepts either a JSON array of records or a dict with a 'transactions' key.
    """
    data = json.loads(content)
    raw_list = (
        data
        if isinstance(data, list)
        else data.get("transactions", [])
        if isinstance(data, dict)
        else None
    )
    if not isinstance(raw_list, list):
        raise TypeError(
            "JSON must contain an array of transaction records or an object with a 'transactions' key."
        )

    valid_records: list[BitcoinTransactionRecord] = []
    rejected_records: list[dict[str, Any]] = []

    for index, item in enumerate(raw_list):
        if not isinstance(item, dict):
            rejected_records.append(
                {
                    "index": index,
                    "txid": f"unknown_index_{index}",
                    "error": "Record is not a valid JSON object",
                }
            )
            continue
        try:
            _bounded(item)
            record = BitcoinTransactionRecord.model_validate(item)
            valid_records.append(record)
        except (ValidationError, ValueError, TypeError) as err:
            rejected_records.append(
                {
                    "index": index,
                    "txid": item.get("txid", f"unknown_index_{index}"),
                    "error": str(err),
                }
            )

    return valid_records, rejected_records


def parse_xml_content(
    content: str,
) -> tuple[list[BitcoinTransactionRecord], list[dict[str, Any]]]:
    """Parse transaction elements with defusedxml and bounded nesting/fields."""
    valid_records: list[BitcoinTransactionRecord] = []
    rejected_records: list[dict[str, Any]] = []
    list_names = {
        "input_addresses",
        "output_addresses",
        "input_amounts",
        "output_amounts",
    }
    depth = 0
    for event, elem in iterparse(io.StringIO(content), events=("start", "end")):
        if event == "start":
            depth += 1
            if depth > MAX_NESTING_DEPTH:
                raise ValueError("XML nesting limit exceeded")
            for value in elem.attrib.values():
                _bounded(value)
            continue
        if elem.tag in {"transaction", "record"}:
            row: dict[str, Any] = {}
            for child in elem:
                key = child.tag
                if key in list_names:
                    values = (
                        [part.text or "" for part in child]
                        if len(child)
                        else parse_list_field(child.text or "")
                    )
                    _bounded(values)
                    row[key] = [*row.get(key, []), *values]
                else:
                    value = child.text or ""
                    _bounded(value)
                    row[key] = value
            for key in ("input_amounts", "output_amounts"):
                row[key] = parse_list_field(row.get(key, []), float)
            for key in ("input_addresses", "output_addresses"):
                row[key] = parse_list_field(row.get(key, []), str)
            if "asn" in row and "ASN" not in row:
                row["ASN"] = row.pop("asn")
            if "fee_btc" in row and "fee" not in row:
                row["fee"] = row.pop("fee_btc")
            try:
                valid_records.append(BitcoinTransactionRecord.model_validate(row))
            except (ValidationError, ValueError, TypeError) as err:
                rejected_records.append(
                    {
                        "index": len(valid_records) + len(rejected_records),
                        "txid": row.get("txid"),
                        "error": type(err).__name__,
                    }
                )
            elem.clear()
        depth -= 1
    return valid_records, rejected_records


def load_transactions_from_csv(
    filepath: str | Path,
) -> tuple[list[BitcoinTransactionRecord], list[dict[str, Any]]]:
    """
    Load and validate Bitcoin transaction records from a CSV file.
    Returns: (valid_records, rejected_records_info)
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_csv_content(content)


def load_transactions_from_json(
    filepath: str | Path,
) -> tuple[list[BitcoinTransactionRecord], list[dict[str, Any]]]:
    """
    Load and validate Bitcoin transaction records from a JSON file.
    Accepts either a JSON array of records or a dict with a 'transactions' key.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_json_content(content)


def load_transactions(
    filepath: str | Path,
) -> tuple[list[BitcoinTransactionRecord], list[dict[str, Any]]]:
    """Generic dataset loader supporting both .csv and .json formats."""
    path = Path(filepath)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_transactions_from_csv(path)
    elif suffix == ".json":
        return load_transactions_from_json(path)
    elif suffix == ".xml":
        with open(path, encoding="utf-8") as stream:
            return parse_xml_content(stream.read())
    else:
        raise ValueError(
            f"Unsupported file format '{suffix}'. Supported: .csv, .json, .xml"
        )


def load_ground_truth(filepath: str | Path) -> dict[str, Any]:
    """Load hidden ground-truth file for offline model evaluation."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Ground truth file not found: {filepath}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_dataset_summary(
    records: list[BitcoinTransactionRecord],
) -> DatasetSummary:
    """Compute high-level summary metrics from a list of validated records."""
    if not records:
        return DatasetSummary(
            schema_version=SCHEMA_VERSION,
            total_transactions=0,
            unique_wallets=0,
            unique_ips=0,
            total_btc_volume=0.0,
            time_range_start="N/A",
            time_range_end="N/A",
        )

    wallets = set()
    ips = set()
    total_volume = 0.0
    timestamps = []

    for r in records:
        wallets.update(r.input_addresses)
        wallets.update(r.output_addresses)
        ips.add(r.src_ip)
        ips.add(r.dst_ip)
        total_volume += sum(r.output_amounts)
        timestamps.append(r.timestamp)

    timestamps.sort()

    return DatasetSummary(
        schema_version=SCHEMA_VERSION,
        total_transactions=len(records),
        unique_wallets=len(wallets),
        unique_ips=len(ips),
        total_btc_volume=round(total_volume, 8),
        time_range_start=timestamps[0],
        time_range_end=timestamps[-1],
    )
