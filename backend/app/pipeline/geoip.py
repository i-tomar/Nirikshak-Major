"""Offline IP enrichment with explicit provenance and a synthetic CIDR fallback."""

import csv
import gzip
import ipaddress
import logging
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Self

import maxminddb

LOGGER = logging.getLogger(__name__)
GEOIP_DIR = Path(__file__).resolve().parents[2] / "data" / "geoip"
FALLBACK = Path(__file__).with_name("geoip_fallback.csv")


class GeoIPResolver:
    """Open database readers once, then resolve only distinct IPs."""

    def __init__(self, geoip_dir: Path = GEOIP_DIR, fallback: Path = FALLBACK):
        self._temporary = TemporaryDirectory()
        self._readers: dict[str, Any] = {}
        self.fallback: list[
            tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, str, str, str]
        ] = []
        with fallback.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                self.fallback.append(
                    (
                        ipaddress.ip_network(row["cidr"]),
                        row["country"],
                        row["asn"],
                        row["as_org"],
                    )
                )
        candidates = {
            "city": ("GeoLite2-City.mmdb", "dbip-city-lite-*.mmdb*"),
            "asn": ("GeoLite2-ASN.mmdb", "dbip-asn-lite-*.mmdb*"),
        }
        for kind, (geolite_name, dbip_pattern) in candidates.items():
            for source in (
                geoip_dir / geolite_name,
                *sorted(geoip_dir.glob(dbip_pattern), reverse=True),
            ):
                if not source.is_file():
                    continue
                target = source
                if source.suffix == ".gz":
                    target = Path(self._temporary.name) / source.stem
                    with (
                        gzip.open(source, "rb") as input_stream,
                        target.open("wb") as output_stream,
                    ):
                        shutil.copyfileobj(
                            input_stream, output_stream, length=1024 * 1024
                        )
                self._readers[kind] = maxminddb.open_database(str(target))
                break
        LOGGER.info(
            "GeoIP source: %s", "offline_mmdb" if self._readers else "synthetic_lookup"
        )

    def close(self) -> None:
        for reader in self._readers.values():
            reader.close()
        self._temporary.cleanup()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def lookup(
        self,
        address: str,
        provided_country: str | None = None,
        provided_asn: str | None = None,
    ) -> dict[str, str | None]:
        """Prefer explicit source metadata, otherwise query an offline DB or fallback."""
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return {
                "ip": address,
                "country": None,
                "asn": None,
                "as_org": None,
                "source": "invalid_ip",
            }
        if provided_country and provided_asn:
            return {
                "ip": address,
                "country": provided_country,
                "asn": provided_asn,
                "as_org": None,
                "source": "provided",
            }
        country: str | None = None
        asn: str | None = None
        org: str | None = None
        source = "offline_mmdb" if self._readers else "synthetic_lookup"
        if self._readers:
            city = (
                self._readers["city"].get(address) if "city" in self._readers else None
            )
            as_data = (
                self._readers["asn"].get(address) if "asn" in self._readers else None
            )
            country = (city or {}).get("country", {}).get("iso_code")
            number = (as_data or {}).get("autonomous_system_number")
            asn = f"AS{number}" if number else None
            org = (as_data or {}).get("autonomous_system_organization")
        else:
            for network, fallback_country, fallback_asn, fallback_org in self.fallback:
                if ip in network:
                    country, asn, org = fallback_country, fallback_asn, fallback_org
                    break
        return {
            "ip": address,
            "country": provided_country or country,
            "asn": provided_asn or asn,
            "as_org": org,
            "source": "provided_plus_" + source
            if provided_country or provided_asn
            else source,
        }
