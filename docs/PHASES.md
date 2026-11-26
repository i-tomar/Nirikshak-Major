# NIRIKSHAK — Phase File v3 (Windows + Docker) — save as `docs\PHASES.md`

*Codex must read this file and `AGENTS.md` before every phase. Each phase = one git branch, one gate, one report, one tag.*

---

## A. One-time setup on your Windows machine (do this yourself, before Codex)

**Install:** Python 3.11, Node 20+, Git, **Docker Desktop** (Linux containers), and Codex (CLI or IDE extension). In Docker Desktop → Settings → Resources, allow about 10–12 GB RAM (or create `C:\Users\<you>\.wslconfig` with `[wsl2]` and `memory=12GB`, then run `wsl --shutdown`). Keep the project path short (`D:\NirikshakM`) to avoid Windows long-path problems.

**Folder layout:** your datasets are in `D:\NirikshakM`, next to the repo. Run this in PowerShell from the repo folder:

```powershell
cd D:\NirikshakM\Nirikshakk-main
git init -b main
git config core.autocrlf false
Set-Content .gitattributes "* text=auto eol=lf"
Add-Content .gitignore "`n# real datasets, secrets, generated output - never commit`nbackend/data/external/`nbackend/data/analysis/`n*.mmdb`n.env`n*.key`nsecrets/"

# create dataset folders and copy the real data in
mkdir backend\data\external\elliptic, backend\data\external\bitcoinheist, backend\data\external\babd13, backend\data\geoip -Force
Copy-Item ..\elliptic_bitcoin_dataset\* backend\data\external\elliptic\ -Recurse
Copy-Item ..\BitcoinHeistData.csv backend\data\external\bitcoinheist\
# BABD-13: unzip the Kaggle download and copy its CSV file(s) into backend\data\external\babd13\

# add the two instruction files, then the first commit
mkdir docs -Force
# copy AGENTS.md to the repo root and PHASES.md to docs\ (from the docs you downloaded)
git add -A
git commit -m "baseline: repo + AGENTS.md + PHASES.md"
git status   # must say: nothing to commit, working tree clean
```

**Check that no dataset is tracked:** `git ls-files backend/data/external` must print nothing.

**GeoIP (optional but recommended):** put `GeoLite2-City.mmdb` and `GeoLite2-ASN.mmdb` (free MaxMind account) or DB-IP Lite files into `backend\data\geoip\`. Without them the labelled fallback table is used and Codex must say so.

**Optional:** create a private GitHub repo and `git remote add origin ...` so every merged phase can be pushed as a backup.

---

## B. Kickoff message (send this at the start of each Codex session, change the phase)

> Read `AGENTS.md` and `docs/PHASES.md` completely, then read `docs/DECISIONS.md`, `docs/BLOCKERS.md` and the latest `docs/phase_reports/`. Do **Phase N only**, following AGENTS.md Section 1 exactly: write the plan, create branch `phase/N-name` from `main`, implement, run the full check and the gate commands (including the Docker run), write the phase report, merge into `main` with `--no-ff` and tag `phase-N-done` **only if everything is green**. Then stop.

To run more than one phase, add: *"Then continue with the next phase the same way, and stop after Phase M."* Prefer at most 2–3 phases per session; long sessions lose context.

**What happens if you just paste the prompt and press go?** It starts, but it will not finish the project in one run. It works phase by phase, and you review each phase and give the next kickoff. The first session should be **Phase 0** only.

---

## C. Git rules (Codex follows; you can verify)

```powershell
git switch main; git status                  # must be clean
git switch -c phase/3-detection-ml           # one branch per phase
# work, commit often: git commit -m "phase-3: peeling detector"
.\tasks.ps1 check                           # must be green
git switch main
git merge --no-ff phase/3-detection-ml -m "phase-3: detection and ML"
git tag phase-3-done
git log --oneline --graph --decorate -15     # you check this after each phase
```

Red gate ⇒ stay on the phase branch, no merge, no tag, and write the problem in `docs/BLOCKERS.md`. Rollback is yours only: `git switch main; git reset --hard phase-2-done`.

---

## D. Phase map

| # | Branch | Phase | Effort (team-days) | Priority |
| --- | --- | --- | --- | --- |
| 0 | `phase/0-recover-boot` | Recover `app/ml`, boot, `tasks.ps1`, Docker boot, security baseline | 2–3 | MUST |
| 1 | `phase/1-data-layer` | CSV/JSON/XML streaming ingest, GeoIP, generator, safe XML/uploads | 4–6 | MUST |
| 2 | `phase/2-correlation` | Cross-layer correlation with typed edges | 3–4 | MUST |
| 3 | `phase/3-detection-ml` | Features, clustering, detectors, models, propagation | 6–8 | MUST |
| 4 | `phase/4-real-data` | Elliptic, BitcoinHeist and BABD-13 adapters and benchmarks | 5–7 | MUST |
| 5 | `phase/5-explainability` | SHAP, evidence ledger, sufficiency | 4–5 | MUST |
| 6 | `phase/6-sparse-engine` | Transaction DNA, bounded expansion, counterfactual | 6–8 | MUST |
| 7 | `phase/7-evaluation` | Computed metrics, baselines, adversarial, scale | 4–5 | MUST |
| 8 | `phase/8-auth-security` | Auth, roles, audit chain, hardening, security tests | 4–5 | MUST |
| 9 | `phase/9-frontend-live` | UI on live API, Cytoscape, real-data page | 6–8 | MUST |
| 10 | `phase/10-cases-provenance` | Cases, snapshots, hashed PDF | 4–5 | SHOULD |
| 11 | `phase/11-docker-package` | Hardened Docker, offline bundle, Windows installer | 3–4 | MUST |
| 12 | `phase/12-docs-demo` | README, write-up, demo script, Q&A, limitations | 3–4 | MUST |
| 13 | `phase/13-optional` | Neo4j export, Electron shell, bare-metal Linux install | 3–5 | COULD |

Auth basics start in Phase 0 and the full audit is Phase 8, early on purpose, so the UI and cases are built on a secure API instead of retrofitted.

---

## Phase 0 — Recover & boot (`phase/0-recover-boot`)

**Goal:** a clean checkout starts on Windows and in Docker, tests pass, and the baseline is safe.

- [ ] Interface table of everything `app.ml.*` must export, from `verify_phase4/5.py`, `tests/`, `frontend/src/lib/api.ts`
- [ ] Recreate `backend/app/ml/` (`analyzer, features (24 features), anomaly, risk, evidence, clustering`) producing `wallet_features.parquet`, `wallet_anomalies.parquet`, `investigative_leads.parquet`, `analysis_summary.json`
- [ ] `Makefile` **and** `tasks.ps1` with identical targets: `setup test check seed run evaluate real-eval security`
- [ ] `scripts/seed_demo.py` (generate → ingest → analyse → build graph)
- [ ] Pinned `requirements.txt` and `requirements-dev.txt` for Python 3.11 (xgboost, shap, maxminddb, defusedxml, argon2-cffi, PyJWT, cryptography, reportlab, pytest, ruff, mypy, bandit, pip-audit)
- [ ] Docker: `docker compose up --build` starts backend + frontend; named volumes for `data/`, `models/`, `cases/`; read-only mounts for `external/` and `geoip/`; web port published on `127.0.0.1` only
- [ ] Quick security fixes: parameterise SQL in `routers/alerts.py`; CORS allow-list from config; OpenAPI docs off unless `NIRIKSHAK_ENABLE_DOCS=1`; generic error handler; **replace pickle graph persistence** in `graph/builder.py`
- [ ] `.env.example`, `docs/DECISIONS.md`, `docs/BLOCKERS.md`, `docs/phase_reports/`

**Gate commands:** `.\tasks.ps1 setup; .\tasks.ps1 seed; .\tasks.ps1 check`; `docker compose up --build` shows a healthy backend; `Select-String -Path backend\app\* -Pattern pickle -Recurse` finds nothing; an injection attempt on `/api/alerts/{id}` fails.

---

## Phase 1 — Data layer (`phase/1-data-layer`)

**Goal:** meet the ingestion and GeoIP requirements and handle large files safely.

- [ ] Streaming CSV, JSON (array and NDJSON), **XML via `defusedxml`/`iterparse`**; list-field parsing for all forms
- [ ] Upload hardening: size cap, content sniffing, random server filenames, archive rejection, SHA-256, streaming to disk
- [ ] Quarantine `rejected.parquet`; UTC normalisation; schema versioning; `tx_inputs`, `tx_outputs`, `ip_enrichment` tables
- [ ] GeoIP with `maxminddb` over unique IPs; labelled `synthetic_lookup` fallback
- [ ] Generator: `--n-tx --seed --profile normal|sparse|adversarial`, CSV/JSON/XML outputs, hidden `ground_truth.json`, CoinJoin and ransomware scenarios
- [ ] Benchmark script → `docs/benchmarks.md` (100K, 1M, optional 5M: time + peak RAM, on Windows and in Docker)
- [ ] Tests: malformed rows in all formats, XXE and entity-bomb XML, path-traversal filenames, oversized upload

**Gate:** all three formats ingest identical data to identical tables; hostile XML/filenames are rejected; 1M rows fit in the Docker memory limit.

---

## Phase 2 — Correlation (`phase/2-correlation`)

- [ ] txid join → as-of time-window join (configurable) → shared IP/ASN links
- [ ] Every link: rule name/version, window, timestamp, evidence type, confidence, direct/inferred
- [ ] First-seen-relay indicator with confidence cap and caveat text
- [ ] `correlations.parquet` consumed by the graph builder as typed edges; `GET /api/correlations/{wallet}`
- [ ] Tests: window edges, duplicate IPs, missing txid, out-of-order timestamps

**Gate:** for any wallet, list every IP/ASN link with rule, window and confidence.

---

## Phase 3 — Detection & ML (`phase/3-detection-ml`)

- [ ] \~40 wallet features via Polars/DuckDB
- [ ] Union-find clustering (CoinJoin excluded), cluster profiles, similar-entity suggestions; re-enable `/api/clusters`
- [ ] Detectors: peeling chain, CoinJoin-like, multi-hop, fan-in/out, burst — structured evidence
- [ ] Isolation Forest + second unsupervised detector
- [ ] XGBoost with time-aware and cluster-grouped splits, imbalance handling, calibration, `model_card.json` with file hash verified on load
- [ ] Propagation from `config/seed_wallets.json` with decay, edge weights, confidence floor, hop cap, hub cap
- [ ] Priority 0–100, separate confidence, tiers; leads table includes `pattern_name` and `confidence`

**Gate:** each of the four required AI/ML areas runs end to end with unit tests on hand-built fixtures; `tests/test_clustering*.py` pass.

---

## Phase 4 — Real-data track (`phase/4-real-data`)

**Goal:** prove the ML approach on real public labels. These models are benchmarks, not wired into the wallet alert pipeline.

- [ ] For **each** dataset in `backend/data/external/` (Elliptic, BitcoinHeist, BABD-13) write `docs/data_audit/<dataset>.md` first: files, columns, dtypes, rows, label counts, time coverage. Derive mappings from the audit only
- [ ] **Elliptic:** time-step split (train ≤ step 34, test 35–49); `unknown` excluded from training and metrics; XGBoost vs a simple baseline; PR-AUC, illicit precision/recall/F1, Precision@K, per-time-step performance
- [ ] **BitcoinHeist:** binary (`white` vs ransomware) and per family; split by year; imbalance handling; SHAP on the real model; per-family recall; chunked read of the 230 MB file
- [ ] **BABD-13 (required):** binary illicit/licit and 13-class; time-aware split if timestamps exist, else stratified with leakage notes; per-class precision/recall; SHAP summary
- [ ] Optional simulated network overlay on real transactions, flagged `simulated=true`, source `real_plus_simulated_network`
- [ ] `real_eval_<dataset>.json`, `docs/real_data_results.md`, `GET /api/model/real-data`
- [ ] Tests on tiny fixtures that mimic each dataset’s real format (never commit the real files)

**Gate:** `.\tasks.ps1 real-eval` regenerates all three results from `external/`; reports state plainly what real-data scores do and do not mean; `git ls-files backend/data/external` prints nothing.

---

## Phase 5 — Explainability (`phase/5-explainability`)

- [ ] SHAP on top-K alerts, signed top-8 contributions stored
- [ ] Isolation Forest explanation as per-feature percentile deviation (labelled)
- [ ] Evidence ledger: Behavioural / Structural / Network-contextual with direct/inferred/contextual tags and source txids
- [ ] Evidence-sufficiency formula (documented, unit-tested), blind-spot report, risk-change explanation
- [ ] Remove fixed feature importances; serve from the model card

**Gate:** `GET /api/alerts/{id}` returns SHAP, three evidence groups, sufficiency, blind spots and provenance.

---

## Phase 6 — Sparse-evidence engine (`phase/6-sparse-engine`)

- [ ] Transaction DNA fingerprint + similarity to labelled-pattern centroids
- [ ] Bounded expansion (≤2 hops, ≤150 nodes, relevance-ranked, stop on small change), efficiency logged
- [ ] Counterfactual check and fragile-lead flag; next-best action with justification
- [ ] `POST /api/investigations/{wallet}/expand`

**Gate:** a one-transaction wallet shows sufficiency LOW, the pulled-in neighbours and why, the counterfactual delta and a next action.

---

## Phase 7 — Evaluation (`phase/7-evaluation`)

- [ ] `scripts/evaluate.py` → `evaluation_report.json` + `docs/evaluation.md`
- [ ] Normal, sparse and adversarial datasets; baseline vs full; ablations; sparse-wallet metrics separate
- [ ] Scale test (100K/1M/5M), API latency, reproducibility hash
- [ ] `/api/model/metrics` reads the report or returns `not_evaluated`

**Gate:** `.\tasks.ps1 evaluate` works; `Select-String -Path backend\app\*,frontend\src\* -Pattern "0.962|0.931|0.968|0.925|0.928" -Recurse` finds nothing.

---

## Phase 8 — Auth & security hardening (`phase/8-auth-security`)

- [ ] argon2id users, `scripts/create_admin.py` (no default password), lockout/backoff
- [ ] Signed short-lived tokens, roles admin/analyst/viewer, server-side route enforcement, object-level checks
- [ ] Tamper-evident hash-chained audit log + `/api/audit/verify`
- [ ] Rate limits, request timeouts, concurrency cap on analysis, security headers/CSP, generic errors
- [ ] Model-file hash verification, formula-injection-safe exports, optional field-level encryption (Fernet)
- [ ] Security test suite covering every S17 item in AGENTS.md; `docs/SECURITY.md` (threat model, residual risks, key management)
- [ ] `.\tasks.ps1 security`: bandit, pip-audit, npm audit, secrets scan → `docs/security/`

**Gate:** all security tests pass (on Windows and inside Docker); unauthenticated calls get 401; role escalation and IDOR attempts fail; audit tampering is detected.

---

## Phase 9 — Frontend on live data (`phase/9-frontend-live`)

- [ ] Login screen and token handling (memory-based; the choice documented in DECISIONS.md)
- [ ] Demo files only when `VITE_DEMO_MODE=true`, with a visible DEMO banner
- [ ] Split `Dashboard.tsx` and `WalletInvestigation.tsx`; import wizard with quarantine report
- [ ] Alerts with filters/pagination; **alert detail** (SHAP waterfall, three evidence panels, sufficiency badge, why prioritised, counterfactual, next action, blind spots, provenance)
- [ ] Cytoscape link analysis: bounded subgraph, node cap, expand on click, edge-type filter, time slider, colour by evidence type
- [ ] Clusters, patterns, model analytics with synthetic and real-data (Elliptic, BitcoinHeist, BABD-13) in separate labelled tables
- [ ] Loading/empty/error states, virtualised tables; no `dangerouslySetInnerHTML`

**Gate:** delete the demo files and the full UI works on a freshly ingested dataset; lint, build and smoke tests pass.

---

## Phase 10 — Cases & provenance (`phase/10-cases-provenance`)

- [ ] SQLite cases, pinned leads, notes, decisions (confirm/reject/annotate)
- [ ] Immutable case snapshot (dataset hash, parser/model/rule versions, run id)
- [ ] Hashed PDF with the wording “investigative lead — not proof”; decisions stored as future evaluation labels, no silent retraining

**Gate:** a lead becomes a case, is annotated, exports a hashed PDF, and regenerates identically from the snapshot.

---

## Phase 11 — Docker packaging (`phase/11-docker-package`)

- [ ] Hardened images: non-root, read-only root FS, `cap_drop: ALL`, `no-new-privileges`, internal backend network, limits, healthchecks, pinned base images
- [ ] Offline bundle: `docker save` tarball + `install.ps1` (loads images, creates volumes and secrets, prompts for the admin, starts the stack) and `uninstall.ps1`
- [ ] `docs/OPERATIONS.md` (start/stop, backup/restore, key rotation, upgrade)
- [ ] Test with the internet disconnected and a fresh Docker environment; record timings

**Gate:** after `install.ps1` with no internet, the login page and dashboard work. Bare-metal Linux is listed in LIMITATIONS.md as “Linux-tested via Docker only”.

---

## Phase 12 — Docs & demo (`phase/12-docs-demo`)

- [ ] README rewritten to match reality (built vs roadmap)
- [ ] `docs/TECHNICAL_WRITEUP.md`, `DEMO_SCRIPT.md` (7-minute flow + 60-second fallback), `JUDGE_QA.md`, `LIMITATIONS.md`
- [ ] Remove unused assets, add a LICENSE placeholder

**Gate:** a teammate who did not build it can run the demo from the script alone.

---

## Phase 13 — Optional (`phase/13-optional`)

Neo4j CSV export + 3 saved Cypher queries (nothing depends on it); Electron shell with `contextIsolation: true`, `nodeIntegration: false`, minimal preload API; bare-metal Linux install script and test.

---

## E. Your checklist after each phase

1. `git log --oneline --graph --decorate -10` shows the merge commit and the `phase-N-done` tag.
2. Read `docs/phase_reports/phase-N.md` and `docs/BLOCKERS.md`.
3. Run `.\tasks.ps1 check` yourself. Do not trust the report alone.
4. `git diff phase-(N-1)-done -- tests` — confirm no test was weakened or deleted without a reason in `DECISIONS.md`.
5. Spot-check honesty: no hardcoded metrics, no “owned by” wording, every result labelled by data source.
6. `git ls-files backend/data/external` prints nothing; then `git push` to your private remote.

## F. Windows-specific watch list

| Issue | What to do |
| --- | --- |
| Docker Desktop not running | Start it before any phase that builds images or runs `check` |
| A package fails to install on Windows (xgboost, shap, etc.) | Stay on Python 3.11; Codex logs it in `BLOCKERS.md` and does not switch versions silently |
| Antivirus slows or blocks Parquet reads | Exclude the project folder |
| Slow bind mounts | Use named volumes for data; only datasets and GeoIP are bind-mounted (read-only) |
| CRLF/LF problems | `.gitattributes` enforces LF; do not re-save files in editors that convert to CRLF |
| Long paths | Keep the project under `D:\NirikshakM`; avoid deeply nested folders |
| Out of memory on 1M+ rows | Raise Docker memory; read datasets chunked or lazily |

## G. Risk register

| Risk | Mitigation |
| --- | --- |
| `app/ml` rebuilt differently from what tests expect | Tests and verify scripts are the spec; any test change needs a written reason in DECISIONS.md |
| Codex weakens tests or fakes a gate | Rule 1.5 forbids it; you review the diff of `tests/` every phase |
| Synthetic-only scores look inflated | Real-data track in Phase 4, adversarial and sparse sets in Phase 7, everything labelled by source |
| Long sessions lose context | One phase per session; plan file written first; reports persisted in `docs/` |
| Real datasets leak into git | `.gitignore` plus the `git ls-files` check after every phase |
| Security retrofitted too late | Safe defaults from Phase 0, full audit in Phase 8 before the UI is finished |
| Scope creep (Neo4j, GNN, Electron) | Locked behind Phase 13 |
