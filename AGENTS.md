# 0. MISSION

You are a senior full-stack, ML and security engineer. Turn this repository (`Nirikshakk-main`) into a **fully working, secure, offline-capable Bitcoin transaction intelligence system** for Smart India Hackathon **PS 26146 (NTRO) — "AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic"**. It is developed on **Windows** and **delivered and run through Docker (Linux containers)**. It must also prove its ML on **real public Bitcoin datasets** (Elliptic, BitcoinHeist, BABD-13) as well as on synthetic data.

Official requirements: ingest bulk Bitcoin transaction/network metadata in **CSV, JSON, XML** (`timestamp, src_ip, dst_ip, src_port, dst_port, txid, input_addresses[], output_addresses[], input_amounts[], output_amounts[], fee, script_type, geo_country/asn` with an **open-source offline GeoIP DB**); **correlate** network-layer (IP/port/timing) with blockchain-layer (wallet/TXID/amount) data; build an **entity/transaction graph**; implement **working trained ML** (entity clustering, anomaly detection, peeling-chain/CoinJoin detection, risk scoring with propagation from seed wallets); produce a **ranked, explainable alert list with confidence scores**; provide a **dashboard / link-analysis view with evidence for each flag**; ship a workable offline solution, repo and short technical write-up.

Product principle: *turn a huge graph into a small set of ranked, explainable, honestly-uncertain investigative leads.* Correlation gives context, never identity or guilt.

---

# 1. HOW TO WORK — MANDATORY WORKFLOW (read before every phase)

## 1.1 Session start checklist (do ALL, in order, every session)

1. Read `AGENTS.md` (this file) fully.
2. Read `docs/PHASES.md` fully and locate the phase you were asked to do.
3. Read `docs/DECISIONS.md`, `docs/BLOCKERS.md` and the newest file in `docs/phase_reports/` (create missing folders/files).
4. Run `git status`; the tree must be clean, otherwise stop and report. Run `git branch --show-current`.
5. Write `docs/phase_reports/phase-N-plan.md` (files to create/change, tests to add, how each gate will be proven) **before writing code**.

## 1.2 Branching and commits

- `main` holds only **green, gate-passed** work. Never commit directly to `main`.
- One branch per phase from `main`: `git switch -c phase/N-short-name`. Commit small and often: `phase-N: <what>`.
- Never commit datasets, `.env`, secrets, keys, `.mmdb` files, model artifacts > 50 MB, or anything under `backend/data/external/`.
- When the phase is done and everything in 1.3 passes: `git switch main`, `git merge --no-ff phase/N-short-name -m "phase-N: <summary>"`, `git tag phase-N-done`. Then stop (or continue only if the kickoff message says so).
- A failing gate means: stay on the phase branch, fix, re-run. Never merge red. Never force-push or rewrite history.

## 1.4 What "tests passed" means (run before every merge)

Provide **both** `Makefile` and `tasks.ps1` with identical targets (`setup test check seed run evaluate real-eval security`). On Windows the developer runs `.\tasks.ps1 check`. `check` runs: backend import test; `pytest -q`; `scripts/verify_phase*.py` that apply; `ruff` and `mypy` on changed Python; `bandit -r backend/app`; `pip-audit`; frontend `npm run lint`, `npm run build`, `npm audit --omit=dev`; **the backend test suite again inside the Docker image** (`docker compose run --rm backend pytest -q`) so Windows-only passes cannot hide Linux failures; plus the gate commands in the Phase file. Fail on HIGH/CRITICAL audit findings unless justified in `docs/DECISIONS.md`. Paste real outputs into the phase report.

## 1.5 Decisions, blockers, honesty

- Ambiguity: choose the safest option, proceed, log it in `docs/DECISIONS.md` (decision, reason, alternative). Stop and ask only if continuing would be unsafe or destroy work.
- If something cannot be finished, write it in `docs/BLOCKERS.md` with the exact error and what you tried. **Never fake a pass. Never hardcode results, weaken/delete a test, or silence a security check without a written reason.**
- If a dependency fails to install on Windows, log it; do not silently switch to an untested version. Python 3.11 is the pinned version.

## 1.6 Phase report (write `docs/phase_reports/phase-N.md` and print it)

1. What was built (files). 2) Commands run + **actual outputs**. 3) Metrics measured (real only), timings, peak RAM. 4) What is not done or approximate. 5) Security checks run and results. 6) Decisions/risks needing my input. 7) Git state (branch, commits, tag).

---

# 2. VERIFIED FACTS ABOUT THE REPO

1. `backend/app/ml/` **is missing** (analyzer, anomaly, features, risk, evidence, clustering). Six modules import it, so `uvicorn app.main:app` fails. Specs exist in `scripts/verify_phase4.py`, `verify_phase5.py`, `tests/test_clustering*.py`, `tests/test_investigations.py`, `frontend/src/lib/api.ts`. Treat them as the interface contract.
2. Reusable: `pipeline/{loader,normalizer,storage}.py` (CSV/JSON, Polars, Parquet, DuckDB), `graph/{builder,queries,serializers}.py` (NetworkX), `schemas/*`, routers, `scripts/generate_dataset.py` (hidden ground truth; multihop, peeling, burst, network-correlated, fan-in), verify scripts, tests, a large React/TS UI, Dockerfiles and `docker-compose.yml`.
3. `routers/models.py` returns **hardcoded** accuracy/precision/recall/F1/ROC-AUC/confusion matrix/feature importances → replace with computed values.
4. Missing: XML ingestion, GeoIP, SHAP/XGBoost, streaming ingestion (loader reads whole files), case management, PDF export, authentication.
5. **Security problems found:** SQL built by string interpolation in `routers/alerts.py`; CORS `*` with credentials; **`graph/builder.py` persists the graph with `pickle`**; no auth; no upload hardening; XML would add XXE/entity-bomb risk.
6. `frontend/src/pages/Dashboard.tsx` (\~98 KB) drives the main graph from hardcoded demo files `src/demo/*`; Alerts and WalletInvestigation use the live API. The clustering router is commented out in `main.py`. The README claims Neo4j/ClickHouse/XGBoost/SHAP/MaxMind/PDF that do not exist.

---

# 3. NON-NEGOTIABLE RULES

1. **No fabricated numbers.** Every metric in API/UI/docs is computed by code and read from a saved report, else `"status": "not_evaluated"`.
2. **No claims of identity, guilt, court-admissibility or money recovered.** Wording: "investigative lead", "correlated with", "inferred". Never "owned by", "criminal", "court-ready".
3. **Label the data source** on every metric/alert: `synthetic`, `real_public`, `real_plus_simulated_network`. Real and synthetic results go in separate tables.
4. **Ground-truth labels never leave the backend** (API, UI, logs, reports). Tested.
5. **No outbound network calls at runtime**, tested. Never download anything during a run.
6. **Parameterised SQL only; no `pickle`/`eval`/`exec` on persisted or untrusted data.**
7. **Determinism:** fixed seeds; same input + versions ⇒ same ranking hash, tested.
8. **Do not add** Neo4j, ClickHouse, Kafka, Flink, Spark, Kubernetes, MLflow, Feast, PyG/GNN, Redis or cloud services to the core (optional Neo4j export only in the last optional phase).
9. Do not delete working features; keep existing tests green; never commit large data. Python: type hints, docstrings, `pathlib`. TypeScript: strict.
10. One phase at a time; the Phase file's gates are binding.

---

# 4. SECURITY REQUIREMENTS (safe defaults from Phase 0; full audit in the Security phase)

**Authentication & authorisation**

- S1. Local auth: users in SQLite; passwords hashed with **argon2id** (`argon2-cffi`); **no default or hardcoded passwords** — `scripts/create_admin.py` prompts on first run; lockout/backoff after repeated failures.
- S2. Short-lived signed tokens (`PyJWT`), key generated at first run and stored outside the repo / as a Docker secret, rotatable. Roles `admin`, `analyst`, `viewer`. Every route except `/api/health` and `/api/auth/login` needs a token; roles enforced server-side per route (viewers read-only; admins manage users/config/models; analysts+admins create cases/exports).
- S3. Object-level checks: users access only cases they own or are assigned.

**Input handling**

- S4. Uploads: size cap (default 500 MB), extension + content sniffing, random server-side filenames (never use client filenames in paths), reject archives/nested zips, stream to disk, compute SHA-256.
- S5. **XML via `defusedxml` only** (no DTD, no external entities, entity-expansion limits). CSV/JSON parsers cap field length, nesting and list sizes.
- S6. Pydantic validation with bounds on all inputs (`limit`, `hops`, `max_nodes`); reject unknown fields on writes.
- S7. Output encoding: CSV/PDF exports neutralise formula injection (prefix `'` before `= + - @`); React never uses `dangerouslySetInnerHTML`; PDF text escaped.

**Data protection**

- S8. Replace `pickle` graph persistence with GraphML/JSON or Parquet edge tables. `joblib` models load only after SHA-256 verification against `model_card.json`, from a directory the API cannot write to.
- S9. Secrets only from environment/Docker secrets/permission-restricted files; `.env` git-ignored; a test greps the repo for keys/passwords.
- S10. Case DB/exports: restrictive permissions **inside the container**; optional field-level encryption (`cryptography` Fernet) for notes/decisions, key kept outside the DB; document key rotation.
- S11. **Tamper-evident audit log:** append-only table, each row hashes the previous row; logs login, failed login, upload, analysis run, case access, export, config/model/user changes; no passwords/tokens/payloads in logs; `/api/audit/verify` detects tampering.

**Transport, headers, abuse**

- S12. CORS allow-list from config (no `*`). Security headers (CSP self-only, `X-Content-Type-Options`, `frame-ancestors`, `Referrer-Policy`, `Permissions-Policy`); TLS optional via reverse proxy with documented self-signed certs.
- S13. Rate limits on login/upload/heavy endpoints, request timeouts, cap on concurrent analysis jobs, generic client errors (details only in server logs).

**Runtime & supply chain**

- S14. Docker: non-root user, `read_only` root FS with explicit writable volumes, `cap_drop: [ALL]`, `no-new-privileges`, healthchecks, resource limits, backend on an `internal: true` network, only the web port published, and only to `127.0.0.1`.
- S15. Pin all dependencies (hashes where practical), commit `package-lock.json`, run `pip-audit`, `npm audit`, `bandit` (and `semgrep` if available offline); store results in `docs/security/`.
- S16. Debug off by default; OpenAPI docs disabled unless `NIRIKSHAK_ENABLE_DOCS=1`.
- S17. Tests for: SQL injection on every query param, path traversal on upload/export, XXE/entity-bomb XML, oversized/malformed uploads, auth bypass, role escalation, IDOR on cases, rate limit, audit-chain tamper detection, ground-truth non-leakage, no-outbound-network, secrets scan.
- S18. `docs/SECURITY.md`: threat model (assets, actors, trust boundaries, abuse cases), mapping S1–S19, residual risks, key management, backup/restore, incident handling.
- S19. Permissions, `read_only`, `cap_drop` and similar controls are enforced **inside the container**, not on the Windows host; Windows-side code must not fail when `chmod` has no effect. JWT/encryption keys live in Docker secrets or a mounted file outside the repo, never in an image layer.

---

# 5. ENVIRONMENT AND STACK

- **Dev machine: Windows 11 (native)**, i5-12450H, \~16 GB RAM, CPU only. Develop with a Python 3.11 venv and Node 20 on Windows. **Docker Desktop (Linux containers) is the reference runtime and the delivery format.** Code must work on Windows paths and in the Linux container: use `pathlib`; never hardcode `/` or `\`; never rely on `chmod`, `fork` or Linux-only tools outside containers. LF line endings (`.gitattributes: * text=auto eol=lf`). Bare-metal Linux install comes after the Windows/Docker version works and is a post-project step.
- Docker rules: **named volumes** for `data/`, `models/`, `cases/`; `backend/data/external/` and `backend/data/geoip/` mounted **read-only** from the host; multi-stage Dockerfile with pinned base images; `docker compose up --build` must start the full system.
- Backend: Python 3.11, FastAPI, Pydantic v2, Polars, DuckDB, PyArrow, NetworkX (igraph only if a benchmark justifies it), scikit-learn, **xgboost**, **shap**, joblib, **maxminddb**, **defusedxml**, **argon2-cffi**, **PyJWT**, **cryptography**, **reportlab**, pytest, httpx, ruff, mypy, bandit, pip-audit.
- Frontend: React 18 + TypeScript + Vite + Tailwind (existing) + **Cytoscape.js** (keep 3D view as secondary).
- Storage: Parquet + DuckDB (analytics), SQLite (users, cases, notes, audit).
- Memory: never materialise full datasets as Python objects; Polars lazy / DuckDB / chunked reads; 1M-transaction pipeline within 16 GB (Docker given \~12 GB); report measured time and peak RAM per stage.

---

# 6. DATA

## 6.1 Canonical record (the format judges will most likely use)

`timestamp` (ISO-8601 → UTC), `src_ip`, `dst_ip`, `src_port`, `dst_port`, `txid`, `input_addresses[]`, `output_addresses[]`, `input_amounts[]`, `output_amounts[]`, `fee`, `script_type` ∈ {P2PKH, P2SH, P2WPKH, P2WSH, P2TR}, `geo_country`, `asn` (optional; filled by GeoIP). Keep the aliases accepted by `loader.py`. Lists may be JSON arrays, `;`/`|`/`,` strings, or repeated XML elements. **Ingestion of this canonical format must be flawless in CSV, JSON and XML.**

## 6.2 Normalised tables (Parquet, zstd)

`transactions`, `wallets`, `network_observations`, `tx_inputs`, `tx_outputs`, `rejected` (line, txid, error, source SHA-256), `correlations`, `ip_enrichment(ip, country, asn, as_org, source)`.

## 6.3 Synthetic generator

Extend `scripts/generate_dataset.py`: `--n-tx --seed --profile normal|sparse|adversarial`, outputs CSV/JSON/XML, hidden `ground_truth.json`. Scenarios: normal users/merchants/exchange hubs with diurnal patterns, peeling chains, rapid multi-hop, burst fan-out, fan-in, network-correlated (shared ASN/Tor-like), **CoinJoin-like**, ransomware collection→consolidation. **sparse:** ≈70–80% of wallets appear in only 1–2 transactions. **adversarial:** amount jitter, randomised timing, broken peeling chains with decoys, VPN/shared-IP noise, mixing before cash-out. IP ranges must match the GeoIP fallback table.

## 6.4 REAL datasets (already placed by the user — inspect, never guess)

Host folders (git-ignored, never committed, never modified, mounted read-only in Docker):

- `backend/data/external/elliptic/` — **Elliptic** (expected `elliptic_txs_features.csv`, `elliptic_txs_classes.csv`, `elliptic_txs_edgelist.csv`; transaction-level; licit/illicit/unknown; 49 time steps; no addresses/IPs).
- `backend/data/external/bitcoinheist/BitcoinHeistData.csv` — **BitcoinHeist** (address-level; expected columns like `address, year, day, length, weight, count, looped, neighbors, income, label`; `white` = non-ransomware; \~230 MB).
- `backend/data/external/babd13/` — **BABD-13** (real files now present: address-level labels, 13 behaviour types, \~148 features). **Required, do not skip.**
- Optional `backend/data/external/elliptic_plus_plus/` if present.
- **First action for each dataset: list files, print columns, dtypes, row counts, label distribution, time coverage into `docs/data_audit/<dataset>.md`. Derive mappings only from what you actually see; never from names in this file.**
- Real datasets contain **no IP/port/ASN**. Any network layer on real data is a **simulated overlay** with documented assumptions (relay-delay distribution, shared-infrastructure probability, Tor/VPN noise), stored separately, flagged `simulated=true`, data source `real_plus_simulated_network`.

---

# 7. TECHNICAL SPECIFICATION

## 7.1 Wallet features (`ml/features.py`)

Keep the 24 `NUMERICAL_FEATURE_NAMES` required by `verify_phase4.py`. Extend to ≈40, no NaN/Inf: transaction/input/output counts, volumes, degree, counterparty count, mean/std amounts, in/out ratio, activity duration, mean time gap, burstiness, amount-fragmentation, round-amount ratio, change-output ratio, fee-rate z-score, script-type entropy, unique IP/ASN/country counts, network-observation count, night-activity ratio, first-seen hour, cluster size/volume, pattern memberships (peeling, CoinJoin, fan-in, fan-out), propagated risk, min hops to seed, neighbour anomaly mean/max, shared-ASN neighbour count. Use Polars/DuckDB, never Python loops over millions of rows.

## 7.2 Detectors (`ml/patterns.py`)

Peeling chain (successive dominant-output reuse + small peel output; min length default 4; output chain id, length, txids, peeled total, confidence); CoinJoin-like (≥N inputs from distinct addresses, ≥2 equal-value outputs; participants + confidence); rapid multi-hop, fan-in, fan-out, burst (time-bounded). Thresholds in config. Always return structured evidence, never a bare boolean.

## 7.3 Clustering (`ml/clustering.py`)

Common-input-ownership via union-find over `tx_inputs`, **CoinJoin-like transactions excluded**, optional change-address heuristic with its own confidence, cluster profiles, graph-embedding refinement (spectral/random-walk with numpy/sklearn) used only for "similar entity" suggestions labelled inferred. Re-enable `/api/clusters`; make `tests/test_clustering*.py` pass.

## 7.4 Models (`ml/anomaly.py`, `supervised.py`, `risk.py`, `propagation.py`)

1. Isolation Forest (random\_state=42) + a second unsupervised detector; report agreement; percentile-calibrated scores.
2. Supervised XGBoost on wallet features; labels from `ground_truth.json` (training/eval only); **time-aware split + cluster-grouped split**; `scale_pos_weight`; probability calibration on a separate slice; `model_card.json` (data SHA-256, params, seed, features, date, metrics, model-file SHA-256).
3. Risk propagation from `config/seed_wallets.json`: per-hop decay (0.5), edge-type weights (direct > inferred > contextual), confidence floor, hop cap 3, cap on influence through hub nodes.
4. Priority 0–100 = documented weighted blend (calibrated probability, anomaly percentile, pattern flags, propagated risk); **confidence** is a separate value (detector agreement + evidence quality); tiers CRITICAL/HIGH/MEDIUM/LOW.

## 7.5 Explainability & evidence (`ml/explain.py`, `evidence.py`)

SHAP `TreeExplainer` on top-K alerts only (default 2000), top-8 signed contributions stored; Isolation Forest explained by per-feature percentile deviation (labelled as such). **Evidence ledger** in three groups (Behavioural, Structural, Network/Contextual); item `{id, group, statement, value, baseline, evidence_type: direct|inferred|contextual, source_txids[], confidence}`. **Evidence sufficiency** 0–1 (LOW/MEDIUM/HIGH) from tx count, history span, feature coverage, network coverage — documented, unit-tested. Blind-spot report (VPN/Tor-masked IP, CoinJoin ambiguity, no external labels, exchange customers unknown). Risk-change explanation between runs.

## 7.6 Sparse-evidence engine (`ml/sparse.py`) — the differentiator

Transaction DNA fingerprint for 1–2-transaction wallets and similarity to labelled-pattern centroids; evidence-bounded expansion when sufficiency is LOW (max 2 hops, max 150 nodes, neighbours ranked by edge-type weight × time decay × neighbour priority × shared-infrastructure bonus; stop when change < ε; log nodes inspected, useful evidence, efficiency); counterfactual check (remove top-k edges/signals, report delta, flag fragile leads); next-best investigative action with justification. All outputs labelled "investigative lead, not proof".

## 7.7 Correlation (`correlate/`)

Order: exact txid → as-of time window (±N s, configurable) → shared IP/ASN within window. Each link stores rule name/version, window, timestamp, evidence type, confidence, direct/inferred. First-seen-relay is an *indicator* with a confidence cap and VPN/Tor/shared-IP caveat. Persist `correlations.parquet`; the graph builder consumes typed edges.

## 7.8 Real-data benchmark track (`scripts/external/`, `ml/realdata/`)

One **adapter** and one train/eval script per dataset. These models are benchmarks and are **not** wired into the wallet alert pipeline; they prove the method on real labels.

- **Elliptic (transaction-level):** use the dataset's time steps; train on early steps, test on later (standard: train ≤ step 34, test 35–49); exclude `unknown` from training and metrics; XGBoost + simple baseline (logistic regression/random forest); PR-AUC, illicit-class precision/recall/F1, Precision@K; per-time-step performance and a note on any collapse after dark-market shutdowns.
- **BitcoinHeist (address-level):** binary (`white` vs any ransomware) and per-family; split by `year`; imbalance via `scale_pos_weight` and PR-AUC; SHAP on the real model; per-family recall; chunked read.
- **BABD-13:** binary illicit/licit and 13-class; time-aware split if timestamps exist, else stratified with leakage notes; per-class precision/recall; SHAP summary.
- Compare each against a trivial baseline; fixed seeds; write `data/analysis/real_eval_<dataset>.json` and `docs/real_data_results.md`. State that real-data scores reflect public labels, possible sampling bias, and say nothing about field performance.

## 7.9 Evaluation (`scripts/evaluate.py`)

Outputs `data/analysis/evaluation_report.json` + `docs/evaluation.md`: PR-AUC, Precision@K, Recall@K, F1, FPR, calibration; **sparse-wallet metrics separately**; adversarial degradation; baseline vs full; ablations (no propagation / expansion / network features); expansion efficiency; scale benchmark (100K/1M/5M if RAM allows: time, peak RAM, API latency); reproducibility hash test. `/api/model/metrics` reads these files; remove all hardcoded values (grep `0.962`, `0.931`, `0.968`, `0.925`, `0.928`).

---

# 8. API CONTRACT

Keep existing routes working; add: `POST /api/auth/login`, `GET /api/auth/me`, admin user routes; `POST /api/datasets/upload` (csv|json|xml), `GET /api/datasets/status|rejected`; `GET /api/stats`; `POST /api/analysis/run`, `GET /api/analysis/status`; `GET /api/alerts` (limit, offset, min\_risk\_score, risk\_level, sufficiency, pattern), `GET /api/alerts/{id}`; `GET /api/investigations/{wallet}`, `POST /api/investigations/{wallet}/expand`; `GET /api/correlations/{wallet}`; `GET /api/clusters`, `/api/clusters/{id}`, `/api/clusters/wallet/{address}`; `GET /api/patterns?type=`; `GET /api/graph/stats|search|path|subgraph/{id}|entity/{id}` (hops, max\_nodes, edge\_types, time window); `GET /api/model/metrics|features|card`, `GET /api/model/real-data`; `/api/cases` CRUD, notes, decisions, `POST /api/cases/{id}/export`; `GET /api/audit`, `GET /api/audit/verify` (admin). All responses are Pydantic models; update `frontend/src/lib/api.ts`. Every lead carries `provenance {dataset_sha256, parser_version, model_version, rule_version, run_id, run_at, data_source}`.

---

# 9. QUALITY BAR

Unit tests: each parser incl. malformed rows in all three formats, GeoIP + fallback, correlation windows, union-find clustering (CoinJoin exclusion), detectors on hand-built fixtures, feature calculations with known answers, sufficiency formula, propagation caps, counterfactual, determinism hash, ground-truth non-leakage, every S17 item. Integration: upload → analyse → alerts → detail → expand → case → PDF via `TestClient`, and the same inside Docker. Frontend: lint, build, Playwright/Vitest smoke. Coverage ≥ 70% on `app/ml`, `app/pipeline`, `app/correlate`, `app/security`. Performance targets (report actuals): alerts list < 500 ms, ≤150-node subgraph < 1 s, detail < 500 ms on the 1M-tx dataset.

---

# 10. DEFINITION OF DONE

On a Windows machine with Docker Desktop and **no internet**, a user can: run `docker compose up --build` (or load the offline bundle) → create the admin → log in → import CSV, JSON and XML → see validation/quarantine → run analysis → browse ranked alerts with confidence → open an alert and see SHAP, three evidence groups, sufficiency, blind spots, provenance → open a one-transaction wallet and see bounded expansion, counterfactual and next action → explore a bounded Cytoscape graph, clusters and peeling/CoinJoin patterns → create a case, annotate, export a hashed PDF → view computed metrics with synthetic and real-data (Elliptic, BitcoinHeist, BABD-13) results in separate labelled tables → verify the audit chain → reproduce identical results on rerun. No fake data in any live view; all security tests pass; every phase gate passed and merged.

---

# 11. START

Do only the phase named in the kickoff message. Follow Section 1 exactly: read this file and `docs/PHASES.md`, plan, branch, implement, test, report, merge only if green, tag. Then stop and wait.
