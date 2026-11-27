"""Measure bounded Phase 1 ingestion without materializing source rows in Python."""

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.pipeline.streaming import ingest_file


def peak_ram_mib() -> float:
    """Read OS-reported peak resident memory for this Python process."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t)
                for name in (
                    "PeakWorkingSetSize",
                    "WorkingSetSize",
                    "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage",
                    "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage",
                    "PagefileUsage",
                    "PeakPagefileUsage",
                )
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(Counters)
        current_process = ctypes.windll.kernel32.GetCurrentProcess
        current_process.restype = wintypes.HANDLE
        process_memory = ctypes.windll.psapi.GetProcessMemoryInfo
        process_memory.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
            wintypes.DWORD,
        )
        process_memory.restype = wintypes.BOOL
        ok = process_memory(current_process(), ctypes.byref(counters), counters.cb)
        if not ok:
            raise OSError("Could not read Windows peak working set")
        return counters.PeakWorkingSetSize / (1024 * 1024)
    import importlib

    resource = importlib.import_module("resource")
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def row(index: int) -> dict[str, object]:
    txid = hashlib.sha256(str(index).encode()).hexdigest()
    return {
        "timestamp": (
            datetime(2025, 1, 1, tzinfo=UTC) + timedelta(seconds=index)
        ).isoformat(),
        "src_ip": f"192.0.2.{index % 250 + 1}",
        "dst_ip": "198.51.100.1",
        "src_port": 40000,
        "dst_port": 8333,
        "txid": txid,
        "input_addresses": [f"source-{index % 100_000}"],
        "output_addresses": [f"target-{index % 100_000}"],
        "input_amounts": [1.0],
        "output_amounts": [0.9999],
        "fee": 0.0001,
        "script_type": "P2WPKH",
        "geo_country": "ZZ",
        "ASN": "AS0",
    }


def write_source(path: Path, count: int, fmt: str) -> None:
    if fmt == "csv":
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row(0)))
            writer.writeheader()
            for index in range(count):
                writer.writerow(
                    {
                        key: json.dumps(value) if isinstance(value, list) else value
                        for key, value in row(index).items()
                    }
                )
    elif fmt == "json":
        with path.open("w", encoding="utf-8") as stream:
            stream.write('{"schema_version":"schema_v2","transactions":[')
            for index in range(count):
                if index:
                    stream.write(",")
                stream.write(json.dumps(row(index), separators=(",", ":")))
            stream.write("]}")
    else:
        with path.open("w", encoding="utf-8") as stream:
            stream.write("<transactions>")
            for index in range(count):
                stream.write("<transaction>")
                for key, value in row(index).items():
                    content = (
                        "".join(f"<item>{escape(str(item))}</item>" for item in value)
                        if isinstance(value, list)
                        else escape(str(value))
                    )
                    stream.write(f"<{key}>{content}</{key}>")
                stream.write("</transaction>")
            stream.write("</transactions>")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--format", choices=("csv", "json", "xml"), required=True)
    args = parser.parse_args()
    if args.rows < 1:
        parser.error("rows must be positive")
    with TemporaryDirectory(dir=BACKEND / "data") as temporary:
        source = Path(temporary) / f"benchmark.{args.format}"
        start = time.perf_counter()
        write_source(source, args.rows, args.format)
        generated_seconds = time.perf_counter() - start
        start = time.perf_counter()
        summary = ingest_file(source, Path(temporary) / "normalized")
        ingest_seconds = time.perf_counter() - start
        if summary["valid_rows"] != args.rows or summary["rejected_rows"] != 0:
            raise RuntimeError(f"Unexpected ingestion counts: {summary}")
        print(
            json.dumps(
                {
                    "format": args.format,
                    "rows": args.rows,
                    "source_bytes": source.stat().st_size,
                    "generation_seconds": round(generated_seconds, 3),
                    "ingest_seconds": round(ingest_seconds, 3),
                    "peak_python_process_ram_mib": round(peak_ram_mib(), 1),
                    "valid_rows": summary["valid_rows"],
                    "rejected_rows": summary["rejected_rows"],
                    "geoip_sources": summary["geoip_sources"],
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
