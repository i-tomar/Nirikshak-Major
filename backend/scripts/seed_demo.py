"""Generate the canonical synthetic fixture and exercise the normal ingest pipeline."""

import sys
from datetime import UTC, datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.graph.builder import build_investigation_graph
from app.ml.analyzer import run_full_analysis
from app.pipeline.loader import load_transactions
from app.pipeline.normalizer import normalize_dataset
from app.pipeline.storage import save_normalized_tables
from scripts.generate_dataset import SyntheticBitcoinGenerator, export_dataset


def main() -> None:
    output = BACKEND / "data"
    generator = SyntheticBitcoinGenerator(
        num_tx=5000,
        num_wallets=1200,
        num_ips=350,
        anomaly_pct=5.0,
        days=7,
        start_time=datetime(2025, 1, 1, 16, 40, tzinfo=UTC),
        seed=42,
    )
    transactions, labels = generator.generate()
    csv_path, _, _ = export_dataset(transactions, labels, output)
    records, rejected = load_transactions(csv_path)
    if rejected or len(records) != len(transactions):
        raise ValueError("The generated fixture failed validation")
    save_normalized_tables(normalize_dataset(records))
    summary = run_full_analysis()
    _, graph = build_investigation_graph(force_rebuild=True)
    print(
        f"synthetic: {len(records)} transactions, {summary.wallets_analyzed} wallets, "
        f"{graph['total_nodes']} graph nodes"
    )


if __name__ == "__main__":
    main()
