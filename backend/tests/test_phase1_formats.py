"""Phase 1 equivalent-format and hostile XML regression tests."""

import csv
import io
import json
from xml.sax.saxutils import escape

import pytest
from app.pipeline.loader import parse_csv_content, parse_json_content, parse_xml_content
from app.pipeline.normalizer import normalize_dataset
from app.schemas.transaction import SCHEMA_VERSION, BitcoinTransactionRecord
from defusedxml.common import DefusedXmlException  # type: ignore[import-untyped]  # defusedxml lacks a typing marker.


def _sample() -> dict[str, object]:
    return {
        "timestamp": "2025-01-01T00:00:00Z",
        "src_ip": "192.0.2.1",
        "dst_ip": "192.0.2.2",
        "src_port": 8333,
        "dst_port": 8333,
        "txid": "a" * 64,
        "input_addresses": ["wallet-in"],
        "output_addresses": ["wallet-out"],
        "input_amounts": [1.0],
        "output_amounts": [0.9],
        "fee": 0.1,
        "script_type": "P2WPKH",
        "geo_country": "US",
        "ASN": "AS64500",
    }


def test_equivalent_csv_json_xml_normalize_identically():
    row = _sample()
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(row))
    writer.writeheader()
    writer.writerow(
        {
            key: json.dumps(value) if isinstance(value, list) else value
            for key, value in row.items()
        }
    )
    csv_records, csv_rejected = parse_csv_content(stream.getvalue())
    json_records, json_rejected = parse_json_content(json.dumps([row]))
    xml_fields = "".join(
        f"<{key}>"
        + (
            "".join(f"<item>{escape(str(item))}</item>" for item in value)
            if isinstance(value, list)
            else escape(str(value))
        )
        + f"</{key}>"
        for key, value in row.items()
    )
    xml_records, xml_rejected = parse_xml_content(
        f"<transactions><transaction>{xml_fields}</transaction></transactions>"
    )
    assert not (csv_rejected or json_rejected or xml_rejected)
    tables = [
        normalize_dataset(records)
        for records in (csv_records, json_records, xml_records)
    ]
    for name in tables[0]:
        assert tables[0][name].equals(tables[1][name])
        assert tables[1][name].equals(tables[2][name])


def test_schema_v2_accepts_five_script_types():
    assert SCHEMA_VERSION == "schema_v2"
    for script_type in ("P2PKH", "P2SH", "P2WPKH", "P2WSH", "P2TR"):
        assert (
            BitcoinTransactionRecord.model_validate(
                {**_sample(), "script_type": script_type}
            ).script_type
            == script_type
        )
    with pytest.raises(ValueError):
        BitcoinTransactionRecord.model_validate({**_sample(), "script_type": "unknown"})


def test_repeated_xml_list_elements():
    row = _sample()
    row["input_addresses"] = ["wallet-in", "wallet-in-2"]
    row["input_amounts"] = [0.6, 0.4]
    fields = "".join(
        "".join(f"<{key}>{escape(str(item))}</{key}>" for item in value)
        if isinstance(value, list) else f"<{key}>{escape(str(value))}</{key}>"
        for key, value in row.items()
    )
    parsed, rejected = parse_xml_content(f"<transactions><transaction>{fields}</transaction></transactions>")
    assert not rejected
    assert parsed[0].input_addresses == ["wallet-in", "wallet-in-2"]
    assert parsed[0].output_amounts == [0.9]


@pytest.mark.parametrize(
    "xml",
    [
        '<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><transactions><transaction>&e;</transaction></transactions>',
        '<!DOCTYPE x [<!ENTITY a "123"><!ENTITY b "&a;&a;&a;">]><transactions><transaction>&b;</transaction></transactions>',
        '<transactions><transaction huge="' + "x" * 65_537 + '"/></transactions>',
        "<x>" * 17 + "</x>" * 17,
        "<transactions><transaction><txid>"
        + "x" * 65_537
        + "</txid></transaction></transactions>",
    ],
)
def test_hostile_xml_is_rejected(xml):
    with pytest.raises((ValueError, DefusedXmlException)):
        parse_xml_content(xml)
