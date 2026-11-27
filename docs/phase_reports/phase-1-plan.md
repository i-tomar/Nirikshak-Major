# Phase 1 data layer plan

Branch: `phase/1-data-layer` from clean Phase 0 `main`.

1. Inspect current loader, normalizer, storage, upload, generator, task runner and Docker layout. Preserve existing API and verifier contracts.
2. Implement bounded streaming CSV, JSON array/NDJSON and defused XML parsing, consistent list aliases, row quarantine with SHA-256 and UTC timestamps. Add normalized input/output and IP enrichment tables.
3. Harden upload streaming with size and content checks, random server paths and stable redacted client errors. Add HTTP tests for unsafe names and content.
4. Add offline GeoIP unique-IP lookup with labelled synthetic fallback, preserving supplied metadata and testing real database path when a database is present.
5. Extend generator CLI, formats and profiles with deterministic outputs and backend-only labels. Add cross-format and adversarial parser tests.
6. Add a benchmark target and run 100K and 1M ingestion on Windows and Docker for CSV, JSON and XML where resources allow. Record actual wall time and process peak RAM. Do not claim a pass where unverified.
7. Run import, pytest, legacy verifiers, Ruff, mypy, Bandit, dependency audits, frontend lint/build, Docker pytest and the Phase 1 gate. Update DECISIONS, BLOCKERS and phase-1 report with measured evidence. Merge and tag only if green; stop after Phase 1.

Safety: stage explicit paths only; before every commit print `git status --short`, inspect staged names and sizes, and exclude external data, caches, secrets, keys and files over 5 MB. Stop Docker containers after each check.
