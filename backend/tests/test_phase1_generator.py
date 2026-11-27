"""Deterministic profile and format tests for the Phase 1 generator."""

from collections import Counter
from hashlib import sha256

from app.main import app
from app.pipeline.loader import load_transactions
from fastapi.testclient import TestClient
from scripts.generate_dataset import SyntheticBitcoinGenerator, export_dataset


def test_profile_outputs_are_deterministic_and_sufficiently_sparse(tmp_path):
    outputs = []
    for subdir in ("first", "second"):
        generator = SyntheticBitcoinGenerator(num_tx=1000, seed=7, profile="sparse")
        records, truth = generator.generate()
        export_dataset(records, truth, tmp_path / subdir, "all")
        paths = [
            tmp_path / subdir / f"demo_transactions.{suffix}"
            for suffix in ("csv", "json", "xml")
        ]
        paths.append(tmp_path / subdir / "ground_truth.json")
        outputs.append([sha256(path.read_bytes()).hexdigest() for path in paths])
        counts = Counter(
            address
            for tx in records
            for address in set(tx["input_addresses"] + tx["output_addresses"])
        )
        ratio = sum(value <= 2 for value in counts.values()) / len(counts)
        assert 0.70 <= ratio <= 0.80
        for path in paths[:3]:
            parsed, rejected = load_transactions(path)
            assert len(parsed) == len(records)
            assert not rejected
    assert outputs[0] == outputs[1]


def test_adversarial_profile_has_mixing_collection_and_decoys():
    generator = SyntheticBitcoinGenerator(num_tx=1000, seed=9, profile="adversarial")
    records, truth = generator.generate()
    kinds = {
        value["anomaly_type"]
        for value in truth["transactions"].values()
        if value["anomaly_type"]
    }
    assert {
        "coinjoin_like",
        "ransomware_collection",
        "ransomware_consolidation",
    } <= kinds
    assert any(
        len(tx["input_addresses"]) >= 3 and len(set(tx["output_amounts"])) == 1
        for tx in records
    )
    assert any(len(tx["output_addresses"]) >= 3 for tx in records)


def test_ground_truth_file_is_not_served():
    with TestClient(app) as client:
        for path in (
            "/ground_truth.json",
            "/data/ground_truth.json",
            "/api/datasets/ground_truth.json",
        ):
            assert client.get(path).status_code == 404
