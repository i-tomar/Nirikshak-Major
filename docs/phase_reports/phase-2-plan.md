# Phase 2 correlation plan

Branch: `phase/2-correlation` from clean Phase 1 `main`.

1. Inspect normalized transaction, wallet and network tables and graph/API contracts. Keep existing tests and routes working.
2. Add deterministic correlation rules in a bounded, vectorized pipeline: direct TXID matches, configurable as-of windows, shared IP/ASN inference and capped first-seen relay indicators. Store rule/version, window, timestamp, evidence type, confidence and caveat per link in `correlations.parquet`.
3. Build correlations during both vectorized upload and legacy normalization. Consume typed correlation edges in the graph. Add a wallet endpoint with bounded, parameterized queries and source labels.
4. Add hand-built fixtures for time boundaries, duplicate IPs, absent TXIDs and out-of-order observations. Assert rule provenance and confidence caps and positive wallet lookup.
5. Run focused tests, `\.\tasks.ps1 check`, Phase 2 gate, Docker health and tests. Record actual outputs and limits in `phase-2.md`. Check staged paths/sizes before each commit; merge and tag only when green, then push `main` and tags.
