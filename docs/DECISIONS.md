# Decisions

Phase 0 starts from the existing origin/main license and the local source baseline. Phase changes remain local until gates pass.

The original synthetic fixture is unavailable. Its generator uses the UTC hour to decide which random draws to consume. We selected a fixed compatible start, 2025-01-01 16:40 UTC, with the original CLI parameters and seed 42. The unmodified generator produced 5,000 transactions, 4,915 wallets and the existing investigation fixture address. This reconstructs the tested counts and address. The original file hash is unknown. No generated row or expected count was edited.

The initial anomaly model reloads from hash-checked numeric Parquet training inputs, pinned library versions and a saved random seed. This trades reload time for safe deserialization. The alert API keeps the historical risk scoring contract. Wallet clustering is behavioral similarity. Entity inference is scheduled for Phase 3.

BABD-13 dropped (file too large for the dev machine); real-data track uses Elliptic and BitcoinHeist.
