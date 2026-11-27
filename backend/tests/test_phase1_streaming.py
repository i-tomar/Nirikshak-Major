"""Vectorized ingestion equivalence and rejected-row provenance."""

import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

import polars as pl
from app.pipeline.storage import get_parquet_paths
from app.pipeline.streaming import ingest_file


def _record(txid: str, timestamp: str) -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "src_ip": "192.0.2.4",
        "dst_ip": "198.51.100.4",
        "src_port": 50000,
        "dst_port": 8333,
        "txid": txid,
        "input_addresses": ["wallet-in"],
        "output_addresses": ["wallet-out"],
        "input_amounts": [1.0],
        "output_amounts": [0.9],
        "fee": 0.1,
        "script_type": "P2WPKH",
        "geo_country": "US",
        "ASN": "AS64500",
    }


def _xml(records: list[dict[str, object]]) -> str:
    elements = []
    for row in records:
        fields = []
        for key, value in row.items():
            content = (
                "".join(f"<item>{escape(str(item))}</item>" for item in value)
                if isinstance(value, list)
                else escape(str(value))
            )
            fields.append(f"<{key}>{content}</{key}>")
        elements.append("<transaction>" + "".join(fields) + "</transaction>")
    return "<transactions>" + "".join(elements) + "</transactions>"


def test_streaming_formats_have_identical_tables(tmp_path: Path):
    records = [
        _record("a" * 64, "2025-01-01T01:00:00+01:00"),
        _record("b" * 64, "2025-01-01T00:00:00Z"),
    ]
    paths = {
        suffix: tmp_path / f"source.{suffix}"
        for suffix in ("csv", "json", "ndjson", "xml")
    }
    with paths["csv"].open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(
            {
                key: json.dumps(value) if isinstance(value, list) else value
                for key, value in row.items()
            }
            for row in records
        )
    paths["json"].write_text(json.dumps({"transactions": records}), encoding="utf-8")
    paths["ndjson"].write_text(
        "\n".join(json.dumps(row) for row in records), encoding="utf-8"
    )
    paths["xml"].write_text(_xml(records), encoding="utf-8")
    results = {}
    tables = {}
    for suffix, path in paths.items():
        destination = tmp_path / suffix
        results[suffix] = ingest_file(path, destination)
        tables[suffix] = {
            name: pl.read_parquet(table_path)
            for name, table_path in get_parquet_paths(destination).items()
        }
        assert results[suffix]["valid_rows"] == 2
        assert results[suffix]["rejected_rows"] == 0
    for name in tables["csv"]:
        if name == "rejected":
            continue
        baseline = tables["csv"][name].sort(tables["csv"][name].columns)
        for suffix in ("json", "ndjson", "xml"):
            assert baseline.equals(
                tables[suffix][name].sort(tables[suffix][name].columns)
            ), (name, suffix)
    assert tables["csv"]["transactions"]["timestamp"].unique().to_list() == [
        "2025-01-01T00:00:00.000000Z"
    ]


def test_rejected_rows_record_source_hash(tmp_path: Path):
    valid = _record("a" * 64, "2025-01-01T00:00:00Z")
    bad = _record("bad", "2025-01-01T00:00:00Z")
    source = tmp_path / "source.ndjson"
    source.write_text(
        "\n".join(json.dumps(row) for row in (valid, bad)), encoding="utf-8"
    )
    summary = ingest_file(source, tmp_path / "store")
    assert summary["valid_rows"] == 1
    assert summary["rejected_rows"] == 1
    rejected = pl.read_parquet(get_parquet_paths(tmp_path / "store")["rejected"])
    assert rejected["source_sha256"][0] == summary["source_sha256"]
    assert rejected["txid"][0] == "bad"
    assert rejected["source_file_name"][0] == source.name


def test_streaming_rejects_overlong_fields_and_lists(tmp_path: Path):
    long_field = {**_record("a" * 64, "2025-01-01T00:00:00Z"), "src_ip": "x" * 65_537}
    long_list = {**_record("b" * 64, "2025-01-01T00:00:00Z"), "input_addresses": ["wallet"] * 1025, "input_amounts": [1 / 1025] * 1025}
    source = tmp_path / "limits.ndjson"
    source.write_text("\n".join(json.dumps(row) for row in (long_field, long_list)), encoding="utf-8")
    result = ingest_file(source, tmp_path / "store")
    assert result["valid_rows"] == 0
    assert result["rejected_rows"] == 2
    errors = set(pl.read_parquet(get_parquet_paths(tmp_path / "store")["rejected"])["error"])
    assert errors == {"Field length limit exceeded", "List size limit exceeded"}
