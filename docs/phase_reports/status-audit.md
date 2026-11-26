# Repository status audit

27 November 2026 · Windows PowerShell · `D:\NirikshakM`

**Phase 0 — PARTIAL.** The app imports, the seed runs, both pytest suites pass, and Docker serves a healthy backend. Legacy verification remains red. **Phase 1 — PARTIAL.** The existing CSV/JSON pipeline covers part of the scope. XML, streaming, GeoIP and the scale gate remain unverified or missing.

## Git safety and hygiene

Both required instruction files were present and read. The index and local commit trees were checked across refs, reflogs and unreachable commits for dataset, environment, cache and key paths. The search returned no prohibited paths. The tracked `.env.example` is a configuration template. The initial Git command output is reproduced below.

```text
git status
On branch phase/0-recover-boot
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   AGENTS.md
	modified:   backend/app/graph/builder.py
	modified:   backend/app/ml/analyzer.py
	modified:   backend/app/pipeline/loader.py
	modified:   backend/app/pipeline/storage.py
	modified:   backend/app/routers/datasets.py
	modified:   backend/app/routers/investigations.py
	modified:   backend/app/routers/models.py
	modified:   backend/scripts/seed_demo.py
	modified:   docs/DECISIONS.md
	modified:   docs/PHASES.md
	modified:   frontend/package-lock.json
	modified:   frontend/package.json

no changes added to commit (use "git add" and/or "git commit -a")
git log --oneline --graph --decorate -20
* d17f273 (HEAD -> phase/0-recover-boot) phase-0: type graph and investigation callbacks for lint gate
* 90b216d phase-0: add pinned setup, seeded demo and Docker checks
* c8ba732 phase-0: recover wallet analysis and behavioral clustering
* 0d06e64 phase-0: establish relocated project baseline and recovery plan
* c8a585e (origin/main, origin/HEAD, main) Initial commit
git tag
(no output)
git ls-files | Select-String (requested pattern)
(no output)
Forbidden paths in index (excluding .env.example)
Forbidden paths in local commit history (all refs, reflogs, and unreachable commits)
Local branches
  main                 c8a585e [origin/main] Initial commit
* phase/0-recover-boot d17f273 phase-0: type graph and investigation callbacks for lint gate
```

Moved the three Elliptic CSVs into `backend/data/external/elliptic/`, BitcoinHeist into `backend/data/external/bitcoinheist/`, and `2204.05746v3.pdf` into `docs/`. Git ignored all five files at their destinations. The staged review listed exactly `.gitattributes`, `.gitignore`, `AGENTS.md`, `docs/DECISIONS.md`, and `docs/PHASES.md`. The largest staged blob was 25,055 bytes. Hygiene commit `9fa07f1` merged into local `main` with merge commit `b1154e0`. No tags or push. The clean worktree for the merge started at the license-only `main`. The app audit covers the active `phase/0-recover-boot` checkout at `d17f273` plus its pre-existing working-tree edits. No application code changed during this session.

## Phase 0 — Recover and boot

| Checkbox | Status | Evidence |
| --- | --- | --- |
| Interface inventory | DONE | `docs/phase_reports/phase-0-interfaces.md` identifies the six ML modules, their callers and persisted output contracts. |
| Recover ML and persist analysis outputs | DONE | Modules listed below. `backend/app/ml/analyzer.py` declares the four required outputs. Seed succeeded, and `backend/scripts/verify_phase4.py` passed all eight checks, including features, model reload, scoring and API. |
| Matching Make and PowerShell targets | DONE | `Makefile:2`, `tasks.ps1:1`, and `scripts/tasks.py:14` declare the same eight targets. Evaluation implementations belong to later phases. |
| Seed demo | DONE | `backend/scripts/seed_demo.py` generated, normalized, analyzed and built the graph for 5,000 transactions and 4,915 wallets. |
| Pinned Python 3.11 requirements | DONE | `backend/requirements.txt` and `backend/requirements-dev.txt` pin the requested direct dependencies. Import worked in the Windows venv and Docker built the backend. Transitive dependencies are not fully locked. |
| Docker build, boot, storage and port | DONE | Compose configuration and boot returned 0. Backend was healthy and returned JSON through port 5173. Named volumes are `data`, `models`, `cases`. External data and GeoIP are read-only mounts. Only the frontend publishes a port, on `127.0.0.1`. |
| Quick security fixes | PARTIAL | `backend/app/routers/alerts.py:46–108` binds query arguments. `backend/app/main.py:10–19` limits CORS and disables docs by default, and lines 65–69 add a generic handler. `backend/app/routers/analysis.py:35–39` still handles some failures explicitly and returns exception text. `backend/app/graph/builder.py` persists JSON and exports GraphML. The legacy verifier did not reach its graph round-trip assertion. |
| Support files | DONE | `.env.example`, `docs/DECISIONS.md`, `docs/BLOCKERS.md`, and `docs/phase_reports/` exist. |

The complete combined Phase 0 gate is **red** because legacy verifier 3 failed. Verifier 5 depends on it. Full static and dependency audits were not rerun in this session. The active alert injection attempt is **unverified**. The audit checked parameter binding statically.

## Phase 1 — Data layer

| Checkbox | Status | Evidence |
| --- | --- | --- |
| Streaming CSV, JSON and XML with list parsing | PARTIAL | `backend/app/pipeline/loader.py:15–153` handles CSV and JSON with list aliases, reads whole files, and accepts JSON arrays and a `transactions` wrapper. NDJSON, XML and streaming are missing. |
| Upload hardening | PARTIAL | `backend/app/routers/datasets.py:174–202` allows only `.csv` and `.json` by filename suffix and reads the upload in one operation. An explicit size cap, content sniffing, random filenames, archive content checks, upload SHA-256 and disk streaming were not found. |
| Rejected Parquet, UTC, versioning and normalized tables | PARTIAL | `backend/app/schemas/transaction.py:5` declares `schema_v1`. `backend/app/pipeline/normalizer.py` builds transactions, wallets and network observations. A rejected Parquet table, guaranteed UTC normalization, and `tx_inputs`, `tx_outputs`, `ip_enrichment` were not verified. |
| Offline GeoIP and labelled fallback | MISSING | `maxminddb` is pinned and the Compose mount exists. No MaxMind enrichment code or `synthetic_lookup` fallback was found in `backend/app`. |
| Expanded generator | PARTIAL | `backend/scripts/generate_dataset.py:697–743` writes CSV, JSON and backend-only labels, with `--num-tx` and `--seed`. No `--n-tx`, `--profile`, XML output, or required CoinJoin and ransomware scenarios were found. |
| Scale benchmark | MISSING | No `docs/benchmarks.md` or matching Phase 1 scale benchmark script was found. 100K and 1M runtime and peak RAM are unverified. |
| Parser and upload regression tests | PARTIAL | `backend/scripts/verify_phase2.py` covers malformed CSV and JSON, empty uploads and an unsupported extension. XML, hostile filename and oversized upload checks were not found. |

The Phase 1 gate is **unverified**. The legacy script named `verify_phase1.py` checks the earlier CSV/JSON fixture and does not cover the current Phase 1 gate.

## Runtime and source evidence

```text
backend/app/ml/
  __init__.py
  analyzer.py
  anomaly.py
  clustering.py
  evidence.py
  features.py
  risk.py

Windows .venv, from backend/
  import app.main: OK
  exit=0

Windows scratch copy of current backend
  synthetic: 5000 transactions, 4915 wallets, 10650 graph nodes
  seed exit=0
  44 passed, 1 warning in 26.62s
  pytest exit=0

Docker
  docker compose config exit=0
  Container nirikshak_backend Healthy
  docker compose up exit=0
  {"status":"ok","service":"nirikshak-backend","version":"0.1.0"}
  docker compose stop exit=0
  docker compose ps --status running: header only
  Disposable Linux container: 44 passed, 1 warning in 6.92s
  container pytest exit=0

rg -n -i 'pickle' backend/app
  exit=1 (no matches)
rg -n '0\.(962|931|968|925|928)\b' backend/app frontend/src
  exit=1 (no matches)
```

Both pytest runs had **0 failed, 0 skipped**. The warning is a Starlette deprecation about the TestClient HTTP dependency. Windows fixture output was written in a temporary backend copy. The Docker pytest run used a disposable container without project data mounts.

| Legacy verifier | Observed result |
| --- | --- |
| `verify_phase1.py` | Exit 0. Synthetic Generator & Pipeline Ready. |
| `verify_phase2.py` | Exit 0. All in-process checks passed. The separate live upload to port 8000 was unverified after Windows returned connection refused (10061). Docker health was checked separately through port 5173. |
| `verify_phase3.py` | Exit 1. DuckDB reported `5216.56493532 BTC`. Line 148 asserts `abs(tot_vol - 5174.20608283) < 1e-6` and raised `AssertionError`. |
| `verify_phase4.py` | Exit 0. All eight checks passed. |
| `verify_phase5.py` | Exit 1. Its Phase 3 regression stopped on the same total-volume assertion before the graph checks ran. |

The two f-strings in `backend/app/routers/alerts.py` format user-facing messages at lines 66 and 113. Query strings use `read_parquet(?)` and bound values for filters, limits and identifiers. The exact five metric constants did not appear in the scanned paths. This search is limited to those values.

## Tests since the source baseline

`git diff 0d06e64 -- tests backend/tests` and `git log --oneline 0d06e64..HEAD -- tests backend/tests` both produced no output. No tests under either directory were removed, skipped or loosened since the source baseline. The existing conditional skips remain in `test_clustering.py:45`, `test_clustering_api.py:50`, `test_dataset_lifecycle.py:45`, `test_graph_path.py:36,38` and `test_investigations.py:38`. None fired in either run. Outside those directories, `backend/scripts/verify_phase5.py:227` now decodes the graph JSON with the serializer's custom attribute names. It still asserts full graph equality.
