"""Bounded, vectorized ingestion from source files to normalized Parquet tables."""

import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TypedDict

import duckdb
import pyarrow as pa  # type: ignore[import-untyped]  # PyArrow has no bundled typing marker.
import pyarrow.parquet as pq  # type: ignore[import-untyped]  # PyArrow has no bundled typing marker.
from app.pipeline.geoip import GeoIPResolver
from app.pipeline.loader import MAX_FIELD_LENGTH, MAX_NESTING_DEPTH, _bounded
from app.pipeline.storage import get_parquet_paths
from defusedxml.ElementTree import iterparse  # type: ignore[import-untyped]  # defusedxml lacks a typing marker.

READ_BYTES = 1024 * 1024


class IngestResult(TypedDict):
    total_rows: int
    valid_rows: int
    rejected_rows: int
    source_sha256: str
    storage_dir: str
    geoip_sources: dict[str, int]


def source_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while block := stream.read(READ_BYTES):
            digest.update(block)
    return digest.hexdigest()


def json_array_to_ndjson(source: Path, destination: Path) -> None:
    """Copy raw JSON objects out of an array or transactions wrapper without decoding rows."""
    in_string = False
    escaped = False
    array_found = False
    depth = 0
    current = bytearray()
    with source.open("rb") as stream, destination.open("wb") as output:
        while block := stream.read(READ_BYTES):
            for byte in block:
                if not array_found:
                    if byte == 34 and not escaped:
                        in_string = not in_string
                    if byte == 91 and not in_string:
                        array_found = True
                    escaped = byte == 92 and not escaped if in_string else False
                    continue
                if depth == 0 and byte == 93:
                    if not output.tell():
                        raise ValueError("JSON transaction array is empty")
                    return
                if depth == 0 and byte in (9, 10, 13, 32, 44):
                    continue
                if depth == 0 and byte != 123:
                    raise ValueError("JSON array must contain objects")
                if not in_string and byte in (9, 10, 13, 32):
                    continue
                current.append(byte)
                if len(current) > MAX_FIELD_LENGTH * 64:
                    raise ValueError("JSON record size limit exceeded")
                if in_string:
                    if escaped:
                        escaped = False
                    elif byte == 92:
                        escaped = True
                    elif byte == 34:
                        in_string = False
                elif byte == 34:
                    in_string = True
                elif byte in (123, 91):
                    depth += 1
                    if depth > MAX_NESTING_DEPTH:
                        raise ValueError("JSON nesting limit exceeded")
                elif byte in (125, 93):
                    depth -= 1
                    if depth < 0:
                        raise ValueError("Invalid JSON nesting")
                    if depth == 0:
                        output.write(current)
                        output.write(b"\n")
                        current.clear()
        raise ValueError("Incomplete JSON transaction array")


def xml_to_ndjson(source: Path, destination: Path) -> None:
    """Stream XML records with defusedxml and bounded element depth and values."""
    list_names = {
        "input_addresses",
        "output_addresses",
        "input_amounts",
        "output_amounts",
    }
    depth = 0
    count = 0
    with source.open("rb") as stream, destination.open("w", encoding="utf-8") as output:
        for event, element in iterparse(stream, events=("start", "end")):
            if event == "start":
                depth += 1
                if depth > MAX_NESTING_DEPTH:
                    raise ValueError("XML nesting limit exceeded")
                for attribute in element.attrib.values():
                    _bounded(attribute)
                continue
            if element.tag in {"transaction", "record"}:
                row: dict[str, object] = {}
                for child in element:
                    if child.tag in list_names:
                        value: object = [part.text or "" for part in child] if len(child) else [child.text or ""]
                        if child.tag in row:
                            previous = row[child.tag]
                            if isinstance(previous, list) and isinstance(value, list):
                                value = [*previous, *value]
                    else:
                        value = child.text or ""
                    _bounded(value)
                    row[child.tag] = value
                output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
                output.write("\n")
                element.clear()
                count += 1
            depth -= 1
    if count == 0:
        raise ValueError("XML contains no transactions")


def _copy(
    connection: duckdb.DuckDBPyConnection,
    query: str,
    destination: Path,
    values: list[object] | None = None,
) -> None:
    connection.execute(
        f"COPY ({query}) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
        [*(values or []), str(destination)],
    )


def _write_ip_enrichment(
    connection: duckdb.DuckDBPyConnection, destination: Path
) -> dict[str, int]:
    """Resolve each distinct source or destination IP once and stream Parquet batches."""
    schema = pa.schema(
        [(name, pa.string()) for name in ("ip", "country", "asn", "as_org", "source")]
    )
    counts: dict[str, int] = {}
    connection.execute("""
        SELECT ip, max(country) AS country, max(asn) AS asn FROM (
          SELECT src_ip AS ip, geo_country AS country, ASN AS asn FROM valid
          UNION ALL SELECT dst_ip AS ip, NULL AS country, NULL AS asn FROM valid
        ) GROUP BY ip ORDER BY ip
    """)
    with (
        GeoIPResolver() as resolver,
        pq.ParquetWriter(destination, schema=schema, compression="zstd") as writer,
    ):
        while rows := connection.fetchmany(10_000):
            enriched = [
                resolver.lookup(str(ip), country, asn) for ip, country, asn in rows
            ]
            for row in enriched:
                source = str(row["source"])
                counts[source] = counts.get(source, 0) + 1
            writer.write_table(pa.Table.from_pylist(enriched, schema=schema))
    return counts


def ingest_file(
    source: str | Path,
    storage_dir: str | Path | None = None,
    source_name: str | None = None,
) -> IngestResult:
    """Ingest CSV, JSON array/wrapper, NDJSON or XML with bounded Python memory."""
    path = Path(source)
    suffix = path.suffix.lower()
    if suffix not in {".csv", ".json", ".ndjson", ".xml"}:
        raise ValueError("Unsupported dataset format")
    digest = source_digest(path)
    target_paths = get_parquet_paths(storage_dir)
    with TemporaryDirectory(dir=target_paths["transactions"].parent) as temporary:
        staging = Path(temporary)
        paths = get_parquet_paths(staging / "normalized")
        scan_path = path
        if suffix == ".json":
            scan_path = staging / "records.ndjson"
            json_array_to_ndjson(path, scan_path)
        elif suffix == ".xml":
            scan_path = staging / "records.ndjson"
            xml_to_ndjson(path, scan_path)
        connection = duckdb.connect()
        connection.execute("SET TimeZone='UTC'")
        connection.execute("SET temp_directory = ?", [str(staging)])
        if suffix == ".csv":
            connection.execute(
                "CREATE TEMP TABLE raw AS SELECT row_number() OVER () AS source_row, * FROM read_csv(?, all_varchar=true, header=true, max_line_size=4194304)",
                [str(scan_path)],
            )
        else:
            connection.execute(
                "CREATE TEMP TABLE raw AS SELECT row_number() OVER () AS source_row, * FROM read_json(?, format='newline_delimited', maximum_object_size=4194304, maximum_depth=16)",
                [str(scan_path)],
            )
        names = {
            row[0].lower() for row in connection.execute("DESCRIBE raw").fetchall()
        }
        required = {
            "timestamp",
            "src_ip",
            "dst_ip",
            "txid",
            "input_addresses",
            "output_addresses",
            "input_amounts",
            "output_amounts",
        }
        if not required <= names:
            raise ValueError("Dataset is missing required columns")
        optional = {
            "src_port": 'ALTER TABLE raw ADD COLUMN src_port VARCHAR',
            "dst_port": 'ALTER TABLE raw ADD COLUMN dst_port VARCHAR',
            "fee": 'ALTER TABLE raw ADD COLUMN fee VARCHAR',
            "fee_btc": 'ALTER TABLE raw ADD COLUMN fee_btc VARCHAR',
            "script_type": 'ALTER TABLE raw ADD COLUMN script_type VARCHAR',
            "geo_country": 'ALTER TABLE raw ADD COLUMN geo_country VARCHAR',
            "asn": 'ALTER TABLE raw ADD COLUMN ASN VARCHAR',
        }
        for name, statement in optional.items():
            if name not in names:
                connection.execute(statement)
        connection.execute("""
            CREATE TEMP TABLE parsed AS SELECT source_row,
              lower(trim(cast(txid AS VARCHAR))) AS txid,
              try_cast(timestamp AS TIMESTAMPTZ) AS timestamp_utc,
              trim(cast(src_ip AS VARCHAR)) AS src_ip,
              trim(cast(dst_ip AS VARCHAR)) AS dst_ip,
              coalesce(try_cast(src_port AS INTEGER), 0) AS src_port,
              coalesce(try_cast(dst_port AS INTEGER), 8333) AS dst_port,
              coalesce(try_cast(input_addresses AS VARCHAR[]),
                string_split(replace(replace(trim(cast(input_addresses AS VARCHAR)), ';', ','), '|', ','), ',')) AS input_addresses,
              coalesce(try_cast(output_addresses AS VARCHAR[]),
                string_split(replace(replace(trim(cast(output_addresses AS VARCHAR)), ';', ','), '|', ','), ',')) AS output_addresses,
              coalesce(try_cast(input_amounts AS DOUBLE[]),
                list_transform(string_split(replace(replace(trim(cast(input_amounts AS VARCHAR)), ';', ','), '|', ','), ','), lambda x: try_cast(x AS DOUBLE))) AS input_amounts,
              coalesce(try_cast(output_amounts AS DOUBLE[]),
                list_transform(string_split(replace(replace(trim(cast(output_amounts AS VARCHAR)), ';', ','), '|', ','), ','), lambda x: try_cast(x AS DOUBLE))) AS output_amounts,
              coalesce(try_cast(fee_btc AS DOUBLE), try_cast(fee AS DOUBLE), 0.0) AS fee,
              coalesce(cast(script_type AS VARCHAR), 'P2WPKH') AS script_type,
              cast(geo_country AS VARCHAR) AS geo_country,
              cast(ASN AS VARCHAR) AS ASN
            FROM raw
        """)
        connection.execute("""
            CREATE TEMP TABLE checked AS SELECT *, CASE
              WHEN len(src_ip)>65536 OR len(dst_ip)>65536 OR len(script_type)>65536 THEN 'Field length limit exceeded'
              WHEN len(input_addresses)>1024 OR len(output_addresses)>1024 OR len(input_amounts)>1024 OR len(output_amounts)>1024 THEN 'List size limit exceeded'
              WHEN len(list_filter(input_addresses, lambda x: len(x)>65536))>0 OR len(list_filter(output_addresses, lambda x: len(x)>65536))>0 THEN 'Field length limit exceeded'
              WHEN NOT regexp_full_match(txid, '[0-9a-f]{64}') THEN 'Invalid txid'
              WHEN timestamp_utc IS NULL THEN 'Invalid timestamp'
              WHEN src_ip IS NULL OR dst_ip IS NULL OR src_ip='' OR dst_ip='' THEN 'Missing IP'
              WHEN src_port NOT BETWEEN 1 AND 65535 OR dst_port NOT BETWEEN 1 AND 65535 THEN 'Invalid port'
              WHEN script_type NOT IN ('P2PKH','P2SH','P2WPKH','P2WSH','P2TR') THEN 'Invalid script type'
              WHEN fee IS NULL OR fee < 0 THEN 'Invalid fee'
              WHEN len(input_addresses)=0 OR len(output_addresses)=0 THEN 'Empty address list'
              WHEN len(input_addresses)<>len(input_amounts) OR len(output_addresses)<>len(output_amounts) THEN 'Mismatched list lengths'
              WHEN len(list_filter(input_amounts, lambda x: x IS NULL))>0 OR len(list_filter(output_amounts, lambda x: x IS NULL))>0 THEN 'Invalid amount'
              WHEN list_sum(output_amounts)>list_sum(input_amounts) THEN 'Outputs exceed inputs'
              ELSE NULL END AS validation_error
            FROM parsed
        """)
        connection.execute(
            "CREATE TEMP VIEW valid AS SELECT * FROM checked WHERE validation_error IS NULL"
        )
        _copy(
            connection,
            """SELECT txid, strftime(timestamp_utc,'%Y-%m-%dT%H:%M:%S.%fZ') AS timestamp,
          fee, script_type, input_addresses, output_addresses, input_amounts, output_amounts,
          round(list_sum(input_amounts),8) AS total_input_amount,
          round(list_sum(output_amounts),8) AS total_output_amount,
          len(input_addresses) AS input_count, len(output_addresses) AS output_count,
          src_ip,dst_ip,src_port,dst_port,geo_country,ASN FROM valid""",
            paths["transactions"],
        )
        _copy(
            connection,
            """SELECT strftime(timestamp_utc,'%Y-%m-%dT%H:%M:%S.%fZ') AS timestamp,
          txid,src_ip,dst_ip,src_port,dst_port,geo_country,ASN FROM valid""",
            paths["network_observations"],
        )
        connection.execute(
            "CREATE TEMP VIEW tx_inputs AS SELECT txid, strftime(timestamp_utc,'%Y-%m-%dT%H:%M:%S.%fZ') AS timestamp, unnest(input_addresses) AS wallet_address, unnest(input_amounts) AS amount FROM valid"
        )
        connection.execute(
            "CREATE TEMP VIEW tx_outputs AS SELECT txid, strftime(timestamp_utc,'%Y-%m-%dT%H:%M:%S.%fZ') AS timestamp, unnest(output_addresses) AS wallet_address, unnest(output_amounts) AS amount FROM valid"
        )
        _copy(connection, "SELECT * FROM tx_inputs", paths["tx_inputs"])
        _copy(connection, "SELECT * FROM tx_outputs", paths["tx_outputs"])
        _copy(
            connection,
            """WITH movements AS (
          SELECT wallet_address,txid,timestamp,amount,'input' AS direction FROM tx_inputs
          UNION ALL SELECT wallet_address,txid,timestamp,amount,'output' FROM tx_outputs)
          SELECT wallet_address, count(DISTINCT txid) AS transaction_count,
          count(DISTINCT CASE WHEN direction='input' THEN txid END) AS input_transaction_count,
          count(DISTINCT CASE WHEN direction='output' THEN txid END) AS output_transaction_count,
          round(sum(CASE WHEN direction='input' THEN amount ELSE 0 END),8) AS total_input_amount,
          round(sum(CASE WHEN direction='output' THEN amount ELSE 0 END),8) AS total_output_amount,
          min(timestamp) AS first_seen,max(timestamp) AS last_seen
          FROM movements GROUP BY wallet_address""",
            paths["wallets"],
        )
        _copy(
            connection,
            """SELECT source_row + ? AS line, txid, validation_error AS error,
          ? AS source_file_name, ? AS source_sha256 FROM checked WHERE validation_error IS NOT NULL""",
            paths["rejected"],
            [1 if suffix == ".csv" else 0, source_name or path.name, digest],
        )
        geoip_sources = _write_ip_enrichment(connection, paths["ip_enrichment"])
        counts = connection.execute(
            "SELECT count(*), count(*) FILTER (WHERE validation_error IS NULL) FROM checked"
        ).fetchone()
        if counts is None:
            raise RuntimeError("Ingestion count unavailable")
        connection.close()
        selected = paths if int(counts[1]) > 0 else {"rejected": paths["rejected"]}
        for name, staged_path in selected.items():
            staged_path.replace(target_paths[name])
        return {
            "total_rows": int(counts[0]),
            "valid_rows": int(counts[1]),
            "rejected_rows": int(counts[0]) - int(counts[1]),
            "source_sha256": digest,
            "storage_dir": str(target_paths["transactions"].parent),
            "geoip_sources": geoip_sources,
        }
