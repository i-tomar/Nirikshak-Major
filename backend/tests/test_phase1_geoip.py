"""Offline GeoIP database and labelled fallback paths."""

from pathlib import Path

from app.pipeline.geoip import GeoIPResolver


def test_fallback_and_supplied_metadata(tmp_path: Path):
    with GeoIPResolver(geoip_dir=tmp_path) as resolver:
        fallback = resolver.lookup("104.16.1.2")
        assert fallback["source"] == "synthetic_lookup"
        assert fallback["country"] == "US"
        assert fallback["asn"] == "AS13335"
        supplied = resolver.lookup("104.16.1.2", "CA", "AS123")
        assert supplied["source"] == "provided"
        assert supplied["country"] == "CA"
        assert supplied["asn"] == "AS123"
        assert resolver.lookup("not-an-ip")["source"] == "invalid_ip"
        private = resolver.lookup("10.1.2.3")
        assert private["source"] == "synthetic_lookup"
        assert private["country"] is None
        ipv6 = resolver.lookup("2001:db8::1")
        assert ipv6["source"] == "synthetic_lookup"
        assert ipv6["country"] is None


def test_offline_mmdb_lookup_path(monkeypatch, tmp_path: Path):
    (tmp_path / "GeoLite2-City.mmdb").write_bytes(b"fixture")
    (tmp_path / "GeoLite2-ASN.mmdb").write_bytes(b"fixture")

    class Reader:
        def __init__(self, name: str):
            self.name = name

        def get(self, _address: str):
            if "City" in self.name:
                return {"country": {"iso_code": "JP"}}
            return {
                "autonomous_system_number": 64501,
                "autonomous_system_organization": "Fixture network",
            }

        def close(self):
            pass

    monkeypatch.setattr(
        "app.pipeline.geoip.maxminddb.open_database", lambda name: Reader(name)
    )
    with GeoIPResolver(geoip_dir=tmp_path) as resolver:
        result = resolver.lookup("203.0.113.3")
    assert result == {
        "ip": "203.0.113.3",
        "country": "JP",
        "asn": "AS64501",
        "as_org": "Fixture network",
        "source": "offline_mmdb",
    }
