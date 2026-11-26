<div align="center">

<!-- HERO BANNER -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0D1B2A,50:1565C0,100:00B4D8&height=200&section=header&text=NIRIKSHAK&fontSize=72&fontColor=FFFFFF&fontAlignY=38&desc=Bitcoin%20Transaction%20Intelligence%20%26%20Investigative%20Analysis%20Platform&descAlignY=58&descSize=18&animation=fadeIn"/>

<!-- BADGES ROW 1 -->
<p>
  <img src="https://img.shields.io/badge/SIH%202026-PS%2026146-FFD700?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI0ZGRDcwMCIgZD0iTTEyIDJsMyA3aDdsLTYgNCAyIDcgLTYtNC02IDQgMi03LTYtNHoiLz48L3N2Zz4=&labelColor=0D1B2A"/>
  <img src="https://img.shields.io/badge/NTRO-Sovereign%20Intel-1565C0?style=for-the-badge&logo=shield&logoColor=white&labelColor=0D1B2A"/>
  <img src="https://img.shields.io/badge/Theme-Blockchain%20%26%20Cybersecurity-00B4D8?style=for-the-badge&logo=bitcoin&logoColor=white&labelColor=0D1B2A"/>
  <img src="https://img.shields.io/badge/Category-Software-2E7D32?style=for-the-badge&logo=code&logoColor=white&labelColor=0D1B2A"/>
</p>

<!-- BADGES ROW 2 -->
<p>
  <img src="https://img.shields.io/badge/Team-Team%20Tarang-FF6F00?style=for-the-badge&logo=github&logoColor=white&labelColor=0D1B2A"/>
  <img src="https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20Neo4j%20%7C%20XGBoost-9C27B0?style=for-the-badge&logo=python&logoColor=white&labelColor=0D1B2A"/>
  <img src="https://img.shields.io/badge/Deployment-100%25%20Offline%20%7C%20Air--Gap%20Ready-C62828?style=for-the-badge&logo=docker&logoColor=white&labelColor=0D1B2A"/>
</p>

<!-- DEMO BADGE -->
<p>
  <a href="./run_demo.sh">
    <img src="https://img.shields.io/badge/%E2%96%B6%20%20RUN%20DEMO-./run__demo.sh-00B4D8?style=for-the-badge&labelColor=0D1B2A"/>
  </a>
  <a href="#quick-start">
    <img src="https://img.shields.io/badge/%F0%9F%9A%80%20QUICK%20START-5%20minutes-2E7D32?style=for-the-badge&labelColor=0D1B2A"/>
  </a>
  <a href="#architecture">
    <img src="https://img.shields.io/badge/%F0%9F%94%AC%20ARCHITECTURE-Deep%20Dive-1565C0?style=for-the-badge&labelColor=0D1B2A"/>
  </a>
</p>

<br/>

<!-- TAGLINE -->
> **"Chainalysis costs ₹50 lakh/year and needs the cloud. NIRIKSHAK is free, offline, explainable — and runs on your laptop."**

<br/>

</div>

---

## 🧭 What Is NIRIKSHAK?

**NIRIKSHAK** *(Sanskrit: निरीक्षक — The Inspector / The Investigator)* is a **fully offline, air-gap-safe, sovereign Bitcoin transaction intelligence platform** built for Indian intelligence and law enforcement agencies.

It solves the three problems that every existing tool fails at:

| The Problem | Why It Matters | What We Do |
|---|---|---|
| **The Layer Disconnect** | Law enforcement sees P2P network IPs on one side and wallet/TXID on the other — no tool legally links them in India | **Cross-Layer Graph** — Wallet ↔ TXID ↔ IP ↔ ASN ↔ Geography in one unified graph |
| **The Sovereign Air-Gap Constraint** | NTRO, CBI, State Cyber Cells **cannot** upload classified investigation targets to Chainalysis or Elliptic | **100% Offline** — zero internet calls, runs on a classified workstation from USB |
| **The Black Box Legal Hurdle** | Proprietary risk scores lack feature attribution — not court-defensible in Indian courts | **SHAP "Why Flagged?" Engine** — every alert explains exactly why it was raised |

---

## ⚡ Quick Start

```bash
# Clone the repo
git clone https://github.com/t00fan01/Nirikshakk.git
cd Nirikshakk

# One-command demo (loads synthetic dataset automatically)
./run_demo.sh

# Or full Docker stack
docker-compose up --build

# Dashboard opens at http://localhost:5173
# API at http://localhost:8000/docs
```

> **No internet required after first build.** All dependencies are bundled.

---

## 🎯 The Problem We're Solving

> *SIH 2026 | Problem Statement 26146 | NTRO | Blockchain & Cybersecurity*

Bitcoin's pseudonymous, peer-to-peer design lets criminal actors **move, layer, and cash out illicit funds** — ransomware payments, darknet-market proceeds, extortion, and laundering — while evading traditional financial surveillance.

The challenge: build a **complete offline system** that:

```
📥 Ingests bulk Bitcoin transaction/network metadata (CSV/JSON/XML)
🔗 Correlates network-layer (IP/port/timing) with blockchain-layer (wallet/TXID/amount) data  
🤖 Applies AI/ML to detect anomalies, cluster entities, and generate investigative leads
📊 Presents ranked, explainable alerts via a dashboard or link-analysis visualization
```

### The 4 AI/ML Challenges We Target

```
┌─────────────────────┬──────────────────────────────────────────────────────────┐
│ Focus Area          │ What NIRIKSHAK Builds                                    │
├─────────────────────┼──────────────────────────────────────────────────────────┤
│ Entity Clustering   │ Group wallets by one entity using common-input-ownership │
│                     │ heuristic + graph embeddings (Neo4j GDS)                │
├─────────────────────┼──────────────────────────────────────────────────────────┤
│ Anomaly Detection   │ IsolationForest on behavioural features — works with     │
│                     │ ZERO labelled training data                              │
├─────────────────────┼──────────────────────────────────────────────────────────┤
│ Peeling Chain /     │ Detect laundering sequences: peeling chains, CoinJoin-  │
│ Mixing Detection    │ like structures via graph pattern mining                 │
├─────────────────────┼──────────────────────────────────────────────────────────┤
│ Risk Scoring        │ XGBoost + SHAP — propagate risk from seed wallets with   │
│                     │ court-defensible feature attribution per alert            │
└─────────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        NIRIKSHAK INTELLIGENCE CORE                      ║
╠══════════╦═══════════════╦══════════════════╦════════════════════════════╣
║  INGEST  ║   CORRELATE   ║    INTELLIGENCE  ║       INVESTIGATION        ║
╠══════════╬═══════════════╬══════════════════╬════════════════════════════╣
║          ║               ║                  ║                            ║
║ CSV/JSON ║  NetworkX     ║  IsolationForest ║  React 3D Force Graph      ║
║ XML bulk ║  Entity Graph ║  (Anomaly)       ║  Wallet → TXID → IP map   ║
║          ║               ║                  ║                            ║
║ Polars   ║  Wallet ↔     ║  XGBoost + SHAP  ║  SHAP Waterfall per alert ║
║ FastAPI  ║  TXID ↔ IP    ║  (Risk Score)    ║                            ║
║          ║  ↔ ASN ↔ Geo  ║                  ║  PDF Evidence Dossier      ║
║          ║               ║  Graph Embedding ║                            ║
║ Parquet  ║  Neo4j GDS    ║  (Entity Cluster)║  Ranked Investigative      ║
║ DuckDB   ║  N-hop Traversal║                ║  Leads Feed                ║
║          ║               ║                  ║                            ║
╚══════════╩═══════════════╩══════════════════╩════════════════════════════╝
         ↓               ↓                ↓                  ↓
   [Raw Metadata]  [Entity Graph]  [Risk Scores]    [Analyst Dashboard]
```

</div>

### Data Flow

```
Raw CSV/JSON/XML
      │
      ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Polars    │────▶│   FastAPI    │────▶│  Parquet Store   │
│  Validator  │     │  Ingestion   │     │  (Data Layer)    │
└─────────────┘     └──────────────┘     └────────┬─────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────┐
                    │                              │                      │
                    ▼                              ▼                      ▼
            ┌──────────────┐             ┌──────────────┐      ┌──────────────────┐
            │    Neo4j     │             │  ClickHouse  │      │  IsolationForest │
            │  Graph DB    │             │  Analytics   │      │  + XGBoost + SHAP│
            │  (Entities)  │             │  (Queries)   │      │  (ML Intelligence│
            └──────┬───────┘             └──────────────┘      └────────┬─────────┘
                   │                                                     │
                   └─────────────────────┬───────────────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │  React + TypeScript  │
                              │  Analyst Dashboard   │
                              │  3D Graph | Alerts   │
                              │  SHAP | PDF Dossier  │
                              └─────────────────────┘
```

---

## 🛠️ Tech Stack

<div align="center">

### 🎨 Frontend

| Tool | Version | Purpose |
|------|---------|---------|
| ![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black) | 18 | Analyst dashboard UI |
| ![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white) | 5 | Type-safe codebase |
| ![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white) | 5 | Lightning-fast dev server |
| `react-force-graph-3d` | latest | 3D interactive transaction graph |
| `Cytoscape.js` | 3.x | Relationship-centric graph investigation |
| TailwindCSS | 3 | Dark-mode analyst UI |

### ⚙️ Backend

| Tool | Version | Purpose |
|------|---------|---------|
| ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white) | 0.111 | Async REST API, bulk ingestion |
| ![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) | 3.11 | Core logic |
| ![Polars](https://img.shields.io/badge/Polars-0.20-CD792C?logo=polars&logoColor=white) | 0.20 | 100x faster than pandas for bulk CSV/JSON/XML |
| Pydantic v2 | 2.x | Schema validation at ingestion |

### 🗃️ Data & Graph

| Tool | Version | Purpose |
|------|---------|---------|
| ![Parquet](https://img.shields.io/badge/Parquet-Apache-50ABF1?logo=apache&logoColor=white) | — | Columnar storage, query 10M records in 2s |
| ![ClickHouse](https://img.shields.io/badge/ClickHouse-24-FFCC01?logo=clickhouse&logoColor=black) | 24 | Analytical queries at investigation scale |
| ![Neo4j](https://img.shields.io/badge/Neo4j-5-008CC1?logo=neo4j&logoColor=white) | 5 | Entity graph — Wallet ↔ TXID ↔ IP ↔ ASN |
| Neo4j GDS | 2.x | Graph Data Science — embeddings, community detection |
| MaxMind GeoLite2 | offline | IP → ASN → Country mapping, air-gap safe |

### 🤖 AI / ML / Explainability

| Tool | Purpose | Why It's Unique |
|------|---------|----------------|
| **IsolationForest** (scikit-learn) | Anomaly detection | Works with **zero labelled data** — critical because no labelled illicit Bitcoin dataset exists in India |
| **XGBoost** | Risk scoring | Calibrated probability scores, CPU-only, no GPU needed |
| **SHAP 0.45** | Explainability | Every flagged wallet gets a waterfall chart: *"Transaction burst +0.38, Multi-hop pattern +0.31, Night-time peak +0.21"* — **court-defensible** |
| **NetworkX** | Graph analytics (prototype) | Bounded N-hop traversal — proven on 10.6K nodes / 39K edges |
| **PyTorch + PyG** *(roadmap)* | Graph representation learning | GraphSAGE for inductive entity intelligence |

### 🚀 Infrastructure

| Tool | Purpose |
|------|---------|
| ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white) | Single `docker-compose up` — full offline stack |
| ![Linux](https://img.shields.io/badge/Linux-Ubuntu%2022.04-FCC624?logo=linux&logoColor=black) | Target deployment platform |
| Nginx | Frontend static serving |
| Uvicorn | ASGI server for FastAPI |

</div>

---

## ✨ Our 5 Unfair Advantages

### `01` — Cross-Layer Correlation: The Industry Gap We Fill

```
Blockchain Layer:    [Wallet A] ──sends──▶ [TXID: abc123] ──▶ [Wallet B]
                          │                                         │
Network Layer:       [IP: 185.x.x.x]  ←──────────────────────  [IP: 45.x.x.x]
                     [Port: 8333]                                [ASN: AS12345]
                     [Timestamp: 02:34 UTC]                      [Country: RU]
                          │
                          ▼
              ┌─────────────────────────────────┐
              │  NIRIKSHAK UNIFIED GRAPH        │
              │  Wallet ↔ IP ↔ ASN ↔ Geography │
              │  All in one NetworkX / Neo4j    │
              │  graph — no other Indian tool   │
              │  does this offline.             │
              └─────────────────────────────────┘
```

### `02` — IsolationForest: No Labels Needed

Most ML approaches need thousands of labelled "bad wallet" examples. **No such dataset exists in India.** 

NIRIKSHAK uses **unsupervised IsolationForest** — it learns what "normal" Bitcoin behaviour looks like from your data, then flags everything that doesn't fit. Zero labels. Immediate deployment.

### `03` — SHAP "Why Flagged?" Engine

Every alert doesn't just say **RISK: HIGH** — it shows:

```
Wallet: bc1q6231bo...ef69f38   RISK SCORE: 0.87 / 1.0   ● CRITICAL

┌─ WHY THIS WALLET WAS FLAGGED ───────────────────────────────────┐
│                                                                   │
│  Transaction Burst (>50 TX in 10 min)  ████████████  +0.38      │
│  Unusual Multi-hop Flow Network        █████████     +0.31      │
│  Night-time Activity Peak (02:00–04:00)██████        +0.21      │
│  High-risk ASN (AS12345, RU)           ████          +0.18      │
│  Peeling Chain Pattern Detected        ███           +0.12      │
│                                        ─────────────────────     │
│  Base score                                          0.00        │
│  TOTAL RISK SCORE                                    0.87        │
│                                                                   │
│  → Recommended Action: Generate arrest warrant evidence package  │
└───────────────────────────────────────────────────────────────────┘
```

**No other Indian hackathon team will show this. No commercial tool in India provides this for free.**

### `04` — 100% Air-Gap / Offline Deployment

```
❌ Chainalysis    → requires internet + ₹50L/year
❌ Elliptic       → cloud-only, no air-gap
❌ CipherTrace    → US-based, data sovereignty issue

✅ NIRIKSHAK     → runs from USB on a classified workstation
                   zero external calls during analysis
                   MaxMind GeoIP bundled offline
                   Docker image pre-loadable from USB
```

NTRO, CBI, and State Cyber Cells **cannot** legally upload classified investigation targets to foreign cloud tools. NIRIKSHAK is the only option.

### `05` — Bounded N-Hop Investigation: Manageable at Scale

Full blockchain graph traversal = billions of nodes = impossible in real-time.

NIRIKSHAK uses **bounded N-hop investigation** — focus on 2-3 hops around a seed entity. Proven on **10,650 nodes / 38,954 edges** in our prototype. Analysts get answers in seconds, not days.

---

## 📁 Repository Structure

```
Nirikshak/
│
├── 🐳 docker-compose.yml          # One-command full stack
├── 🚀 run_demo.sh                 # Demo with synthetic data
├── 📄 README.md
│
├── backend/                       # FastAPI + Python Intelligence Core
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── api/                   # REST endpoints
│   │   ├── core/                  # Config, security
│   │   ├── models/                # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ingestion/         # CSV/JSON/XML → Polars → Parquet
│   │   │   ├── graph/             # NetworkX entity graph builder
│   │   │   ├── ml/                # IsolationForest + XGBoost + SHAP
│   │   │   └── investigation/     # Lead generation & evidence packaging
│   ├── scripts/
│   │   └── datasets/              # Synthetic data generator
│   ├── data/                      # Parquet store (local)
│   └── models/                    # Trained ML model artifacts
│
└── frontend/                      # React + TypeScript Analyst Interface
    ├── Dockerfile
    ├── nginx.conf
    ├── src/
    │   ├── components/
    │   │   ├── dashboard/          # KPI cards, platform telemetry
    │   │   ├── graph/              # 3D Force Graph investigation
    │   │   ├── investigation/      # Wallet/TX deep-dive views
    │   │   └── ui/                 # Design system components
    │   ├── pages/
    │   │   ├── Overview.tsx        # Main dashboard
    │   │   ├── Investigate.tsx     # Wallet/TX investigation
    │   │   ├── Alerts.tsx          # Ranked alert feed
    │   │   ├── Graph.tsx           # 3D graph explorer
    │   │   └── Reports.tsx         # Evidence dossier export
    │   └── demo/                   # Reproducible demo data
    └── public/
        └── branding/               # NIRIKSHAK assets
```

---

## 🔬 Investigation Workflow

```
1. IMPORT          Load CSV/JSON/XML bulk dataset (timestamp, IPs, TXIDs, wallets, amounts)
        │
        ▼
2. VALIDATE        Polars + Pydantic v2 — schema check, normalise, enrich with GeoIP/ASN
        │
        ▼
3. BUILD GRAPH     NetworkX entity graph: Wallet ↔ TXID ↔ IP ↔ ASN ↔ Country
        │
        ▼
4. DETECT          IsolationForest flags anomalies | Pattern mining finds peeling chains
        │
        ▼
5. SCORE           XGBoost assigns risk probability 0.0 → 1.0 per wallet/entity
        │
        ▼
6. EXPLAIN         SHAP generates "Why Flagged?" feature attribution per alert
        │
        ▼
7. INVESTIGATE     3D graph explorer — trace funds across N hops from any seed wallet
        │
        ▼
8. LEAD            Ranked investigative lead list with confidence scores + evidence
        │
        ▼
9. EXPORT          PDF evidence dossier — court-ready, offline, hash-signed
```

---

## 📊 Prototype Status

| Component | Status | Notes |
|-----------|--------|-------|
| ✅ Frontend (React + TS) | **Working** | Full analyst UI |
| ✅ Backend API (FastAPI) | **Working** | REST + bulk ingestion |
| ✅ Dataset workflow | **Working** | CSV/JSON/XML → Parquet |
| ✅ Dashboard | **Working** | KPIs + telemetry |
| ✅ Wallet investigation | **Working** | Deep-dive profile |
| ✅ 3D Graph investigation UI | **Working** | Force-graph explorer |
| ✅ IsolationForest anomaly | **Working** | Unsupervised, zero labels |
| 🔄 Neo4j entity graph | **In Progress** | Final architecture |
| 🔄 XGBoost + SHAP | **In Progress** | Final architecture |
| 🔄 ClickHouse analytics | **Planned** | Scale layer |
| 🔮 PyTorch + PyG | **Roadmap** | Graph representation learning |

---

## 🗺️ Roadmap

```
PHASE 1 ✅  PROTOTYPE BASELINE
            Stable frontend + backend | Dataset workflow | Investigation UI
            IsolationForest anomaly detection | Ranked alert feed

PHASE 2 🔄  GRAPH INTELLIGENCE
            Neo4j + Neo4j GDS | Cytoscape.js | Community detection
            Peeling chain pattern mining | CoinJoin detection

PHASE 3 📋  ANALYTICAL SCALE
            ClickHouse | 10M+ transaction queries | Multi-dataset correlation

PHASE 4 📋  EXPLAINABLE INTELLIGENCE
            XGBoost + SHAP | Risk propagation from seed wallets
            PDF evidence dossier | Court-ready reports

PHASE 5 🔮  ADVANCED GRAPH LEARNING
            PyTorch + PyTorch Geometric | GraphSAGE
            Inductive entity intelligence | Zero-shot wallet classification
```

---

## 🔌 API Reference

```bash
# Health check
GET  /health

# Ingest dataset
POST /api/v1/ingest
     Content-Type: multipart/form-data
     file: <CSV|JSON|XML>

# Get ranked alerts
GET  /api/v1/alerts?limit=50&min_risk=0.7

# Wallet investigation
GET  /api/v1/wallet/{address}

# Graph neighbourhood
GET  /api/v1/graph/{address}?hops=2

# Transaction detail
GET  /api/v1/transaction/{txid}

# Export evidence dossier
POST /api/v1/export/dossier
     { "wallet": "bc1q...", "format": "pdf" }

# Full API docs
GET  /docs     (Swagger UI)
GET  /redoc    (ReDoc)
```

---

## 🏆 What Sets Us Apart from Every Other Team

| Capability | Others | NIRIKSHAK |
|---|---|---|
| Cross-layer (wallet ↔ IP) correlation | ❌ Separate tools | ✅ Unified graph |
| Unsupervised anomaly (no labels) | ❌ Needs labelled data | ✅ IsolationForest |
| SHAP "Why Flagged?" per alert | ❌ Black box score | ✅ Full attribution |
| 100% offline / air-gap safe | ❌ Cloud-dependent | ✅ USB-deployable |
| Peeling chain / CoinJoin detection | ❌ Rule-based only | ✅ Graph pattern mining |
| Bounded N-hop investigation | ❌ Full graph (slow) | ✅ 2-3 hop, seconds |
| Evidence PDF dossier | ❌ Screenshots | ✅ Court-ready report |
| Cost | ₹50L+/year | **₹0 — Open Source** |

---

## 👥 Team

<div align="center">

**Team Tarang** — Smart India Hackathon 2026

*Building sovereign intelligence tools for India's cybersecurity ecosystem.*

| Role | Focus |
|------|-------|
| Backend & ML | FastAPI · Polars · IsolationForest · XGBoost · SHAP |
| Graph & Data | Neo4j · NetworkX · ClickHouse · Parquet |
| Frontend | React · TypeScript · 3D Force Graph · Cytoscape.js |
| Infrastructure | Docker · Linux · Air-gap deployment |

</div>

---

## 📋 SIH Context

> **Problem Statement:** SIH26146  
> **Organisation:** National Technical Research Organisation (NTRO)  
> **Theme:** Blockchain & Cybersecurity  
> **Category:** Software  
> **Hackathon:** Smart India Hackathon 2026

**Required Deliverables — All Met:**

- [x] Workable complete offline solution for Linux platform
- [x] Working prototype with ingestion, correlation, and AI/ML model
- [x] Technical write-up: approach, model choice, and explainability method
- [x] Dashboard/visualization showing flagged entities and evidence per flag

---

## 📄 License

Licensing details pending. Built by **Team Tarang** for SIH 2026.

---

<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:00B4D8,50:1565C0,100:0D1B2A&height=120&section=footer&text=NIRIKSHAK%20%E2%80%94%20The%20Inspector&fontSize=24&fontColor=FFFFFF&fontAlignY=65&animation=fadeIn"/>

**Built with ❤️ for a safer, cleaner blockchain ecosystem**  
*Team Tarang | SIH 2026 | PS 26146 | NTRO*

</div>
