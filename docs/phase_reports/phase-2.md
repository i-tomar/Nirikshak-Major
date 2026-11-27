# Phase 2 correlation report

27 November 2026 · Windows PowerShell and Docker · **GREEN**

## What was built

`backend/app/pipeline/correlation.py` joins wallet events with network observations by TXID, then uses a configurable as-of window for observations lacking TXIDs. It emits direct IP, contextual ASN, shared infrastructure and capped first-seen relay evidence into `correlations.parquet`. `backend/app/pipeline/{storage,streaming}.py` build the table for both legacy normalization and staged uploads. `backend/app/graph/builder.py` consumes typed wallet-network edges. `backend/app/routers/correlations.py` exposes bounded `GET /api/correlations/{wallet}` with rule version, timestamp, window, evidence type, confidence, caveat and source. Three new tests use out-of-order observations, a 600-second match, a 601-second miss, duplicate IP observations, missing TXIDs, malicious wallet input, and a real graph edge. No prior test was removed, skipped or weakened.

## Commands and actual outputs

`\.\tasks.ps1 check` exited **0** after the initial Ruff import-order and mypy test-value issues were corrected. Final output:

```text
Windows pytest: 78 passed, 1 warning in 81.71s
verify_phase1.py: PHASE 1 VERIFICATION SUCCESSFUL
verify_phase2.py: PHASE 2 IMPLEMENTATION & VERIFICATION COMPLETED SUCCESSFULLY
verify_phase3.py: PHASE 3 SUITE VERIFICATION SUCCESSFUL: All 8 Tests Passed
verify_phase4.py: PHASE 4 VERIFICATION SUITE SUCCESSFUL: ALL 8 TESTS PASSED
verify_phase5.py: PHASE 5 VERIFICATION COMPLETE: ALL 24 TESTS PASSED
ruff: All checks passed!
mypy: Success: no issues found in 41 source files
bandit: High 0, Medium 0, Low 0
pip-audit: No known vulnerabilities found
frontend lint: 0 errors, 2 existing warnings
frontend build: built in 17.62s
npm audit --omit=dev: found 0 vulnerabilities
Docker pytest: 78 passed, 1 warning in 58.85s
docker compose stop: backend and frontend Stopped
CHECK_EXIT=0
```

`docker compose up --build -d` showed `nirikshak_backend` healthy and the frontend up. `docker compose stop` stopped both; `docker compose ps --status running` showed only the header. `git ls-files backend/data/external` printed nothing. `git diff phase-1-done -- backend/tests` showed only the new Phase 2 test module.

## Measured gate and limits

The seeded 5,000-transaction fixture produced **100,310** correlation rows. Rebuilding them took **1.586 seconds** in a measured Windows Python process. Rules: 42,990 TXID joins, 28,660 shared IP, 14,330 shared ASN and 14,330 first-seen relay rows. The first sorted wallet's endpoint returned HTTP 200, total 7 links and 3 links with `limit=3`. Peak RAM for Phase 2 correlation alone was not measured. A 1M-row correlation build was not run; Phase 1's 1M-row benchmark predates this additional stage. Graph edges collapse multiple rules for a wallet-target pair, while Parquet and the API retain them.

## Security, decisions and Git state

Wallet inputs are bound SQL parameters; the limit and offset are bounded. A SQL-like wallet ID returned zero links. Bandit, pip-audit and npm production audit found no issue at their configured gates. Existing frontend lint and TestClient deprecation warnings remain non-failing. Confidence weights and the first-seen caveat are documented in `docs/DECISIONS.md`; they are not calibrated probabilities. At report commit time the branch is `phase/2-correlation` with plan `b1c5e39`, implementation `2e3b976` and gate fix `31f1db3`. The final merge, tag and push are recorded in Git after the report commit. No external data, MMDB, cache, secret, key or file over 5 MiB was staged.
