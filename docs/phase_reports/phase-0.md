# Phase 0 recovery report

27 November 2026 · Windows PowerShell and Docker · **GREEN after final branch check**

## What was built

Phase 0 restored importable backend ML and graph services, deterministic demo seed, parameterized DuckDB queries, safe graph persistence, generic API errors, CORS allowlist and opt-in docs, PowerShell check runner, Docker boot, and a buildable frontend. This closure pass fixed Ruff and mypy errors, narrowed catches, typed the normalizer accumulator, and added HTTP injection tests using one-row Parquet fixtures. Existing tests were not deleted, skipped or loosened. The test addition and narrow third-party typing exceptions are explained in `docs/DECISIONS.md`.

## Commands run and actual outputs

`./tasks.ps1 check` (PowerShell command was `.\tasks.ps1 check`) exited **0**. The ordered stage output from the final run was:

```text
backend import: + D:\NirikshakM\.venv\Scripts\python.exe -c from app.main import app
Windows pytest: 49 passed, 1 warning in 27.12s
verify_phase1.py: PHASE 1 VERIFICATION SUCCESSFUL: Synthetic Generator & Pipeline Ready!
verify_phase2.py: PHASE 2 IMPLEMENTATION & VERIFICATION COMPLETED SUCCESSFULLY
verify_phase3.py: PHASE 3 SUITE VERIFICATION SUCCESSFUL: All 8 Tests Passed!
verify_phase4.py: PHASE 4 VERIFICATION SUITE SUCCESSFUL: ALL 8 TESTS PASSED!
verify_phase5.py: PHASE 5 VERIFICATION COMPLETE: ALL 24 TESTS PASSED!
ruff check: All checks passed!
mypy: Success: no issues found in 29 source files
bandit -r app: No issues identified. Total lines of code: 3769; High: 0; Medium: 0; Low: 0
pip-audit: No known vulnerabilities found
npm run lint: 0 errors, 2 warnings
npm run build: ✓ built in 18.62s
npm audit --omit=dev --audit-level=high: found 0 vulnerabilities
docker compose build backend: Image nirikshak-backend:latest Built
docker compose run --rm backend python scripts/seed_demo.py: synthetic: 5000 transactions, 4915 wallets, 10650 graph nodes
docker compose run --rm backend pytest -q: 49 passed, 1 warning in 6.69s
docker compose stop: backend and frontend Stopped
CHECK_EXIT=0
```

The two frontend lint warnings concern existing React Hook dependency arrays in WalletInvestigation and GraphPathInvestigator. They do not fail the configured lint command. The pytest warning is Starlette's `httpx` TestClient deprecation notice. Verify Phase 2's default live probe is optional when no server is on port 8000; its live upload step was separately run against disposable Docker backend on 127.0.0.1:18080 in the earlier Phase 0 audit and passed with 5000 valid, 0 rejected. The final in-process verification exited 0.

`docker compose up --build -d` reported `Container nirikshak_backend Healthy` and started the frontend on `127.0.0.1:5173`. `docker compose stop` then stopped both. `docker compose ps --status running` printed only its header. `rg -n pickle backend/app` returned no matches.

## Metrics and limits

The verified fixture has 5,000 transactions, 4,915 wallets, 10,650 graph nodes and 38,887 graph edges. Its source CSV SHA-256 is `be9448ac22895089f0274ded4dc9b63100db0e4b17ac688faf5f7981a85ca937`; both the original baseline and this phase pipeline independently measured 5216.56493532 BTC. The old 5174.20608283 BTC constant belonged to an unavailable fixture and was replaced by source CSV calculation. Frontend build took 18.62s, Windows pytest 27.12s and Docker pytest 6.69s. Peak RAM remains unverified; the observed Windows launcher process did not represent the Python process.

## Security evidence and residual risks

Real HTTP tests sent SQL operator, comment, UNION, stacked statement, null byte, Unicode, 10,000-character and traversal inputs through `/api/alerts`, `/api/alerts/{id}` and `/api/investigations/{wallet_id}` and its limits. Legitimate identifiers worked. Malformed inputs returned empty or 4xx results without leaking unrequested rows, SQL text, stack traces or file paths. Alert result counts stayed within `limit`; one-row Parquet fixture and leakage-sentinel file hashes stayed unchanged. The 422 handler now omits invalid input; investigation 400/404 messages no longer reflect identifiers. Default docs-off and configured-only CORS are runtime-tested. Bandit, pip-audit and npm production audit found no high or critical issue. Full authentication and broader security hardening remain in Phase 8; Phase 1 was not started.

## Decisions and Git state

The narrow third-party type ignores are listed individually in `docs/DECISIONS.md`. No Ruff rule or mypy module was broadly exempted. At this report revision the phase branch includes the hygiene merge from local main (`b1154e0`); final main merge and `phase-0-done` tag are to be recorded after the required post-merge check. No dataset, cache, secret, key or file over 5 MB was staged.
