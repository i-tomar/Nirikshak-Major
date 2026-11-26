# Decisions

<<<<<<< HEAD
Phase 0 starts from the existing origin/main license and the local source baseline. Phase changes remain local until gates pass.

The original synthetic fixture is unavailable. Its generator uses the UTC hour to decide which random draws to consume. We selected a fixed compatible start, 2025-01-01 16:40 UTC, with the original CLI parameters and seed 42. The unmodified generator produced 5,000 transactions, 4,915 wallets and the existing investigation fixture address. This reconstructs the tested counts and address. The original file hash is unknown. No generated row or expected count was edited.

The initial anomaly model reloads from hash-checked numeric Parquet training inputs, pinned library versions and a saved random seed. This trades reload time for safe deserialization. The alert API keeps the historical risk scoring contract. Wallet clustering is behavioral similarity. Entity inference is scheduled for Phase 3.

=======
>>>>>>> main
BABD-13 dropped (file too large for the dev machine); real-data track uses Elliptic and BitcoinHeist.

Both baseline 0d06e64 and 32ebd44 generated the same CSV, SHA-256 be9448ac22895089f0274ded4dc9b63100db0e4b17ac688faf5f7981a85ca937. With 5,000 transactions, 4,915 wallets, 5,000 observations and zero rejected rows on both, independent Decimal summation and DuckDB each gave 5216.56493532 BTC on both revisions. The baseline package initializer was bypassed in the scratch worktree because it imports the missing ML module. The actual generator, schema, loader, normalizer and storage were unchanged. The legacy fixture was unavailable. Phase 3 verification now derives expected volume and timestamp boundaries directly from source CSV and retains the original precision and table-count checks. Phase 5 inherits this correction through its regression runner.

API failure tests cover server-side correlation IDs, sensitive detail redaction, configured CORS and default-disabled documentation. Alert literal-input tests cover punctuation, Unicode and length without requiring application data mutations.
