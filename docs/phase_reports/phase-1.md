# Phase 1 data layer report

27 November 2026 · Windows PowerShell and Docker · **GREEN**

## What was built

- `backend/app/pipeline/streaming.py` ingests CSV, JSON arrays, NDJSON and XML through bounded scans/conversion and DuckDB, writes versioned normalized Parquet tables and quarantines invalid rows with source SHA-256. It stages outputs on the destination volume and preserves active tables after an all-rejected upload.
- `backend/app/pipeline/geoip.py` and `geoip_fallback.csv` resolve unique IPs through local GeoLite2 or DB-IP Lite files, supplied metadata, or an explicitly labelled synthetic CIDR fallback. No network lookup is used.
- `backend/app/routers/datasets.py` streams upload chunks to random server paths, enforces the configured 500 MiB default, checks type/content and archive signatures throughout the stream, and gives redacted 4xx errors.
- `backend/scripts/generate_dataset.py` adds deterministic normal, sparse and adversarial profiles, CSV/JSON/XML output, CoinJoin-like and ransomware scenarios. Ground truth stays in backend-only data. `backend/scripts/benchmark_ingest.py` and `tasks.ps1 benchmark`/Makefile benchmark provide measurements.
- Five Phase 1 test modules cover equivalent tables, hostile XML, format and list limits, upload attacks, GeoIP source paths, generator determinism and all-rejected upload preservation. The single Phase 0 fixture adjustment and reason are recorded in `docs/DECISIONS.md`; no test was removed or skipped.

## Commands and actual outputs

The post-fix `\.\tasks.ps1 check` exited **0**. Its final output includes:

```text
backend import: succeeded
Windows pytest: 75 passed, 1 warning in 67.28s
verify_phase1.py: PHASE 1 VERIFICATION SUCCESSFUL
verify_phase2.py: IN-PROCESS TESTCLIENT SUITE: ALL TESTS PASSED
verify_phase3.py: PHASE 3 SUITE VERIFICATION SUCCESSFUL: All 8 Tests Passed
verify_phase4.py: PHASE 4 VERIFICATION SUITE SUCCESSFUL: ALL 8 TESTS PASSED
verify_phase5.py: PHASE 5 VERIFICATION COMPLETE: ALL 24 TESTS PASSED
ruff check: All checks passed!
mypy: Success: no issues found in 38 source files
bandit -r app: High: 0, Medium: 0, Low: 0
pip-audit: No known vulnerabilities found
frontend lint: 0 errors, 2 existing warnings
frontend build: built in 17.56s
npm audit --omit=dev --audit-level=high: found 0 vulnerabilities
Docker pytest: 75 passed, 1 warning in 71.92s
docker compose stop: backend and frontend Stopped
CHECK_EXIT=0
```

`docker compose up --build -d` followed by `docker compose ps` showed `nirikshak_backend ... Up ... (healthy)` and the frontend up. `docker compose stop` stopped both; `docker compose ps --status running` printed only its header. Verify Phase 2's optional live probe reported port 8000 unavailable during the check; its in-process suite passed. The previous Phase 0 live probe was run separately. `git diff main...HEAD -- backend/tests` showed five added test files and one adjusted fixture; no skip, xfail or removed test. `git ls-files backend/data/external` printed nothing.

## Measured metrics

The final-code `\.\tasks.ps1 benchmark` and six `docker compose run --rm backend python scripts/benchmark_ingest.py` runs ingested all requested rows with zero rejects. Times below are ingestion only; peak process memory includes sequential source generation and ingestion. Full source byte sizes, generation times and all twelve measurements are in `docs/benchmarks.md`.

| Runtime | Rows | CSV seconds / MiB | JSON seconds / MiB | XML seconds / MiB |
| --- | ---: | ---: | ---: | ---: |
| Windows | 100,000 | 7.398 / 324.9 | 25.163 / 318.7 | 25.881 / 323.9 |
| Windows | 1,000,000 | 5.810 / 1,925.3 | 192.351 / 1,914.2 | 178.274 / 2,054.6 |
| Docker, 12 GB limit | 100,000 | 5.235 / 543.7 | 6.971 / 649.4 | 9.880 / 571.7 |
| Docker, 12 GB limit | 1,000,000 | 8.615 / 2,252.7 | 43.415 / 2,377.4 | 40.249 / 2,205.1 |

## Limits, security and decisions

Five million rows were not run. Large uploads finish ingestion but defer graph and ML analysis with an explicit `PARTIAL` pipeline status. The Phase 0 list loader remains for legacy verifiers; HTTP uploads and the benchmark use the streaming path. The Windows JSON/XML final benchmark was slower than the earlier run; both measured sets were real, and `docs/benchmarks.md` records the final run. A literal archive signature anywhere in the upload stream is rejected, including a signature inside text data.

Defused XML tests reject DTD/entity attacks, oversized nodes and deep nesting. Upload tests reject traversal names, excessive size, mismatched types, archives, empty files and binary input without path or stack trace leakage. Bandit found no low, medium or high issues; both dependency audits found no vulnerabilities at their configured gates. The two existing frontend lint warnings and Starlette TestClient deprecation warning remain non-failing. `docs/DECISIONS.md` records narrow third-party typing exceptions, schema and timestamp choices, source precedence, and the staged-output bug fix. No user decision is needed for this phase.

## Git state

Phase branch `phase/1-data-layer` started from clean Phase 0 main (`0d5ed7f`) and contains plan `a901a48`, ingestion `7f504a1`, upload `745b58e`, generator `3f54372`, benchmark `d0699b9`, and stabilization `4cb050f`. The report and final merge/tag will be recorded by Git after this report is committed. No external dataset, MMDB, cache, secret, key or file over 5 MiB was staged.
