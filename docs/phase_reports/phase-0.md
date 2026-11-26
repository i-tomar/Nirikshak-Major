# Phase 0 recovery report

27 November 2026 · Windows and Docker · **RED**

## What changed

- Merged hygiene from local main at b1154e0 into the phase branch at 32ebd44. AGENTS.md and docs/PHASES.md match main. DECISIONS.md includes the hygiene decision and the phase notes.
- Replaced the legacy Phase 3 verifier's stale volume and time expectations with independent CSV calculations. Kept the table counts, precision tolerance and separate storage and API assertions. Phase 5 calls the same regression.
- Added generic internal error responses with a server-generated request ID, logged the exception server-side, and removed exception text and filesystem paths from explicit router responses.
- Added runtime tests for redaction, CORS, default-disabled API documentation, and quoted, Unicode and overlong alert literals. Active SQL exploit-payload reproduction was not run.
- The check runner executes all requested stages in order, returns failure when a gate fails, and stops Compose in a finally block.

## Verification and measurements

| Revision | Source CSV SHA-256 | Transactions | Wallets | Network observations | Rejected | CSV output BTC | DuckDB output BTC |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline 0d06e64 | be9448ac22895089f0274ded4dc9b63100db0e4b17ac688faf5f7981a85ca937 | 5000 | 4915 | 5000 | 0 | 5216.56493532 | 5216.56493532 |
| Phase branch 32ebd44 | be9448ac22895089f0274ded4dc9b63100db0e4b17ac688faf5f7981a85ca937 | 5000 | 4915 | 5000 | 0 | 5216.56493532 | 5216.56493532 |

Baseline ran in a detached scratch Git worktree. Its package initializer was bypassed because it imports the missing app.ml package. Generator, loader, transaction schema, normalizer and storage were unmodified. Seed 42, 5,000 transactions, 1,200 source wallet pool, 350 IP pool, 5% anomaly target, seven days, fixed 2025-01-01 16:40 UTC. Independent summation used Python CSV, JSON and Decimal. The earlier volume expectation of 5174.20608283 belongs to an unavailable fixture.

- Windows pytest: 47 passed in 24.25s. Docker pytest: 47 passed in 6.52s. Zero skips or failures in either. The three new tests also passed independently after the fixture isolation change.
- Legacy verify_phase1.py through verify_phase5.py exited 0. Verify Phase 2's default probe targets port 8000 and warns when the server is absent. The same live verifier passed separately against a disposable Docker backend bound to 127.0.0.1:18080. Output: Live Upload Response PASSED, Total Rows 5000, Valid 5000, Rejected 0.
- Docker seed: 5,000 transactions, 4,915 wallets, 10,650 graph nodes. The graph verifier measured 38,887 edges.
- Frontend build: 20.07s. ESLint returned zero errors and two hook dependency warnings. End-to-end peak RAM is unverified.

## Security checks and open gates

Bandit reported no issues. pip-audit found no known vulnerabilities. npm audit --omit=dev reported zero vulnerabilities. No HIGH or CRITICAL findings required an exception. Compose stopped both services, and docker compose ps --status running returned an empty list.

The full check exited 1 because Ruff reported 224 violations and mypy found 40 errors in 14 files. Examples include older typing syntax and import ordering for Ruff, and missing library stubs and incompatible annotations for mypy. No checks were suppressed. No existing pytest tests were weakened, skipped or removed. Untested exploit payloads and full runtime peak RAM remain unverified.

## Git state

Initial status was dirty on phase/0-recover-boot at d17f273. After the reviewed commits and main hygiene merge, git status --short --branch showed only the phase branch header. Final implementation commits are 223ac64 and cbf3f5d. Local main remains at b1154e0. No phase-0-done tag.

## Actual full-check output

Per-scenario ground-truth details were omitted from the captured output.

~~~~text
[Per-scenario ground-truth detail omitted]
      • rapid           : 24/30 ( 80.0%)
      • peeling_chain_0 :  9/17 ( 52.9%)
      • burst           :  6/90 (  6.7%)
      • tor             : 42/60 ( 70.0%)
      • fanin           :  5/45 ( 11.1%)
      • peeling_chain_1 :  8/17 ( 47.1%)
      • peeling_chain_2 :  8/17 ( 47.1%)
      • peeling_chain_3 :  8/17 ( 47.1%)
      • peeling_chain_4 :  8/17 ( 47.1%)
      • peeling_chain_5 :  8/17 ( 47.1%)
   [PASS] Offline evaluation metrics computed honestly.

======================================================================
PHASE 4 VERIFICATION SUITE SUCCESSFUL: ALL 8 TESTS PASSED!
======================================================================
+ D:\NirikshakM\.venv\Scripts\python.exe D:\NirikshakM\backend\scripts\verify_phase5.py
D:\NirikshakM\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  from starlette.testclient import TestClient as TestClient  # noqa
================================================================================
NIRIKSHAK AI — PHASE 5 VERIFICATION SUITE
SIH26146: Real Bitcoin Investigation Graph (NetworkX + API)
================================================================================

[1/24] Running Phase 1 Regression...
   [PASS] Phase 1 synthetic dataset & schema regression passed.

[2/24] Running Phase 2 Regression...
   [PASS] Phase 2 dataset ingestion & validation regression passed.

[3/24] Running Phase 3 Regression...
   [PASS] Phase 3 data normalization, Parquet & DuckDB regression passed.

[4/24] Running Phase 4 Regression...
   [PASS] Phase 4 feature engineering & risk engine regression passed.

[5/24] Verifying Graph Construction from Parquet Tables...
   [PASS] Graph compiled successfully: 10,650 nodes, 38,887 edges.

[6/24] Verifying Node Types...
   [PASS] Expected node types present: ['asn', 'country', 'ip', 'transaction', 'wallet']
          Wallets: 4915, Txs: 5000, IPs: 710, ASNs: 16, Countries: 9

[7/24] Verifying Edge Types...
   [PASS] Expected edge types present: ['counterparty', 'input', 'network_observation', 'output']
          Input: 5731, Output: 8600, Counterparty: 9314, Network Obs: 15242

[8/24] Verifying No Duplicate Transaction Nodes...
   [PASS] Exactly 5,000 unique transaction nodes exist (1:1 with transactions table).

[9/24] Verifying Wallet <-> Transaction Edge Consistency...
   [PASS] Wallet-Transaction input and output edge topologies verified.

[10/24] Verifying Transaction <-> IP Relationships...
   [PASS] Network observation edges correctly link tx to observed IPs: 65.159.226.86, 198.51.100.128.

[11/24] Verifying IP <-> ASN Relationships...
   [PASS] IP-ASN association edges verified.

[12/24] Verifying IP <-> Country Relationships...
   [PASS] IP-Country geolocation edges verified.

[13/24] Verifying Counterparty Heuristic Edges...
   [PASS] Counterparty heuristic edges generated correctly without O(N^2) explosion.

[14/24] Verifying Graph Construction Determinism...
   [PASS] Rebuilding graph yields 100% byte-for-byte deterministic structure.

[15/24] Verifying Local Graph Storage...
   [PASS] Local graph artifacts verified: json (14.38 MB), stats.json, graphml.

[16/24] Verifying Neighborhood Queries (1-hop, 2-hop)...
   [PASS] Neighborhood query works: 1-hop=19 nodes, 2-hop=100 nodes.

[17/24] Verifying Hop Limit Bounds (1 to 3)...
   [PASS] Hop limit correctly clamped between 1 and 3.

[18/24] Verifying Max Nodes Safety Cap...
   [PASS] max_nodes cap enforced (returned 15 <= 15).

[19/24] Verifying Search Engine...
   [PASS] Search successfully resolves wallets, txids, and IPs.

[20/24] Verifying Shortest Path Lookup...
   [PASS] Shortest path found between counterparties (length=1) with causal disclaimer.

[21/24] Verifying Phase 4 Risk Metadata Integration...
   [PASS] 4,915 wallet nodes contain validated Phase 4 risk scores and tiers.

[22/24] Verifying Ground Truth Protection...
   [PASS] Zero ground truth attributes leaked into the graph layer.

[23/24] Verifying Frontend Files are Untouched in Phase 5...
   [PASS] Zero frontend modifications detected.

[24/24] Verifying FastAPI HTTP Endpoints...
   [PASS] All /api/graph/* endpoints validated with 200 OK responses and proper 404 handling.

================================================================================
🎉 PHASE 5 VERIFICATION COMPLETE: ALL 24 TESTS PASSED!
================================================================================
+ D:\NirikshakM\.venv\Scripts\python.exe -m ruff check backend/app/graph/builder.py backend/app/main.py backend/app/ml/__init__.py backend/app/ml/analyzer.py backend/app/ml/anomaly.py backend/app/ml/clustering.py backend/app/ml/evidence.py backend/app/ml/features.py backend/app/ml/risk.py backend/app/pipeline/loader.py backend/app/pipeline/storage.py backend/app/routers/alerts.py backend/app/routers/analysis.py backend/app/routers/clusters.py backend/app/routers/datasets.py backend/app/routers/graph.py backend/app/routers/investigations.py backend/app/routers/models.py backend/app/schemas/analysis.py backend/app/schemas/clustering.py backend/scripts/seed_demo.py backend/scripts/verify_phase3.py backend/scripts/verify_phase5.py scripts/tasks.py backend/tests/test_phase0_security.py
I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\graph\builder.py:11:1
   |
 9 |   """
10 |
11 | / import logging
12 | |
13 | | from collections import defaultdict
14 | | from datetime import datetime, timezone
15 | | import json
16 | | from pathlib import Path
17 | | from typing import Any, Dict, List, Optional, Set, Tuple, Union
18 | | import duckdb
19 | | import networkx as nx
20 | | import polars as pl
21 | |
22 | | from app.pipeline.storage import (
23 | |     DEFAULT_STORAGE_DIR,
24 | |     get_parquet_paths,
25 | |     get_storage_dir,
26 | |     has_normalized_data,
27 | | )
   | |_^
28 |
29 |   DEFAULT_ANALYSIS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "analysis"
   |
help: Organize imports
   |
10 |
11 + import json
12 | import logging
   -
13 | from collections import defaultdict
14 | from datetime import datetime, timezone
   - import json
15 | from pathlib import Path
16 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
17 +
18 | import duckdb
19 | import networkx as nx
20 | import polars as pl
   -
21 | from app.pipeline.storage import (
   |

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> backend\app\graph\builder.py:17:1
   |
15 | import json
16 | from pathlib import Path
17 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
18 | import duckdb
19 | import networkx as nx
   |

UP035 `typing.List` is deprecated, use `list` instead
  --> backend\app\graph\builder.py:17:1
   |
15 | import json
16 | from pathlib import Path
17 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
18 | import duckdb
19 | import networkx as nx
   |

UP035 `typing.Set` is deprecated, use `set` instead
  --> backend\app\graph\builder.py:17:1
   |
15 | import json
16 | from pathlib import Path
17 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
18 | import duckdb
19 | import networkx as nx
   |

UP035 `typing.Tuple` is deprecated, use `tuple` instead
  --> backend\app\graph\builder.py:17:1
   |
15 | import json
16 | from pathlib import Path
17 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
18 | import duckdb
19 | import networkx as nx
   |

F401 [*] `typing.List` imported but unused
  --> backend\app\graph\builder.py:17:31
   |
15 | import json
16 | from pathlib import Path
17 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   |                               ^^^^
18 | import duckdb
19 | import networkx as nx
   |
help: Remove unused import: `typing.List`
   |
16 | from pathlib import Path
   - from typing import Any, Dict, List, Optional, Set, Tuple, Union
17 + from typing import Any, Dict, Optional, Set, Tuple, Union
18 | import duckdb
   |

F401 [*] `duckdb` imported but unused
  --> backend\app\graph\builder.py:18:8
   |
16 | from pathlib import Path
17 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
18 | import duckdb
   |        ^^^^^^
19 | import networkx as nx
20 | import polars as pl
   |
help: Remove unused import: `duckdb`
   |
17 | from typing import Any, Dict, List, Optional, Set, Tuple, Union
   - import duckdb
18 | import networkx as nx
   |

F401 [*] `app.pipeline.storage.DEFAULT_STORAGE_DIR` imported but unused
  --> backend\app\graph\builder.py:23:5
   |
22 | from app.pipeline.storage import (
23 |     DEFAULT_STORAGE_DIR,
   |     ^^^^^^^^^^^^^^^^^^^
24 |     get_parquet_paths,
25 |     get_storage_dir,
   |
help: Remove unused import
   |
22 | from app.pipeline.storage import (
   -     DEFAULT_STORAGE_DIR,
23 |     get_parquet_paths,
   -     get_storage_dir,
24 |     has_normalized_data,
   |

F401 [*] `app.pipeline.storage.get_storage_dir` imported but unused
  --> backend\app\graph\builder.py:25:5
   |
23 |     DEFAULT_STORAGE_DIR,
24 |     get_parquet_paths,
25 |     get_storage_dir,
   |     ^^^^^^^^^^^^^^^
26 |     has_normalized_data,
27 | )
   |
help: Remove unused import
   |
22 | from app.pipeline.storage import (
   -     DEFAULT_STORAGE_DIR,
23 |     get_parquet_paths,
   -     get_storage_dir,
24 |     has_normalized_data,
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:32:34
   |
32 | def get_analysis_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
   |                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
33 |     """Return analysis directory Path."""
34 |     return Path(custom_dir) if custom_dir else DEFAULT_ANALYSIS_DIR
   |
help: Convert to `X | None`
   |
31 |
   - def get_analysis_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
32 + def get_analysis_dir(custom_dir: Union[str, Path] | None = None) -> Path:
33 |     """Return analysis directory Path."""
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\graph\builder.py:32:43
   |
32 | def get_analysis_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
   |                                           ^^^^^^^^^^^^^^^^
33 |     """Return analysis directory Path."""
34 |     return Path(custom_dir) if custom_dir else DEFAULT_ANALYSIS_DIR
   |
help: Convert to `X | Y`
   |
31 |
   - def get_analysis_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
32 + def get_analysis_dir(custom_dir: Optional[str | Path] = None) -> Path:
33 |     """Return analysis directory Path."""
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:37:37
   |
37 | def has_analysis_data(analysis_dir: Optional[Union[str, Path]] = None) -> bool:
   |                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^
38 |     """Check if compiled Phase 4 analysis results exist on disk."""
39 |     adir = get_analysis_dir(analysis_dir)
   |
help: Convert to `X | None`
   |
36 |
   - def has_analysis_data(analysis_dir: Optional[Union[str, Path]] = None) -> bool:
37 + def has_analysis_data(analysis_dir: Union[str, Path] | None = None) -> bool:
38 |     """Check if compiled Phase 4 analysis results exist on disk."""
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\graph\builder.py:37:46
   |
37 | def has_analysis_data(analysis_dir: Optional[Union[str, Path]] = None) -> bool:
   |                                              ^^^^^^^^^^^^^^^^
38 |     """Check if compiled Phase 4 analysis results exist on disk."""
39 |     adir = get_analysis_dir(analysis_dir)
   |
help: Convert to `X | Y`
   |
36 |
   - def has_analysis_data(analysis_dir: Optional[Union[str, Path]] = None) -> bool:
37 + def has_analysis_data(analysis_dir: Optional[str | Path] = None) -> bool:
38 |     """Check if compiled Phase 4 analysis results exist on disk."""
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:47:22
   |
46 | # In-memory singleton cache to prevent rebuilding/reloading graph on every API call
47 | _MEMORY_GRAPH_CACHE: Optional[nx.DiGraph] = None
   |                      ^^^^^^^^^^^^^^^^^^^^
48 | _MEMORY_STATS_CACHE: Optional[Dict[str, Any]] = None
   |
help: Convert to `X | None`
   |
46 | # In-memory singleton cache to prevent rebuilding/reloading graph on every API call
   - _MEMORY_GRAPH_CACHE: Optional[nx.DiGraph] = None
47 + _MEMORY_GRAPH_CACHE: nx.DiGraph | None = None
48 | _MEMORY_STATS_CACHE: Optional[Dict[str, Any]] = None
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:48:22
   |
46 | # In-memory singleton cache to prevent rebuilding/reloading graph on every API call
47 | _MEMORY_GRAPH_CACHE: Optional[nx.DiGraph] = None
48 | _MEMORY_STATS_CACHE: Optional[Dict[str, Any]] = None
   |                      ^^^^^^^^^^^^^^^^^^^^^^^^
help: Convert to `X | None`
   |
47 | _MEMORY_GRAPH_CACHE: Optional[nx.DiGraph] = None
   - _MEMORY_STATS_CACHE: Optional[Dict[str, Any]] = None
48 + _MEMORY_STATS_CACHE: Dict[str, Any] | None = None
49 |
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\graph\builder.py:48:31
   |
46 | # In-memory singleton cache to prevent rebuilding/reloading graph on every API call
47 | _MEMORY_GRAPH_CACHE: Optional[nx.DiGraph] = None
48 | _MEMORY_STATS_CACHE: Optional[Dict[str, Any]] = None
   |                               ^^^^
help: Replace with `dict`
   |
47 | _MEMORY_GRAPH_CACHE: Optional[nx.DiGraph] = None
   - _MEMORY_STATS_CACHE: Optional[Dict[str, Any]] = None
48 + _MEMORY_STATS_CACHE: Optional[dict[str, Any]] = None
49 |
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:58:31
   |
58 | def get_graph_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
   |                               ^^^^^^^^^^^^^^^^^^^^^^^^^^
59 |     """Return graph directory Path, creating it if it does not exist."""
60 |     target_dir = Path(custom_dir) if custom_dir else DEFAULT_GRAPH_DIR
   |
help: Convert to `X | None`
   |
57 |
   - def get_graph_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
58 + def get_graph_dir(custom_dir: Union[str, Path] | None = None) -> Path:
59 |     """Return graph directory Path, creating it if it does not exist."""
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\graph\builder.py:58:40
   |
58 | def get_graph_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
   |                                        ^^^^^^^^^^^^^^^^
59 |     """Return graph directory Path, creating it if it does not exist."""
60 |     target_dir = Path(custom_dir) if custom_dir else DEFAULT_GRAPH_DIR
   |
help: Convert to `X | Y`
   |
57 |
   - def get_graph_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
58 + def get_graph_dir(custom_dir: Optional[str | Path] = None) -> Path:
59 |     """Return graph directory Path, creating it if it does not exist."""
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:65:40
   |
65 | def get_graph_storage_paths(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
   |                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^
66 |     """Return paths to serialized graph representations and metadata."""
67 |     gdir = get_graph_dir(graph_dir)
   |
help: Convert to `X | None`
   |
64 |
   - def get_graph_storage_paths(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
65 + def get_graph_storage_paths(graph_dir: Union[str, Path] | None = None) -> Dict[str, Path]:
66 |     """Return paths to serialized graph representations and metadata."""
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\graph\builder.py:65:49
   |
65 | def get_graph_storage_paths(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
   |                                                 ^^^^^^^^^^^^^^^^
66 |     """Return paths to serialized graph representations and metadata."""
67 |     gdir = get_graph_dir(graph_dir)
   |
help: Convert to `X | Y`
   |
64 |
   - def get_graph_storage_paths(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
65 + def get_graph_storage_paths(graph_dir: Optional[str | Path] = None) -> Dict[str, Path]:
66 |     """Return paths to serialized graph representations and metadata."""
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\graph\builder.py:65:78
   |
65 | def get_graph_storage_paths(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
   |                                                                              ^^^^
66 |     """Return paths to serialized graph representations and metadata."""
67 |     gdir = get_graph_dir(graph_dir)
   |
help: Replace with `dict`
   |
64 |
   - def get_graph_storage_paths(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
65 + def get_graph_storage_paths(graph_dir: Optional[Union[str, Path]] = None) -> dict[str, Path]:
66 |     """Return paths to serialized graph representations and metadata."""
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:75:31
   |
75 | def has_graph_data(graph_dir: Optional[Union[str, Path]] = None) -> bool:
   |                               ^^^^^^^^^^^^^^^^^^^^^^^^^^
76 |     """Check if compiled graph exists on disk."""
77 |     paths = get_graph_storage_paths(graph_dir)
   |
help: Convert to `X | None`
   |
74 |
   - def has_graph_data(graph_dir: Optional[Union[str, Path]] = None) -> bool:
75 + def has_graph_data(graph_dir: Union[str, Path] | None = None) -> bool:
76 |     """Check if compiled graph exists on disk."""
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\graph\builder.py:75:40
   |
75 | def has_graph_data(graph_dir: Optional[Union[str, Path]] = None) -> bool:
   |                                        ^^^^^^^^^^^^^^^^
76 |     """Check if compiled graph exists on disk."""
77 |     paths = get_graph_storage_paths(graph_dir)
   |
help: Convert to `X | Y`
   |
74 |
   - def has_graph_data(graph_dir: Optional[Union[str, Path]] = None) -> bool:
75 + def has_graph_data(graph_dir: Optional[str | Path] = None) -> bool:
76 |     """Check if compiled graph exists on disk."""
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:82:18
   |
81 | def build_investigation_graph(
82 |     storage_dir: Optional[Union[str, Path]] = None,
   |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
83 |     analysis_dir: Optional[Union[str, Path]] = None,
84 |     graph_dir: Optional[Union[str, Path]] = None,
   |
help: Convert to `X | None`
   |
81 | def build_investigation_graph(
   -     storage_dir: Optional[Union[str, Path]] = None,
82 +     storage_dir: Union[str, Path] | None = None,
83 |     analysis_dir: Optional[Union[str, Path]] = None,
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\graph\builder.py:82:27
   |
81 | def build_investigation_graph(
82 |     storage_dir: Optional[Union[str, Path]] = None,
   |                           ^^^^^^^^^^^^^^^^
83 |     analysis_dir: Optional[Union[str, Path]] = None,
84 |     graph_dir: Optional[Union[str, Path]] = None,
   |
help: Convert to `X | Y`
   |
81 | def build_investigation_graph(
   -     storage_dir: Optional[Union[str, Path]] = None,
82 +     storage_dir: Optional[str | Path] = None,
83 |     analysis_dir: Optional[Union[str, Path]] = None,
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:83:19
   |
81 | def build_investigation_graph(
82 |     storage_dir: Optional[Union[str, Path]] = None,
83 |     analysis_dir: Optional[Union[str, Path]] = None,
   |                   ^^^^^^^^^^^^^^^^^^^^^^^^^^
84 |     graph_dir: Optional[Union[str, Path]] = None,
85 |     force_rebuild: bool = False,
   |
help: Convert to `X | None`
   |
82 |     storage_dir: Optional[Union[str, Path]] = None,
   -     analysis_dir: Optional[Union[str, Path]] = None,
83 +     analysis_dir: Union[str, Path] | None = None,
84 |     graph_dir: Optional[Union[str, Path]] = None,
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\graph\builder.py:83:28
   |
81 | def build_investigation_graph(
82 |     storage_dir: Optional[Union[str, Path]] = None,
83 |     analysis_dir: Optional[Union[str, Path]] = None,
   |                            ^^^^^^^^^^^^^^^^
84 |     graph_dir: Optional[Union[str, Path]] = None,
85 |     force_rebuild: bool = False,
   |
help: Convert to `X | Y`
   |
82 |     storage_dir: Optional[Union[str, Path]] = None,
   -     analysis_dir: Optional[Union[str, Path]] = None,
83 +     analysis_dir: Optional[str | Path] = None,
84 |     graph_dir: Optional[Union[str, Path]] = None,
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\graph\builder.py:84:16
   |
82 |     storage_dir: Optional[Union[str, Path]] = None,
83 |     analysis_dir: Optional[Union[str, Path]] = None,
84 |     graph_dir: Optional[Union[str, Path]] = None,
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^
85 |     force_rebuild: bool = False,
86 | ) -> Tuple[nx.DiGraph, Dict[str, Any]]:
   |
help: Convert to `X | None`
   |
83 |     analysis_dir: Optional[Union[str, Path]] = None,
   -     graph_dir: Optional[Union[str, Path]] = None,
84 +     graph_dir: Union[str, Path] | None = None,
85 |     force_rebuild: bool = False,
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\graph\builder.py:84:25
   |
82 |     storage_dir: Optional[Union[str, Path]] = None,
83 |     analysis_dir: Optional[Union[str, Path]] = None,
84 |     graph_dir: Optional[Union[str, Path]] = None,
   |                         ^^^^^^^^^^^^^^^^
85 |     force_rebuild: bool = False,
86 | ) -> Tuple[nx.DiGraph, Dict[str, Any]]:
   |
help: Convert to `X | Y`
   |
83 |     analysis_dir: Optional[Union[str, Path]] = None,
   -     graph_dir: Optional[Union[str, Path]] = None,
84 +     graph_dir: Optional[str | Path] = None,
85 |     force_rebuild: bool = False,
   |

UP006 [*] Use `tuple` instead of `Tuple` for type annotation
  --> backend\app\graph\builder.py:86:6
   |
84 |     graph_dir: Optional[Union[str, Path]] = None,
85 |     force_rebuild: bool = False,
86 | ) -> Tuple[nx.DiGraph, Dict[str, Any]]:
   |      ^^^^^
87 |     """
88 |     Build the multi-layer Bitcoin investigation graph deterministically
   |
help: Replace with `tuple`
   |
85 |     force_rebuild: bool = False,
   - ) -> Tuple[nx.DiGraph, Dict[str, Any]]:
86 + ) -> tuple[nx.DiGraph, Dict[str, Any]]:
87 |     """
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\graph\builder.py:86:24
   |
84 |     graph_dir: Optional[Union[str, Path]] = None,
85 |     force_rebuild: bool = False,
86 | ) -> Tuple[nx.DiGraph, Dict[str, Any]]:
   |                        ^^^^
87 |     """
88 |     Build the multi-layer Bitcoin investigation graph deterministically
   |
help: Replace with `dict`
   |
85 |     force_rebuild: bool = False,
   - ) -> Tuple[nx.DiGraph, Dict[str, Any]]:
86 + ) -> Tuple[nx.DiGraph, dict[str, Any]]:
87 |     """
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\graph\builder.py:107:25
    |
106 |     # Load Phase 4 analysis data if present (investigative_leads.parquet)
107 |     analysis_by_wallet: Dict[str, Dict[str, Any]] = {}
    |                         ^^^^
108 |     if has_analysis_data(analysis_dir):
109 |         try:
    |
help: Replace with `dict`
    |
106 |     # Load Phase 4 analysis data if present (investigative_leads.parquet)
    -     analysis_by_wallet: Dict[str, Dict[str, Any]] = {}
107 +     analysis_by_wallet: dict[str, Dict[str, Any]] = {}
108 |     if has_analysis_data(analysis_dir):
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\graph\builder.py:107:35
    |
106 |     # Load Phase 4 analysis data if present (investigative_leads.parquet)
107 |     analysis_by_wallet: Dict[str, Dict[str, Any]] = {}
    |                                   ^^^^
108 |     if has_analysis_data(analysis_dir):
109 |         try:
    |
help: Replace with `dict`
    |
106 |     # Load Phase 4 analysis data if present (investigative_leads.parquet)
    -     analysis_by_wallet: Dict[str, Dict[str, Any]] = {}
107 +     analysis_by_wallet: Dict[str, dict[str, Any]] = {}
108 |     if has_analysis_data(analysis_dir):
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\graph\builder.py:123:16
    |
121 |                     "rank": int(row["rank"]),
122 |                 }
123 |         except Exception:
    |                ^^^^^^^^^
124 |             analysis_by_wallet = {}
    |

UP006 [*] Use `set` instead of `Set` for type annotation
   --> backend\app\graph\builder.py:162:15
    |
160 |     # 2. TRANSACTION NODES & WALLET <-> TX EDGES & COUNTERPARTY EDGES
161 |     # -------------------------------------------------------------
162 |     seen_ips: Set[str] = set()
    |               ^^^
163 |     seen_asns: Set[str] = set()
164 |     seen_countries: Set[str] = set()
    |
help: Replace with `set`
    |
161 |     # -------------------------------------------------------------
    -     seen_ips: Set[str] = set()
162 +     seen_ips: set[str] = set()
163 |     seen_asns: Set[str] = set()
    |

UP006 [*] Use `set` instead of `Set` for type annotation
   --> backend\app\graph\builder.py:163:16
    |
161 |     # -------------------------------------------------------------
162 |     seen_ips: Set[str] = set()
163 |     seen_asns: Set[str] = set()
    |                ^^^
164 |     seen_countries: Set[str] = set()
    |
help: Replace with `set`
    |
162 |     seen_ips: Set[str] = set()
    -     seen_asns: Set[str] = set()
163 +     seen_asns: set[str] = set()
164 |     seen_countries: Set[str] = set()
    |

UP006 [*] Use `set` instead of `Set` for type annotation
   --> backend\app\graph\builder.py:164:21
    |
162 |     seen_ips: Set[str] = set()
163 |     seen_asns: Set[str] = set()
164 |     seen_countries: Set[str] = set()
    |                     ^^^
165 |
166 |     for row in df_txs.sort("txid").iter_rows(named=True):
    |
help: Replace with `set`
    |
163 |     seen_asns: Set[str] = set()
    -     seen_countries: Set[str] = set()
164 +     seen_countries: set[str] = set()
165 |
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\graph\builder.py:327:23
    |
325 |     # 4. COMPUTE STRUCTURAL METRICS & SERIALIZE
326 |     # -------------------------------------------------------------
327 |     node_type_counts: Dict[str, int] = defaultdict(int)
    |                       ^^^^
328 |     for _, data in G.nodes(data=True):
329 |         node_type_counts[data.get("type", "unknown")] += 1
    |
help: Replace with `dict`
    |
326 |     # -------------------------------------------------------------
    -     node_type_counts: Dict[str, int] = defaultdict(int)
327 +     node_type_counts: dict[str, int] = defaultdict(int)
328 |     for _, data in G.nodes(data=True):
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\graph\builder.py:331:23
    |
329 |         node_type_counts[data.get("type", "unknown")] += 1
330 |
331 |     edge_type_counts: Dict[str, int] = defaultdict(int)
    |                       ^^^^
332 |     for _, _, data in G.edges(data=True):
333 |         edge_type_counts[data.get("type", "unknown")] += 1
    |
help: Replace with `dict`
    |
330 |
    -     edge_type_counts: Dict[str, int] = defaultdict(int)
331 +     edge_type_counts: dict[str, int] = defaultdict(int)
332 |     for _, _, data in G.edges(data=True):
    |

UP017 [*] Use `datetime.UTC` alias
   --> backend\app\graph\builder.py:355:34
    |
353 |         "density": density,
354 |         "is_deterministic": True,
355 |         "built_at": datetime.now(timezone.utc).isoformat(),
    |                                  ^^^^^^^^^^^^
356 |         "source_dataset_records": len(df_txs),
357 |     }
    |
help: Convert to `datetime.UTC` alias
    |
13  | from collections import defaultdict
    - from datetime import datetime, timezone
14  + from datetime import datetime, timezone, UTC
15  | import json
--------------------------------------------------------------------------------
354 |         "is_deterministic": True,
    -         "built_at": datetime.now(timezone.utc).isoformat(),
355 +         "built_at": datetime.now(UTC).isoformat(),
356 |         "source_dataset_records": len(df_txs),
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\graph\builder.py:377:12
    |
375 |             clean_G.add_edge(u, v, **clean_data)
376 |         nx.write_graphml(clean_G, str(g_paths["graphml"]))
377 |     except Exception:
    |            ^^^^^^^^^
378 |         logging.getLogger(__name__).warning("GraphML export failed")
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\graph\builder.py:387:18
    |
386 | def load_or_build_graph(
387 |     storage_dir: Optional[Union[str, Path]] = None,
    |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
388 |     analysis_dir: Optional[Union[str, Path]] = None,
389 |     graph_dir: Optional[Union[str, Path]] = None,
    |
help: Convert to `X | None`
    |
386 | def load_or_build_graph(
    -     storage_dir: Optional[Union[str, Path]] = None,
387 +     storage_dir: Union[str, Path] | None = None,
388 |     analysis_dir: Optional[Union[str, Path]] = None,
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\graph\builder.py:387:27
    |
386 | def load_or_build_graph(
387 |     storage_dir: Optional[Union[str, Path]] = None,
    |                           ^^^^^^^^^^^^^^^^
388 |     analysis_dir: Optional[Union[str, Path]] = None,
389 |     graph_dir: Optional[Union[str, Path]] = None,
    |
help: Convert to `X | Y`
    |
386 | def load_or_build_graph(
    -     storage_dir: Optional[Union[str, Path]] = None,
387 +     storage_dir: Optional[str | Path] = None,
388 |     analysis_dir: Optional[Union[str, Path]] = None,
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\graph\builder.py:388:19
    |
386 | def load_or_build_graph(
387 |     storage_dir: Optional[Union[str, Path]] = None,
388 |     analysis_dir: Optional[Union[str, Path]] = None,
    |                   ^^^^^^^^^^^^^^^^^^^^^^^^^^
389 |     graph_dir: Optional[Union[str, Path]] = None,
390 | ) -> nx.DiGraph:
    |
help: Convert to `X | None`
    |
387 |     storage_dir: Optional[Union[str, Path]] = None,
    -     analysis_dir: Optional[Union[str, Path]] = None,
388 +     analysis_dir: Union[str, Path] | None = None,
389 |     graph_dir: Optional[Union[str, Path]] = None,
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\graph\builder.py:388:28
    |
386 | def load_or_build_graph(
387 |     storage_dir: Optional[Union[str, Path]] = None,
388 |     analysis_dir: Optional[Union[str, Path]] = None,
    |                            ^^^^^^^^^^^^^^^^
389 |     graph_dir: Optional[Union[str, Path]] = None,
390 | ) -> nx.DiGraph:
    |
help: Convert to `X | Y`
    |
387 |     storage_dir: Optional[Union[str, Path]] = None,
    -     analysis_dir: Optional[Union[str, Path]] = None,
388 +     analysis_dir: Optional[str | Path] = None,
389 |     graph_dir: Optional[Union[str, Path]] = None,
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\graph\builder.py:389:16
    |
387 |     storage_dir: Optional[Union[str, Path]] = None,
388 |     analysis_dir: Optional[Union[str, Path]] = None,
389 |     graph_dir: Optional[Union[str, Path]] = None,
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^
390 | ) -> nx.DiGraph:
391 |     """Load cached in-memory graph, load from local disk, or build on demand."""
    |
help: Convert to `X | None`
    |
388 |     analysis_dir: Optional[Union[str, Path]] = None,
    -     graph_dir: Optional[Union[str, Path]] = None,
389 +     graph_dir: Union[str, Path] | None = None,
390 | ) -> nx.DiGraph:
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\graph\builder.py:389:25
    |
387 |     storage_dir: Optional[Union[str, Path]] = None,
388 |     analysis_dir: Optional[Union[str, Path]] = None,
389 |     graph_dir: Optional[Union[str, Path]] = None,
    |                         ^^^^^^^^^^^^^^^^
390 | ) -> nx.DiGraph:
391 |     """Load cached in-memory graph, load from local disk, or build on demand."""
    |
help: Convert to `X | Y`
    |
388 |     analysis_dir: Optional[Union[str, Path]] = None,
    -     graph_dir: Optional[Union[str, Path]] = None,
389 +     graph_dir: Optional[str | Path] = None,
390 | ) -> nx.DiGraph:
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\graph\builder.py:407:16
    |
405 |             _MEMORY_STATS_CACHE = stats
406 |             return G
407 |         except Exception:
    |                ^^^^^^^^^
408 |             logging.getLogger(__name__).warning("Rebuilding unreadable graph cache")
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\graph\builder.py:419:32
    |
419 | def get_graph_stats(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    |                                ^^^^^^^^^^^^^^^^^^^^^^^^^^
420 |     """Retrieve precompiled graph statistics."""
421 |     global _MEMORY_STATS_CACHE
    |
help: Convert to `X | None`
    |
418 |
    - def get_graph_stats(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
419 + def get_graph_stats(graph_dir: Union[str, Path] | None = None) -> Dict[str, Any]:
420 |     """Retrieve precompiled graph statistics."""
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\graph\builder.py:419:41
    |
419 | def get_graph_stats(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    |                                         ^^^^^^^^^^^^^^^^
420 |     """Retrieve precompiled graph statistics."""
421 |     global _MEMORY_STATS_CACHE
    |
help: Convert to `X | Y`
    |
418 |
    - def get_graph_stats(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
419 + def get_graph_stats(graph_dir: Optional[str | Path] = None) -> Dict[str, Any]:
420 |     """Retrieve precompiled graph statistics."""
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\graph\builder.py:419:70
    |
419 | def get_graph_stats(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    |                                                                      ^^^^
420 |     """Retrieve precompiled graph statistics."""
421 |     global _MEMORY_STATS_CACHE
    |
help: Replace with `dict`
    |
418 |
    - def get_graph_stats(graph_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
419 + def get_graph_stats(graph_dir: Optional[Union[str, Path]] = None) -> dict[str, Any]:
420 |     """Retrieve precompiled graph statistics."""
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\graph\builder.py:432:16
    |
430 |             _MEMORY_STATS_CACHE = stats
431 |             return stats
432 |         except Exception:
    |                ^^^^^^^^^
433 |             logging.getLogger(__name__).warning("Rebuilding unreadable graph statistics")
    |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\main.py:1:1
   |
 1 | / import logging
 2 | | import os
 3 | | from uuid import uuid4
 4 | | from starlette.exceptions import HTTPException
 5 | | from fastapi.exception_handlers import http_exception_handler
 6 | | from fastapi import Request
 7 | | from fastapi.responses import JSONResponse
 8 | | from fastapi import FastAPI
 9 | | from fastapi.middleware.cors import CORSMiddleware
10 | |
11 | | from app.routers import datasets, stats, analysis, alerts, graph, investigations, models, clusters
   | |__________________________________________________________________________________________________^
12 |
13 |   docs_enabled = os.getenv("NIRIKSHAK_ENABLE_DOCS") == "1"
   |
help: Organize imports
   |
3  | from uuid import uuid4
   - from starlette.exceptions import HTTPException
4  +
5  + from app.routers import (
6  +     alerts,
7  +     analysis,
8  +     clusters,
9  +     datasets,
10 +     graph,
11 +     investigations,
12 +     models,
13 +     stats,
14 + )
15 + from fastapi import FastAPI, Request
16 | from fastapi.exception_handlers import http_exception_handler
   - from fastapi import Request
17 + from fastapi.middleware.cors import CORSMiddleware
18 | from fastapi.responses import JSONResponse
   - from fastapi import FastAPI
   - from fastapi.middleware.cors import CORSMiddleware
   -
   - from app.routers import datasets, stats, analysis, alerts, graph, investigations, models, clusters
19 + from starlette.exceptions import HTTPException
20 |
   |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\pipeline\loader.py:1:1
   |
 1 | / import csv
 2 | | import io
 3 | | import json
 4 | | from pathlib import Path
 5 | | from typing import Any, Dict, List, Tuple, Union
 6 | | from pydantic import ValidationError
 7 | |
 8 | | from app.schemas.transaction import (
 9 | |     SCHEMA_VERSION,
10 | |     BitcoinTransactionRecord,
11 | |     DatasetSummary,
12 | | )
   | |_^
help: Organize imports
   |
5  | from typing import Any, Dict, List, Tuple, Union
   - from pydantic import ValidationError
6  |
--------------------------------------------------------------------------------
11 | )
12 + from pydantic import ValidationError
13 |
   |

UP035 `typing.Dict` is deprecated, use `dict` instead
 --> backend\app\pipeline\loader.py:5:1
  |
3 | import json
4 | from pathlib import Path
5 | from typing import Any, Dict, List, Tuple, Union
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
6 | from pydantic import ValidationError
  |

UP035 `typing.List` is deprecated, use `list` instead
 --> backend\app\pipeline\loader.py:5:1
  |
3 | import json
4 | from pathlib import Path
5 | from typing import Any, Dict, List, Tuple, Union
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
6 | from pydantic import ValidationError
  |

UP035 `typing.Tuple` is deprecated, use `tuple` instead
 --> backend\app\pipeline\loader.py:5:1
  |
3 | import json
4 | from pathlib import Path
5 | from typing import Any, Dict, List, Tuple, Union
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
6 | from pydantic import ValidationError
  |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:15:60
   |
15 | def parse_list_field(value: Any, item_type: type = str) -> List[Any]:
   |                                                            ^^^^
16 |     """Safely parse list fields from CSV (which may be JSON-encoded or already lists)."""
17 |     if isinstance(value, list):
   |
help: Replace with `list`
   |
14 |
   - def parse_list_field(value: Any, item_type: type = str) -> List[Any]:
15 + def parse_list_field(value: Any, item_type: type = str) -> list[Any]:
16 |     """Safely parse list fields from CSV (which may be JSON-encoded or already lists)."""
   |

UP006 [*] Use `tuple` instead of `Tuple` for type annotation
  --> backend\app\pipeline\loader.py:37:40
   |
37 | def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
   |                                        ^^^^^
38 |     """
39 |     Parse and validate Bitcoin transaction records from CSV string content.
   |
help: Replace with `tuple`
   |
36 |
   - def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
37 + def parse_csv_content(content: str) -> tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
38 |     """
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:37:46
   |
37 | def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
   |                                              ^^^^
38 |     """
39 |     Parse and validate Bitcoin transaction records from CSV string content.
   |
help: Replace with `list`
   |
36 |
   - def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
37 + def parse_csv_content(content: str) -> Tuple[list[BitcoinTransactionRecord], List[Dict[str, Any]]]:
38 |     """
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:37:78
   |
37 | def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
   |                                                                              ^^^^
38 |     """
39 |     Parse and validate Bitcoin transaction records from CSV string content.
   |
help: Replace with `list`
   |
36 |
   - def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
37 + def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], list[Dict[str, Any]]]:
38 |     """
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\pipeline\loader.py:37:83
   |
37 | def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
   |                                                                                   ^^^^
38 |     """
39 |     Parse and validate Bitcoin transaction records from CSV string content.
   |
help: Replace with `dict`
   |
36 |
   - def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
37 + def parse_csv_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[dict[str, Any]]]:
38 |     """
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:47:20
   |
45 |         return [], [{"line": 1, "txid": "none", "error": "Empty CSV or missing header row"}]
46 |
47 |     valid_records: List[BitcoinTransactionRecord] = []
   |                    ^^^^
48 |     rejected_records: List[Dict[str, Any]] = []
   |
help: Replace with `list`
   |
46 |
   -     valid_records: List[BitcoinTransactionRecord] = []
47 +     valid_records: list[BitcoinTransactionRecord] = []
48 |     rejected_records: List[Dict[str, Any]] = []
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:48:23
   |
47 |     valid_records: List[BitcoinTransactionRecord] = []
48 |     rejected_records: List[Dict[str, Any]] = []
   |                       ^^^^
49 |
50 |     for line_num, row in enumerate(reader, start=2):
   |
help: Replace with `list`
   |
47 |     valid_records: List[BitcoinTransactionRecord] = []
   -     rejected_records: List[Dict[str, Any]] = []
48 +     rejected_records: list[Dict[str, Any]] = []
49 |
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\pipeline\loader.py:48:28
   |
47 |     valid_records: List[BitcoinTransactionRecord] = []
48 |     rejected_records: List[Dict[str, Any]] = []
   |                            ^^^^
49 |
50 |     for line_num, row in enumerate(reader, start=2):
   |
help: Replace with `dict`
   |
47 |     valid_records: List[BitcoinTransactionRecord] = []
   -     rejected_records: List[Dict[str, Any]] = []
48 +     rejected_records: List[dict[str, Any]] = []
49 |
   |

UP006 [*] Use `tuple` instead of `Tuple` for type annotation
  --> backend\app\pipeline\loader.py:82:41
   |
82 | def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
   |                                         ^^^^^
83 |     """
84 |     Parse and validate Bitcoin transaction records from JSON string content.
   |
help: Replace with `tuple`
   |
81 |
   - def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
82 + def parse_json_content(content: str) -> tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
83 |     """
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:82:47
   |
82 | def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
   |                                               ^^^^
83 |     """
84 |     Parse and validate Bitcoin transaction records from JSON string content.
   |
help: Replace with `list`
   |
81 |
   - def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
82 + def parse_json_content(content: str) -> Tuple[list[BitcoinTransactionRecord], List[Dict[str, Any]]]:
83 |     """
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:82:79
   |
82 | def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
   |                                                                               ^^^^
83 |     """
84 |     Parse and validate Bitcoin transaction records from JSON string content.
   |
help: Replace with `list`
   |
81 |
   - def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
82 + def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], list[Dict[str, Any]]]:
83 |     """
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\pipeline\loader.py:82:84
   |
82 | def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
   |                                                                                    ^^^^
83 |     """
84 |     Parse and validate Bitcoin transaction records from JSON string content.
   |
help: Replace with `dict`
   |
81 |
   - def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
82 + def parse_json_content(content: str) -> Tuple[List[BitcoinTransactionRecord], List[dict[str, Any]]]:
83 |     """
   |

TRY004 Prefer `TypeError` exception for invalid type
  --> backend\app\pipeline\loader.py:90:9
   |
88 |     raw_list = data if isinstance(data, list) else data.get("transactions", [])
89 |     if not isinstance(raw_list, list):
90 |         raise ValueError("JSON must contain an array of transaction records or an object with a 'transactions' key.")
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
91 |
92 |     valid_records: List[BitcoinTransactionRecord] = []
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:92:20
   |
90 |         raise ValueError("JSON must contain an array of transaction records or an object with a 'transactions' key.")
91 |
92 |     valid_records: List[BitcoinTransactionRecord] = []
   |                    ^^^^
93 |     rejected_records: List[Dict[str, Any]] = []
   |
help: Replace with `list`
   |
91 |
   -     valid_records: List[BitcoinTransactionRecord] = []
92 +     valid_records: list[BitcoinTransactionRecord] = []
93 |     rejected_records: List[Dict[str, Any]] = []
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\pipeline\loader.py:93:23
   |
92 |     valid_records: List[BitcoinTransactionRecord] = []
93 |     rejected_records: List[Dict[str, Any]] = []
   |                       ^^^^
94 |
95 |     for index, item in enumerate(raw_list):
   |
help: Replace with `list`
   |
92 |     valid_records: List[BitcoinTransactionRecord] = []
   -     rejected_records: List[Dict[str, Any]] = []
93 +     rejected_records: list[Dict[str, Any]] = []
94 |
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\pipeline\loader.py:93:28
   |
92 |     valid_records: List[BitcoinTransactionRecord] = []
93 |     rejected_records: List[Dict[str, Any]] = []
   |                            ^^^^
94 |
95 |     for index, item in enumerate(raw_list):
   |
help: Replace with `dict`
   |
92 |     valid_records: List[BitcoinTransactionRecord] = []
   -     rejected_records: List[Dict[str, Any]] = []
93 +     rejected_records: List[dict[str, Any]] = []
94 |
   |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\loader.py:116:42
    |
116 | def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                          ^^^^^^^^^^^^^^^^
117 |     """
118 |     Load and validate Bitcoin transaction records from a CSV file.
    |
help: Convert to `X | Y`
    |
115 |
    - def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
116 + def load_transactions_from_csv(filepath: str | Path) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
117 |     """
    |

UP006 [*] Use `tuple` instead of `Tuple` for type annotation
   --> backend\app\pipeline\loader.py:116:63
    |
116 | def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                               ^^^^^
117 |     """
118 |     Load and validate Bitcoin transaction records from a CSV file.
    |
help: Replace with `tuple`
    |
115 |
    - def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
116 + def load_transactions_from_csv(filepath: Union[str, Path]) -> tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
117 |     """
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\loader.py:116:69
    |
116 | def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                     ^^^^
117 |     """
118 |     Load and validate Bitcoin transaction records from a CSV file.
    |
help: Replace with `list`
    |
115 |
    - def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
116 + def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[list[BitcoinTransactionRecord], List[Dict[str, Any]]]:
117 |     """
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\loader.py:116:101
    |
116 | def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                                                     ^^^^
117 |     """
118 |     Load and validate Bitcoin transaction records from a CSV file.
    |
help: Replace with `list`
    |
115 |
    - def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
116 + def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], list[Dict[str, Any]]]:
117 |     """
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\pipeline\loader.py:116:106
    |
116 | def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                                                          ^^^^
117 |     """
118 |     Load and validate Bitcoin transaction records from a CSV file.
    |
help: Replace with `dict`
    |
115 |
    - def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
116 + def load_transactions_from_csv(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[dict[str, Any]]]:
117 |     """
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\loader.py:130:43
    |
130 | def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                           ^^^^^^^^^^^^^^^^
131 |     """
132 |     Load and validate Bitcoin transaction records from a JSON file.
    |
help: Convert to `X | Y`
    |
129 |
    - def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
130 + def load_transactions_from_json(filepath: str | Path) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
131 |     """
    |

UP006 [*] Use `tuple` instead of `Tuple` for type annotation
   --> backend\app\pipeline\loader.py:130:64
    |
130 | def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                ^^^^^
131 |     """
132 |     Load and validate Bitcoin transaction records from a JSON file.
    |
help: Replace with `tuple`
    |
129 |
    - def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
130 + def load_transactions_from_json(filepath: Union[str, Path]) -> tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
131 |     """
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\loader.py:130:70
    |
130 | def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                      ^^^^
131 |     """
132 |     Load and validate Bitcoin transaction records from a JSON file.
    |
help: Replace with `list`
    |
129 |
    - def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
130 + def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[list[BitcoinTransactionRecord], List[Dict[str, Any]]]:
131 |     """
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\loader.py:130:102
    |
130 | def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                                                      ^^^^
131 |     """
132 |     Load and validate Bitcoin transaction records from a JSON file.
    |
help: Replace with `list`
    |
129 |
    - def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
130 + def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], list[Dict[str, Any]]]:
131 |     """
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\pipeline\loader.py:130:107
    |
130 | def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                                                           ^^^^
131 |     """
132 |     Load and validate Bitcoin transaction records from a JSON file.
    |
help: Replace with `dict`
    |
129 |
    - def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
130 + def load_transactions_from_json(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[dict[str, Any]]]:
131 |     """
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\loader.py:144:33
    |
144 | def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                 ^^^^^^^^^^^^^^^^
145 |     """Generic dataset loader supporting both .csv and .json formats."""
146 |     path = Path(filepath)
    |
help: Convert to `X | Y`
    |
143 |
    - def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
144 + def load_transactions(filepath: str | Path) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
145 |     """Generic dataset loader supporting both .csv and .json formats."""
    |

UP006 [*] Use `tuple` instead of `Tuple` for type annotation
   --> backend\app\pipeline\loader.py:144:54
    |
144 | def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                      ^^^^^
145 |     """Generic dataset loader supporting both .csv and .json formats."""
146 |     path = Path(filepath)
    |
help: Replace with `tuple`
    |
143 |
    - def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
144 + def load_transactions(filepath: Union[str, Path]) -> tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
145 |     """Generic dataset loader supporting both .csv and .json formats."""
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\loader.py:144:60
    |
144 | def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                            ^^^^
145 |     """Generic dataset loader supporting both .csv and .json formats."""
146 |     path = Path(filepath)
    |
help: Replace with `list`
    |
143 |
    - def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
144 + def load_transactions(filepath: Union[str, Path]) -> Tuple[list[BitcoinTransactionRecord], List[Dict[str, Any]]]:
145 |     """Generic dataset loader supporting both .csv and .json formats."""
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\loader.py:144:92
    |
144 | def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                                            ^^^^
145 |     """Generic dataset loader supporting both .csv and .json formats."""
146 |     path = Path(filepath)
    |
help: Replace with `list`
    |
143 |
    - def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
144 + def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], list[Dict[str, Any]]]:
145 |     """Generic dataset loader supporting both .csv and .json formats."""
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\pipeline\loader.py:144:97
    |
144 | def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
    |                                                                                                 ^^^^
145 |     """Generic dataset loader supporting both .csv and .json formats."""
146 |     path = Path(filepath)
    |
help: Replace with `dict`
    |
143 |
    - def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[Dict[str, Any]]]:
144 + def load_transactions(filepath: Union[str, Path]) -> Tuple[List[BitcoinTransactionRecord], List[dict[str, Any]]]:
145 |     """Generic dataset loader supporting both .csv and .json formats."""
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\loader.py:156:33
    |
156 | def load_ground_truth(filepath: Union[str, Path]) -> Dict[str, Any]:
    |                                 ^^^^^^^^^^^^^^^^
157 |     """Load hidden ground-truth file for offline model evaluation."""
158 |     path = Path(filepath)
    |
help: Convert to `X | Y`
    |
155 |
    - def load_ground_truth(filepath: Union[str, Path]) -> Dict[str, Any]:
156 + def load_ground_truth(filepath: str | Path) -> Dict[str, Any]:
157 |     """Load hidden ground-truth file for offline model evaluation."""
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\pipeline\loader.py:156:54
    |
156 | def load_ground_truth(filepath: Union[str, Path]) -> Dict[str, Any]:
    |                                                      ^^^^
157 |     """Load hidden ground-truth file for offline model evaluation."""
158 |     path = Path(filepath)
    |
help: Replace with `dict`
    |
155 |
    - def load_ground_truth(filepath: Union[str, Path]) -> Dict[str, Any]:
156 + def load_ground_truth(filepath: Union[str, Path]) -> dict[str, Any]:
157 |     """Load hidden ground-truth file for offline model evaluation."""
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\loader.py:165:40
    |
165 | def calculate_dataset_summary(records: List[BitcoinTransactionRecord]) -> DatasetSummary:
    |                                        ^^^^
166 |     """Compute high-level summary metrics from a list of validated records."""
167 |     if not records:
    |
help: Replace with `list`
    |
164 |
    - def calculate_dataset_summary(records: List[BitcoinTransactionRecord]) -> DatasetSummary:
165 + def calculate_dataset_summary(records: list[BitcoinTransactionRecord]) -> DatasetSummary:
166 |     """Compute high-level summary metrics from a list of validated records."""
    |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\pipeline\storage.py:11:1
   |
 9 |   """
10 |
11 | / from pathlib import Path
12 | | from typing import Any, Dict, List, Optional, Tuple, Union
13 | | import duckdb
14 | | import polars as pl
   | |___________________^
15 |
16 |   # Path to normalized storage directory inside backend/data/normalized
   |
help: Organize imports
   |
12 | from typing import Any, Dict, List, Optional, Tuple, Union
13 +
14 | import duckdb
   |

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> backend\app\pipeline\storage.py:12:1
   |
11 | from pathlib import Path
12 | from typing import Any, Dict, List, Optional, Tuple, Union
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 | import duckdb
14 | import polars as pl
   |

UP035 `typing.List` is deprecated, use `list` instead
  --> backend\app\pipeline\storage.py:12:1
   |
11 | from pathlib import Path
12 | from typing import Any, Dict, List, Optional, Tuple, Union
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 | import duckdb
14 | import polars as pl
   |

UP035 `typing.Tuple` is deprecated, use `tuple` instead
  --> backend\app\pipeline\storage.py:12:1
   |
11 | from pathlib import Path
12 | from typing import Any, Dict, List, Optional, Tuple, Union
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 | import duckdb
14 | import polars as pl
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\pipeline\storage.py:20:33
   |
20 | def get_storage_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
   |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^
21 |     """Return storage directory Path, creating it if it does not exist."""
22 |     target_dir = Path(custom_dir) if custom_dir else DEFAULT_STORAGE_DIR
   |
help: Convert to `X | None`
   |
19 |
   - def get_storage_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
20 + def get_storage_dir(custom_dir: Union[str, Path] | None = None) -> Path:
21 |     """Return storage directory Path, creating it if it does not exist."""
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\pipeline\storage.py:20:42
   |
20 | def get_storage_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
   |                                          ^^^^^^^^^^^^^^^^
21 |     """Return storage directory Path, creating it if it does not exist."""
22 |     target_dir = Path(custom_dir) if custom_dir else DEFAULT_STORAGE_DIR
   |
help: Convert to `X | Y`
   |
19 |
   - def get_storage_dir(custom_dir: Optional[Union[str, Path]] = None) -> Path:
20 + def get_storage_dir(custom_dir: Optional[str | Path] = None) -> Path:
21 |     """Return storage directory Path, creating it if it does not exist."""
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\pipeline\storage.py:27:36
   |
27 | def get_parquet_paths(storage_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
   |                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^
28 |     """Get file paths for all three core analytical Parquet tables."""
29 |     sdir = get_storage_dir(storage_dir)
   |
help: Convert to `X | None`
   |
26 |
   - def get_parquet_paths(storage_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
27 + def get_parquet_paths(storage_dir: Union[str, Path] | None = None) -> Dict[str, Path]:
28 |     """Get file paths for all three core analytical Parquet tables."""
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\pipeline\storage.py:27:45
   |
27 | def get_parquet_paths(storage_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
   |                                             ^^^^^^^^^^^^^^^^
28 |     """Get file paths for all three core analytical Parquet tables."""
29 |     sdir = get_storage_dir(storage_dir)
   |
help: Convert to `X | Y`
   |
26 |
   - def get_parquet_paths(storage_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
27 + def get_parquet_paths(storage_dir: Optional[str | Path] = None) -> Dict[str, Path]:
28 |     """Get file paths for all three core analytical Parquet tables."""
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\pipeline\storage.py:27:74
   |
27 | def get_parquet_paths(storage_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
   |                                                                          ^^^^
28 |     """Get file paths for all three core analytical Parquet tables."""
29 |     sdir = get_storage_dir(storage_dir)
   |
help: Replace with `dict`
   |
26 |
   - def get_parquet_paths(storage_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
27 + def get_parquet_paths(storage_dir: Optional[Union[str, Path]] = None) -> dict[str, Path]:
28 |     """Get file paths for all three core analytical Parquet tables."""
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\pipeline\storage.py:38:13
   |
37 | def save_normalized_tables(
38 |     tables: Dict[str, pl.DataFrame],
   |             ^^^^
39 |     storage_dir: Optional[Union[str, Path]] = None,
40 | ) -> Dict[str, str]:
   |
help: Replace with `dict`
   |
37 | def save_normalized_tables(
   -     tables: Dict[str, pl.DataFrame],
38 +     tables: dict[str, pl.DataFrame],
39 |     storage_dir: Optional[Union[str, Path]] = None,
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\pipeline\storage.py:39:18
   |
37 | def save_normalized_tables(
38 |     tables: Dict[str, pl.DataFrame],
39 |     storage_dir: Optional[Union[str, Path]] = None,
   |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
40 | ) -> Dict[str, str]:
41 |     """
   |
help: Convert to `X | None`
   |
38 |     tables: Dict[str, pl.DataFrame],
   -     storage_dir: Optional[Union[str, Path]] = None,
39 +     storage_dir: Union[str, Path] | None = None,
40 | ) -> Dict[str, str]:
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\pipeline\storage.py:39:27
   |
37 | def save_normalized_tables(
38 |     tables: Dict[str, pl.DataFrame],
39 |     storage_dir: Optional[Union[str, Path]] = None,
   |                           ^^^^^^^^^^^^^^^^
40 | ) -> Dict[str, str]:
41 |     """
   |
help: Convert to `X | Y`
   |
38 |     tables: Dict[str, pl.DataFrame],
   -     storage_dir: Optional[Union[str, Path]] = None,
39 +     storage_dir: Optional[str | Path] = None,
40 | ) -> Dict[str, str]:
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\pipeline\storage.py:40:6
   |
38 |     tables: Dict[str, pl.DataFrame],
39 |     storage_dir: Optional[Union[str, Path]] = None,
40 | ) -> Dict[str, str]:
   |      ^^^^
41 |     """
42 |     Save normalized Polars DataFrames as Parquet files in local storage.
   |
help: Replace with `dict`
   |
39 |     storage_dir: Optional[Union[str, Path]] = None,
   - ) -> Dict[str, str]:
40 + ) -> dict[str, str]:
41 |     """
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\pipeline\storage.py:55:38
   |
55 | def has_normalized_data(storage_dir: Optional[Union[str, Path]] = None) -> bool:
   |                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^
56 |     """Check if all required Parquet tables exist on disk and have content."""
57 |     paths = get_parquet_paths(storage_dir)
   |
help: Convert to `X | None`
   |
54 |
   - def has_normalized_data(storage_dir: Optional[Union[str, Path]] = None) -> bool:
55 + def has_normalized_data(storage_dir: Union[str, Path] | None = None) -> bool:
56 |     """Check if all required Parquet tables exist on disk and have content."""
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\pipeline\storage.py:55:47
   |
55 | def has_normalized_data(storage_dir: Optional[Union[str, Path]] = None) -> bool:
   |                                               ^^^^^^^^^^^^^^^^
56 |     """Check if all required Parquet tables exist on disk and have content."""
57 |     paths = get_parquet_paths(storage_dir)
   |
help: Convert to `X | Y`
   |
54 |
   - def has_normalized_data(storage_dir: Optional[Union[str, Path]] = None) -> bool:
55 + def has_normalized_data(storage_dir: Optional[str | Path] = None) -> bool:
56 |     """Check if all required Parquet tables exist on disk and have content."""
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\pipeline\storage.py:64:40
   |
64 | def get_duckdb_connection(storage_dir: Optional[Union[str, Path]] = None) -> duckdb.DuckDBPyConnection:
   |                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^
65 |     """
66 |     Create an in-memory DuckDB connection with views pointing directly
   |
help: Convert to `X | None`
   |
63 |
   - def get_duckdb_connection(storage_dir: Optional[Union[str, Path]] = None) -> duckdb.DuckDBPyConnection:
64 + def get_duckdb_connection(storage_dir: Union[str, Path] | None = None) -> duckdb.DuckDBPyConnection:
65 |     """
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\pipeline\storage.py:64:49
   |
64 | def get_duckdb_connection(storage_dir: Optional[Union[str, Path]] = None) -> duckdb.DuckDBPyConnection:
   |                                                 ^^^^^^^^^^^^^^^^
65 |     """
66 |     Create an in-memory DuckDB connection with views pointing directly
   |
help: Convert to `X | Y`
   |
63 |
   - def get_duckdb_connection(storage_dir: Optional[Union[str, Path]] = None) -> duckdb.DuckDBPyConnection:
64 + def get_duckdb_connection(storage_dir: Optional[str | Path] = None) -> duckdb.DuckDBPyConnection:
65 |     """
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\pipeline\storage.py:82:40
   |
82 | def get_transaction_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
   |                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^
83 |     con = get_duckdb_connection(storage_dir)
84 |     res = con.execute("SELECT COUNT(*) FROM transactions").fetchone()
   |
help: Convert to `X | None`
   |
81 |
   - def get_transaction_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
82 + def get_transaction_count(storage_dir: Union[str, Path] | None = None) -> int:
83 |     con = get_duckdb_connection(storage_dir)
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\pipeline\storage.py:82:49
   |
82 | def get_transaction_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
   |                                                 ^^^^^^^^^^^^^^^^
83 |     con = get_duckdb_connection(storage_dir)
84 |     res = con.execute("SELECT COUNT(*) FROM transactions").fetchone()
   |
help: Convert to `X | Y`
   |
81 |
   - def get_transaction_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
82 + def get_transaction_count(storage_dir: Optional[str | Path] = None) -> int:
83 |     con = get_duckdb_connection(storage_dir)
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\pipeline\storage.py:88:35
   |
88 | def get_wallet_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
   |                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^
89 |     con = get_duckdb_connection(storage_dir)
90 |     res = con.execute("SELECT COUNT(*) FROM wallets").fetchone()
   |
help: Convert to `X | None`
   |
87 |
   - def get_wallet_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
88 + def get_wallet_count(storage_dir: Union[str, Path] | None = None) -> int:
89 |     con = get_duckdb_connection(storage_dir)
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\pipeline\storage.py:88:44
   |
88 | def get_wallet_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
   |                                            ^^^^^^^^^^^^^^^^
89 |     con = get_duckdb_connection(storage_dir)
90 |     res = con.execute("SELECT COUNT(*) FROM wallets").fetchone()
   |
help: Convert to `X | Y`
   |
87 |
   - def get_wallet_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
88 + def get_wallet_count(storage_dir: Optional[str | Path] = None) -> int:
89 |     con = get_duckdb_connection(storage_dir)
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\pipeline\storage.py:94:48
   |
94 | def get_network_observation_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
   |                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^
95 |     con = get_duckdb_connection(storage_dir)
96 |     res = con.execute("SELECT COUNT(*) FROM network_observations").fetchone()
   |
help: Convert to `X | None`
   |
93 |
   - def get_network_observation_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
94 + def get_network_observation_count(storage_dir: Union[str, Path] | None = None) -> int:
95 |     con = get_duckdb_connection(storage_dir)
   |

UP007 [*] Use `X | Y` for type annotations
  --> backend\app\pipeline\storage.py:94:57
   |
94 | def get_network_observation_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
   |                                                         ^^^^^^^^^^^^^^^^
95 |     con = get_duckdb_connection(storage_dir)
96 |     res = con.execute("SELECT COUNT(*) FROM network_observations").fetchone()
   |
help: Convert to `X | Y`
   |
93 |
   - def get_network_observation_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
94 + def get_network_observation_count(storage_dir: Optional[str | Path] = None) -> int:
95 |     con = get_duckdb_connection(storage_dir)
   |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\pipeline\storage.py:100:38
    |
100 | def get_unique_ip_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
    |                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^
101 |     con = get_duckdb_connection(storage_dir)
102 |     res = con.execute("""
    |
help: Convert to `X | None`
    |
99  |
    - def get_unique_ip_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
100 + def get_unique_ip_count(storage_dir: Union[str, Path] | None = None) -> int:
101 |     con = get_duckdb_connection(storage_dir)
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\storage.py:100:47
    |
100 | def get_unique_ip_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
    |                                               ^^^^^^^^^^^^^^^^
101 |     con = get_duckdb_connection(storage_dir)
102 |     res = con.execute("""
    |
help: Convert to `X | Y`
    |
99  |
    - def get_unique_ip_count(storage_dir: Optional[Union[str, Path]] = None) -> int:
100 + def get_unique_ip_count(storage_dir: Optional[str | Path] = None) -> int:
101 |     con = get_duckdb_connection(storage_dir)
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\pipeline\storage.py:112:47
    |
112 | def get_total_transaction_volume(storage_dir: Optional[Union[str, Path]] = None) -> float:
    |                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^
113 |     con = get_duckdb_connection(storage_dir)
114 |     res = con.execute("SELECT ROUND(SUM(total_output_amount), 8) FROM transactions").fetchone()
    |
help: Convert to `X | None`
    |
111 |
    - def get_total_transaction_volume(storage_dir: Optional[Union[str, Path]] = None) -> float:
112 + def get_total_transaction_volume(storage_dir: Union[str, Path] | None = None) -> float:
113 |     con = get_duckdb_connection(storage_dir)
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\storage.py:112:56
    |
112 | def get_total_transaction_volume(storage_dir: Optional[Union[str, Path]] = None) -> float:
    |                                                        ^^^^^^^^^^^^^^^^
113 |     con = get_duckdb_connection(storage_dir)
114 |     res = con.execute("SELECT ROUND(SUM(total_output_amount), 8) FROM transactions").fetchone()
    |
help: Convert to `X | Y`
    |
111 |
    - def get_total_transaction_volume(storage_dir: Optional[Union[str, Path]] = None) -> float:
112 + def get_total_transaction_volume(storage_dir: Optional[str | Path] = None) -> float:
113 |     con = get_duckdb_connection(storage_dir)
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\pipeline\storage.py:118:33
    |
118 | def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
    |                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^
119 |     con = get_duckdb_connection(storage_dir)
120 |     res = con.execute("SELECT MIN(timestamp), MAX(timestamp) FROM transactions").fetchone()
    |
help: Convert to `X | None`
    |
117 |
    - def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
118 + def get_time_range(storage_dir: Union[str, Path] | None = None) -> Tuple[Optional[str], Optional[str]]:
119 |     con = get_duckdb_connection(storage_dir)
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\storage.py:118:42
    |
118 | def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
    |                                          ^^^^^^^^^^^^^^^^
119 |     con = get_duckdb_connection(storage_dir)
120 |     res = con.execute("SELECT MIN(timestamp), MAX(timestamp) FROM transactions").fetchone()
    |
help: Convert to `X | Y`
    |
117 |
    - def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
118 + def get_time_range(storage_dir: Optional[str | Path] = None) -> Tuple[Optional[str], Optional[str]]:
119 |     con = get_duckdb_connection(storage_dir)
    |

UP006 [*] Use `tuple` instead of `Tuple` for type annotation
   --> backend\app\pipeline\storage.py:118:71
    |
118 | def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
    |                                                                       ^^^^^
119 |     con = get_duckdb_connection(storage_dir)
120 |     res = con.execute("SELECT MIN(timestamp), MAX(timestamp) FROM transactions").fetchone()
    |
help: Replace with `tuple`
    |
117 |
    - def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
118 + def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> tuple[Optional[str], Optional[str]]:
119 |     con = get_duckdb_connection(storage_dir)
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\pipeline\storage.py:118:77
    |
118 | def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
    |                                                                             ^^^^^^^^^^^^^
119 |     con = get_duckdb_connection(storage_dir)
120 |     res = con.execute("SELECT MIN(timestamp), MAX(timestamp) FROM transactions").fetchone()
    |
help: Convert to `X | None`
    |
117 |
    - def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
118 + def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[str | None, Optional[str]]:
119 |     con = get_duckdb_connection(storage_dir)
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\pipeline\storage.py:118:92
    |
118 | def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
    |                                                                                            ^^^^^^^^^^^^^
119 |     con = get_duckdb_connection(storage_dir)
120 |     res = con.execute("SELECT MIN(timestamp), MAX(timestamp) FROM transactions").fetchone()
    |
help: Convert to `X | None`
    |
117 |
    - def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], Optional[str]]:
118 + def get_time_range(storage_dir: Optional[Union[str, Path]] = None) -> Tuple[Optional[str], str | None]:
119 |     con = get_duckdb_connection(storage_dir)
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\pipeline\storage.py:128:18
    |
126 | def get_top_wallets_by_tx_count(
127 |     limit: int = 10,
128 |     storage_dir: Optional[Union[str, Path]] = None,
    |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
129 | ) -> List[Dict[str, Any]]:
130 |     con = get_duckdb_connection(storage_dir)
    |
help: Convert to `X | None`
    |
127 |     limit: int = 10,
    -     storage_dir: Optional[Union[str, Path]] = None,
128 +     storage_dir: Union[str, Path] | None = None,
129 | ) -> List[Dict[str, Any]]:
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\storage.py:128:27
    |
126 | def get_top_wallets_by_tx_count(
127 |     limit: int = 10,
128 |     storage_dir: Optional[Union[str, Path]] = None,
    |                           ^^^^^^^^^^^^^^^^
129 | ) -> List[Dict[str, Any]]:
130 |     con = get_duckdb_connection(storage_dir)
    |
help: Convert to `X | Y`
    |
127 |     limit: int = 10,
    -     storage_dir: Optional[Union[str, Path]] = None,
128 +     storage_dir: Optional[str | Path] = None,
129 | ) -> List[Dict[str, Any]]:
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\storage.py:129:6
    |
127 |     limit: int = 10,
128 |     storage_dir: Optional[Union[str, Path]] = None,
129 | ) -> List[Dict[str, Any]]:
    |      ^^^^
130 |     con = get_duckdb_connection(storage_dir)
131 |     df = con.execute("""
    |
help: Replace with `list`
    |
128 |     storage_dir: Optional[Union[str, Path]] = None,
    - ) -> List[Dict[str, Any]]:
129 + ) -> list[Dict[str, Any]]:
130 |     con = get_duckdb_connection(storage_dir)
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\pipeline\storage.py:129:11
    |
127 |     limit: int = 10,
128 |     storage_dir: Optional[Union[str, Path]] = None,
129 | ) -> List[Dict[str, Any]]:
    |           ^^^^
130 |     con = get_duckdb_connection(storage_dir)
131 |     df = con.execute("""
    |
help: Replace with `dict`
    |
128 |     storage_dir: Optional[Union[str, Path]] = None,
    - ) -> List[Dict[str, Any]]:
129 + ) -> List[dict[str, Any]]:
130 |     con = get_duckdb_connection(storage_dir)
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\pipeline\storage.py:148:18
    |
146 | def get_top_wallets_by_volume(
147 |     limit: int = 10,
148 |     storage_dir: Optional[Union[str, Path]] = None,
    |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
149 | ) -> List[Dict[str, Any]]:
150 |     con = get_duckdb_connection(storage_dir)
    |
help: Convert to `X | None`
    |
147 |     limit: int = 10,
    -     storage_dir: Optional[Union[str, Path]] = None,
148 +     storage_dir: Union[str, Path] | None = None,
149 | ) -> List[Dict[str, Any]]:
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\storage.py:148:27
    |
146 | def get_top_wallets_by_volume(
147 |     limit: int = 10,
148 |     storage_dir: Optional[Union[str, Path]] = None,
    |                           ^^^^^^^^^^^^^^^^
149 | ) -> List[Dict[str, Any]]:
150 |     con = get_duckdb_connection(storage_dir)
    |
help: Convert to `X | Y`
    |
147 |     limit: int = 10,
    -     storage_dir: Optional[Union[str, Path]] = None,
148 +     storage_dir: Optional[str | Path] = None,
149 | ) -> List[Dict[str, Any]]:
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\pipeline\storage.py:149:6
    |
147 |     limit: int = 10,
148 |     storage_dir: Optional[Union[str, Path]] = None,
149 | ) -> List[Dict[str, Any]]:
    |      ^^^^
150 |     con = get_duckdb_connection(storage_dir)
151 |     df = con.execute("""
    |
help: Replace with `list`
    |
148 |     storage_dir: Optional[Union[str, Path]] = None,
    - ) -> List[Dict[str, Any]]:
149 + ) -> list[Dict[str, Any]]:
150 |     con = get_duckdb_connection(storage_dir)
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\pipeline\storage.py:149:11
    |
147 |     limit: int = 10,
148 |     storage_dir: Optional[Union[str, Path]] = None,
149 | ) -> List[Dict[str, Any]]:
    |           ^^^^
150 |     con = get_duckdb_connection(storage_dir)
151 |     df = con.execute("""
    |
help: Replace with `dict`
    |
148 |     storage_dir: Optional[Union[str, Path]] = None,
    - ) -> List[Dict[str, Any]]:
149 + ) -> List[dict[str, Any]]:
150 |     con = get_duckdb_connection(storage_dir)
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\pipeline\storage.py:166:18
    |
165 | def get_dataset_analytics_summary(
166 |     storage_dir: Optional[Union[str, Path]] = None,
    |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
167 | ) -> Dict[str, Any]:
168 |     """
    |
help: Convert to `X | None`
    |
165 | def get_dataset_analytics_summary(
    -     storage_dir: Optional[Union[str, Path]] = None,
166 +     storage_dir: Union[str, Path] | None = None,
167 | ) -> Dict[str, Any]:
    |

UP007 [*] Use `X | Y` for type annotations
   --> backend\app\pipeline\storage.py:166:27
    |
165 | def get_dataset_analytics_summary(
166 |     storage_dir: Optional[Union[str, Path]] = None,
    |                           ^^^^^^^^^^^^^^^^
167 | ) -> Dict[str, Any]:
168 |     """
    |
help: Convert to `X | Y`
    |
165 | def get_dataset_analytics_summary(
    -     storage_dir: Optional[Union[str, Path]] = None,
166 +     storage_dir: Optional[str | Path] = None,
167 | ) -> Dict[str, Any]:
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\pipeline\storage.py:167:6
    |
165 | def get_dataset_analytics_summary(
166 |     storage_dir: Optional[Union[str, Path]] = None,
167 | ) -> Dict[str, Any]:
    |      ^^^^
168 |     """
169 |     High-level analytics summary calculated via DuckDB queries over the Parquet store.
    |
help: Replace with `dict`
    |
166 |     storage_dir: Optional[Union[str, Path]] = None,
    - ) -> Dict[str, Any]:
167 + ) -> dict[str, Any]:
168 |     """
    |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\routers\alerts.py:9:1
   |
 7 |   """
 8 |
 9 | / import json
10 | | from typing import Any, Dict, List, Optional
11 | | import duckdb
12 | | from fastapi import APIRouter, HTTPException, Query, status
13 | |
14 | | from app.ml.analyzer import get_analysis_paths, has_analysis_data
15 | | from app.ml.evidence import EvidenceReason
16 | | from app.schemas.analysis import (
17 | |     AlertDetailResponse,
18 | |     AlertItem,
19 | |     AlertsListResponse,
20 | | )
   | |_^
21 |
22 |   router = APIRouter()
   |
help: Organize imports
   |
10 | from typing import Any, Dict, List, Optional
11 +
12 | import duckdb
   - from fastapi import APIRouter, HTTPException, Query, status
   -
13 | from app.ml.analyzer import get_analysis_paths, has_analysis_data
--------------------------------------------------------------------------------
19 | )
20 + from fastapi import APIRouter, HTTPException, Query, status
21 |
   |

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> backend\app\routers\alerts.py:10:1
   |
 9 | import json
10 | from typing import Any, Dict, List, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11 | import duckdb
12 | from fastapi import APIRouter, HTTPException, Query, status
   |

UP035 `typing.List` is deprecated, use `list` instead
  --> backend\app\routers\alerts.py:10:1
   |
 9 | import json
10 | from typing import Any, Dict, List, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
11 | import duckdb
12 | from fastapi import APIRouter, HTTPException, Query, status
   |

F401 [*] `typing.Any` imported but unused
  --> backend\app\routers\alerts.py:10:20
   |
 9 | import json
10 | from typing import Any, Dict, List, Optional
   |                    ^^^
11 | import duckdb
12 | from fastapi import APIRouter, HTTPException, Query, status
   |
help: Remove unused import
   |
9  | import json
   - from typing import Any, Dict, List, Optional
10 + from typing import List, Optional
11 | import duckdb
   |

F401 [*] `typing.Dict` imported but unused
  --> backend\app\routers\alerts.py:10:25
   |
 9 | import json
10 | from typing import Any, Dict, List, Optional
   |                         ^^^^
11 | import duckdb
12 | from fastapi import APIRouter, HTTPException, Query, status
   |
help: Remove unused import
   |
9  | import json
   - from typing import Any, Dict, List, Optional
10 + from typing import List, Optional
11 | import duckdb
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\routers\alerts.py:29:17
   |
27 |     limit: int = Query(50, ge=1, le=500, description="Maximum number of leads to return"),
28 |     min_risk_score: float = Query(0.0, ge=0.0, le=100.0, description="Minimum risk score threshold"),
29 |     risk_level: Optional[str] = Query(None, description="Filter by risk tier: CRITICAL, HIGH, MEDIUM, LOW"),
   |                 ^^^^^^^^^^^^^
30 | ):
31 |     """
   |
help: Convert to `X | None`
   |
28 |     min_risk_score: float = Query(0.0, ge=0.0, le=100.0, description="Minimum risk score threshold"),
   -     risk_level: Optional[str] = Query(None, description="Filter by risk tier: CRITICAL, HIGH, MEDIUM, LOW"),
29 +     risk_level: str | None = Query(None, description="Filter by risk tier: CRITICAL, HIGH, MEDIUM, LOW"),
30 | ):
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\routers\alerts.py:63:12
   |
61 |         ).fetch_df()
62 |
63 |     items: List[AlertItem] = []
   |            ^^^^
64 |     for _, r in df_results.iterrows():
65 |         reasons_list = json.loads(r["reasons_json"]) if r["reasons_json"] else []
   |
help: Replace with `list`
   |
62 |
   -     items: List[AlertItem] = []
63 +     items: list[AlertItem] = []
64 |     for _, r in df_results.iterrows():
   |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\routers\analysis.py:9:1
   |
 7 |   """
 8 |
 9 | / from fastapi import APIRouter, HTTPException, status
10 | | from app.ml.analyzer import (
11 | |     AnalysisStatusResponse,
12 | |     AnalysisSummary,
13 | |     get_analysis_status,
14 | |     run_full_analysis,
15 | | )
16 | | from app.pipeline.storage import has_normalized_data
   | |____________________________________________________^
17 |
18 |   router = APIRouter()
   |
help: Organize imports
   |
8  |
   - from fastapi import APIRouter, HTTPException, status
9  | from app.ml.analyzer import (
--------------------------------------------------------------------------------
15 | from app.pipeline.storage import has_normalized_data
16 + from fastapi import APIRouter, HTTPException, status
17 |
   |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\routers\datasets.py:1:1
   |
 1 | / from datetime import datetime, timezone
 2 | | import json
 3 | | import logging
 4 | | from pathlib import Path
 5 | | import time
 6 | | from typing import Any, Dict, List, Optional
 7 | | from fastapi import APIRouter, File, HTTPException, UploadFile, status
 8 | |
 9 | | from app.graph.builder import (
10 | |     build_investigation_graph,
11 | |     get_graph_stats,
12 | |     has_graph_data,
13 | |     invalidate_graph_cache,
14 | | )
15 | | from app.ml.analyzer import (
16 | |     get_analysis_paths,
17 | |     has_analysis_data,
18 | |     run_full_analysis,
19 | | )
20 | | from app.pipeline.loader import (
21 | |     calculate_dataset_summary,
22 | |     parse_csv_content,
23 | |     parse_json_content,
24 | | )
25 | | from app.pipeline.normalizer import normalize_dataset
26 | | from app.pipeline.storage import (
27 | |     get_dataset_analytics_summary,
28 | |     get_storage_dir,
29 | |     has_normalized_data,
30 | |     save_normalized_tables,
31 | | )
32 | | from app.schemas.transaction import (
33 | |     ActiveDatasetStatus,
34 | |     BitcoinTransactionRecord,
35 | |     DatasetUploadResponse,
36 | |     StorageInfo,
37 | | )
   | |_^
38 |
39 |   router = APIRouter()
   |
help: Organize imports
   |
   - from datetime import datetime, timezone
1  | import json
2  | import logging
3  + import time
4  + from datetime import datetime, timezone
5  | from pathlib import Path
   - import time
6  | from typing import Any, Dict, List, Optional
   - from fastapi import APIRouter, File, HTTPException, UploadFile, status
7  |
--------------------------------------------------------------------------------
36 | )
37 + from fastapi import APIRouter, File, HTTPException, UploadFile, status
38 |
   |

UP035 `typing.Dict` is deprecated, use `dict` instead
 --> backend\app\routers\datasets.py:6:1
  |
4 | from pathlib import Path
5 | import time
6 | from typing import Any, Dict, List, Optional
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
7 | from fastapi import APIRouter, File, HTTPException, UploadFile, status
  |

UP035 `typing.List` is deprecated, use `list` instead
 --> backend\app\routers\datasets.py:6:1
  |
4 | from pathlib import Path
5 | import time
6 | from typing import Any, Dict, List, Optional
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
7 | from fastapi import APIRouter, File, HTTPException, UploadFile, status
  |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\routers\datasets.py:47:20
   |
46 | def process_dataset_end_to_end(
47 |     valid_records: List[BitcoinTransactionRecord],
   |                    ^^^^
48 |     filename: str,
49 |     detected_format: str,
   |
help: Replace with `list`
   |
46 | def process_dataset_end_to_end(
   -     valid_records: List[BitcoinTransactionRecord],
47 +     valid_records: list[BitcoinTransactionRecord],
48 |     filename: str,
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\routers\datasets.py:51:23
   |
49 |     detected_format: str,
50 |     total_rows: int,
51 |     rejected_records: List[Dict[str, Any]],
   |                       ^^^^
52 |     validation_status: str,
53 |     val_ms: float,
   |
help: Replace with `list`
   |
50 |     total_rows: int,
   -     rejected_records: List[Dict[str, Any]],
51 +     rejected_records: list[Dict[str, Any]],
52 |     validation_status: str,
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\routers\datasets.py:51:28
   |
49 |     detected_format: str,
50 |     total_rows: int,
51 |     rejected_records: List[Dict[str, Any]],
   |                            ^^^^
52 |     validation_status: str,
53 |     val_ms: float,
   |
help: Replace with `dict`
   |
50 |     total_rows: int,
   -     rejected_records: List[Dict[str, Any]],
51 +     rejected_records: List[dict[str, Any]],
52 |     validation_status: str,
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\routers\datasets.py:65:19
   |
64 |     summary = calculate_dataset_summary(valid_records) if valid_records else None
65 |     storage_info: Optional[StorageInfo] = None
   |                   ^^^^^^^^^^^^^^^^^^^^^
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
67 |     analysis_dict: Optional[Dict[str, Any]] = None
   |
help: Convert to `X | None`
   |
64 |     summary = calculate_dataset_summary(valid_records) if valid_records else None
   -     storage_info: Optional[StorageInfo] = None
65 +     storage_info: StorageInfo | None = None
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\routers\datasets.py:66:20
   |
64 |     summary = calculate_dataset_summary(valid_records) if valid_records else None
65 |     storage_info: Optional[StorageInfo] = None
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
   |                    ^^^^
67 |     analysis_dict: Optional[Dict[str, Any]] = None
68 |     graph_dict: Optional[Dict[str, Any]] = None
   |
help: Replace with `dict`
   |
65 |     storage_info: Optional[StorageInfo] = None
   -     stage_timings: Dict[str, Any] = {"validation": val_ms}
66 +     stage_timings: dict[str, Any] = {"validation": val_ms}
67 |     analysis_dict: Optional[Dict[str, Any]] = None
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\routers\datasets.py:67:20
   |
65 |     storage_info: Optional[StorageInfo] = None
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
67 |     analysis_dict: Optional[Dict[str, Any]] = None
   |                    ^^^^^^^^^^^^^^^^^^^^^^^^
68 |     graph_dict: Optional[Dict[str, Any]] = None
69 |     pipeline_status = "SUCCESS"
   |
help: Convert to `X | None`
   |
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
   -     analysis_dict: Optional[Dict[str, Any]] = None
67 +     analysis_dict: Dict[str, Any] | None = None
68 |     graph_dict: Optional[Dict[str, Any]] = None
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\routers\datasets.py:67:29
   |
65 |     storage_info: Optional[StorageInfo] = None
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
67 |     analysis_dict: Optional[Dict[str, Any]] = None
   |                             ^^^^
68 |     graph_dict: Optional[Dict[str, Any]] = None
69 |     pipeline_status = "SUCCESS"
   |
help: Replace with `dict`
   |
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
   -     analysis_dict: Optional[Dict[str, Any]] = None
67 +     analysis_dict: Optional[dict[str, Any]] = None
68 |     graph_dict: Optional[Dict[str, Any]] = None
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\routers\datasets.py:68:17
   |
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
67 |     analysis_dict: Optional[Dict[str, Any]] = None
68 |     graph_dict: Optional[Dict[str, Any]] = None
   |                 ^^^^^^^^^^^^^^^^^^^^^^^^
69 |     pipeline_status = "SUCCESS"
   |
help: Convert to `X | None`
   |
67 |     analysis_dict: Optional[Dict[str, Any]] = None
   -     graph_dict: Optional[Dict[str, Any]] = None
68 +     graph_dict: Dict[str, Any] | None = None
69 |     pipeline_status = "SUCCESS"
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\routers\datasets.py:68:26
   |
66 |     stage_timings: Dict[str, Any] = {"validation": val_ms}
67 |     analysis_dict: Optional[Dict[str, Any]] = None
68 |     graph_dict: Optional[Dict[str, Any]] = None
   |                          ^^^^
69 |     pipeline_status = "SUCCESS"
   |
help: Replace with `dict`
   |
67 |     analysis_dict: Optional[Dict[str, Any]] = None
   -     graph_dict: Optional[Dict[str, Any]] = None
68 +     graph_dict: Optional[dict[str, Any]] = None
69 |     pipeline_status = "SUCCESS"
   |

UP017 [*] Use `datetime.UTC` alias
   --> backend\app\routers\datasets.py:143:45
    |
141 |                 "graph_edges": graph_dict["total_edges"],
142 |                 "stage_timings_ms": stage_timings,
143 |                 "analyzed_at": datetime.now(timezone.utc).isoformat(),
    |                                             ^^^^^^^^^^^^
144 |             }
145 |             try:
    |
help: Convert to `datetime.UTC` alias
    |
    - from datetime import datetime, timezone
1   + from datetime import datetime, timezone, UTC
2   | import json
--------------------------------------------------------------------------------
142 |                 "stage_timings_ms": stage_timings,
    -                 "analyzed_at": datetime.now(timezone.utc).isoformat(),
143 +                 "analyzed_at": datetime.now(UTC).isoformat(),
144 |             }
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\routers\datasets.py:148:20
    |
146 |                 with open(MANIFEST_FILE, "w", encoding="utf-8") as mf:
147 |                     json.dump(manifest_payload, mf, indent=2)
148 |             except Exception:
    |                    ^^^^^^^^^
149 |                 logging.getLogger(__name__).warning("Could not persist dataset manifest")
    |

B008 Do not perform function call `File` in argument defaults; instead, perform the call within the function, or read the default from a module-level singleton variable
   --> backend\app\routers\datasets.py:175:24
    |
173 | @router.post("/upload", response_model=DatasetUploadResponse, status_code=status.HTTP_200_OK)
174 | async def upload_dataset(
175 |     file: UploadFile = File(..., description="Bitcoin transaction dataset (.csv or .json)")
    |                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
176 | ):
177 |     """
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\routers\datasets.py:310:16
    |
308 |                 data = json.load(mf)
309 |                 return ActiveDatasetStatus(**data)
310 |         except Exception:
    |                ^^^^^^^^^
311 |             logging.getLogger(__name__).warning("Could not read dataset manifest")
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\routers\datasets.py:336:16
    |
334 |                 analyzed_at=analysis_summary.get("analyzed_at"),
335 |             )
336 |         except Exception:
    |                ^^^^^^^^^
337 |             logging.getLogger(__name__).warning("Could not read analysis summary")
    |

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> backend\app\routers\graph.py:12:1
   |
10 | """
11 |
12 | from typing import Any, Dict, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 | from fastapi import APIRouter, HTTPException, Query, status
   |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\routers\graph.py:12:1
   |
10 |   """
11 |
12 | / from typing import Any, Dict, Optional
13 | | from fastapi import APIRouter, HTTPException, Query, status
14 | |
15 | | from app.graph.builder import get_graph_stats, load_or_build_graph
16 | | from app.graph.queries import (
17 | |     find_shortest_path,
18 | |     get_entity_details,
19 | |     get_neighborhood_subgraph,
20 | |     search_entities,
21 | | )
22 | | from app.schemas.graph import (
23 | |     GraphPathResponse,
24 | |     GraphSearchResponse,
25 | |     GraphStatsResponse,
26 | |     GraphSubgraphResponse,
27 | | )
   | |_^
28 |
29 |   router = APIRouter()
   |
help: Organize imports
   |
12 | from typing import Any, Dict, Optional
   - from fastapi import APIRouter, HTTPException, Query, status
13 |
--------------------------------------------------------------------------------
26 | )
27 + from fastapi import APIRouter, HTTPException, Query, status
28 |
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\routers\graph.py:32:42
   |
32 | @router.get("/demo-root", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
   |                                          ^^^^
33 | def get_demo_root():
34 |     """
   |
help: Replace with `dict`
   |
31 |
   - @router.get("/demo-root", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
32 + @router.get("/demo-root", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
33 | def get_demo_root():
   |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\routers\graph.py:40:9
   |
38 |       try:
39 |           graph = load_or_build_graph()
40 | /         from app.ml.analyzer import get_analysis_paths, has_analysis_data
41 | |         import polars as pl
   | |___________________________^
42 |           if has_analysis_data():
43 |               leads_path = get_analysis_paths()["leads"]
   |
help: Organize imports
   |
39 |         graph = load_or_build_graph()
40 +         import polars as pl
41 |         from app.ml.analyzer import get_analysis_paths, has_analysis_data
   -         import polars as pl
42 |         if has_analysis_data():
   |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\routers\graph.py:180:21
    |
178 |     hops: int = Query(1, ge=1, le=3, description="Neighborhood traversal depth (1 to 3 hops)"),
179 |     max_nodes: int = Query(100, ge=5, le=500, description="Maximum nodes cap to prevent visual overload"),
180 |     min_risk_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Filter neighboring wallets by minimum risk score"),
    |                     ^^^^^^^^^^^^^^^
181 |     risk_level: Optional[str] = Query(None, description="Filter neighboring wallets by tier: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'"),
182 | ):
    |
help: Convert to `X | None`
    |
179 |     max_nodes: int = Query(100, ge=5, le=500, description="Maximum nodes cap to prevent visual overload"),
    -     min_risk_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Filter neighboring wallets by minimum risk score"),
180 +     min_risk_score: float | None = Query(None, ge=0.0, le=100.0, description="Filter neighboring wallets by minimum risk score"),
181 |     risk_level: Optional[str] = Query(None, description="Filter neighboring wallets by tier: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'"),
    |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\routers\graph.py:181:17
    |
179 |     max_nodes: int = Query(100, ge=5, le=500, description="Maximum nodes cap to prevent visual overload"),
180 |     min_risk_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Filter neighboring wallets by minimum risk score"),
181 |     risk_level: Optional[str] = Query(None, description="Filter neighboring wallets by tier: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'"),
    |                 ^^^^^^^^^^^^^
182 | ):
183 |     """
    |
help: Convert to `X | None`
    |
180 |     min_risk_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Filter neighboring wallets by minimum risk score"),
    -     risk_level: Optional[str] = Query(None, description="Filter neighboring wallets by tier: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'"),
181 +     risk_level: str | None = Query(None, description="Filter neighboring wallets by tier: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'"),
182 | ):
    |

UP006 [*] Use `dict` instead of `Dict` for type annotation
   --> backend\app\routers\graph.py:217:44
    |
217 | @router.get("/{entity_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
    |                                            ^^^^
218 | def entity_detail(entity_id: str):
219 |     """
    |
help: Replace with `dict`
    |
216 |
    - @router.get("/{entity_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
217 + @router.get("/{entity_id}", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
218 | def entity_detail(entity_id: str):
    |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\routers\investigations.py:16:1
   |
14 |   """
15 |
16 | / import json
17 | | from typing import Any, Dict, List, Optional
18 | | import duckdb
19 | | from fastapi import APIRouter, HTTPException, Query, status
20 | |
21 | | from app.ml.analyzer import get_analysis_paths, has_analysis_data
22 | | from app.pipeline.storage import get_parquet_paths, has_normalized_data
23 | | from app.schemas.investigation import (
24 | |     EvidenceItem,
25 | |     InvestigationGraphSummary,
26 | |     InvestigationNetworkObservation,
27 | |     InvestigationTransaction,
28 | |     RiskDossier,
29 | |     WalletInvestigationResponse,
30 | |     WalletSummary,
31 | | )
   | |_^
32 |
33 |   router = APIRouter()
   |
help: Organize imports
   |
17 | from typing import Any, Dict, List, Optional
18 +
19 | import duckdb
   - from fastapi import APIRouter, HTTPException, Query, status
   -
20 | from app.ml.analyzer import get_analysis_paths, has_analysis_data
--------------------------------------------------------------------------------
30 | )
31 + from fastapi import APIRouter, HTTPException, Query, status
32 |
   |

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> backend\app\routers\investigations.py:17:1
   |
16 | import json
17 | from typing import Any, Dict, List, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
18 | import duckdb
19 | from fastapi import APIRouter, HTTPException, Query, status
   |

UP035 `typing.List` is deprecated, use `list` instead
  --> backend\app\routers\investigations.py:17:1
   |
16 | import json
17 | from typing import Any, Dict, List, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
18 | import duckdb
19 | from fastapi import APIRouter, HTTPException, Query, status
   |

F401 [*] `typing.Any` imported but unused
  --> backend\app\routers\investigations.py:17:20
   |
16 | import json
17 | from typing import Any, Dict, List, Optional
   |                    ^^^
18 | import duckdb
19 | from fastapi import APIRouter, HTTPException, Query, status
   |
help: Remove unused import
   |
16 | import json
   - from typing import Any, Dict, List, Optional
17 + from typing import List, Optional
18 | import duckdb
   |

F401 [*] `typing.Dict` imported but unused
  --> backend\app\routers\investigations.py:17:25
   |
16 | import json
17 | from typing import Any, Dict, List, Optional
   |                         ^^^^
18 | import duckdb
19 | from fastapi import APIRouter, HTTPException, Query, status
   |
help: Remove unused import
   |
16 | import json
   - from typing import Any, Dict, List, Optional
17 + from typing import List, Optional
18 | import duckdb
   |

UP045 [*] Use `X | None` for type annotations
   --> backend\app\routers\investigations.py:107:19
    |
106 |     # 2. Risk & Why-Flagged evidence from investigative leads
107 |     risk_dossier: Optional[RiskDossier] = None
    |                   ^^^^^^^^^^^^^^^^^^^^^
108 |     evidence_items: List[EvidenceItem] = []
    |
help: Convert to `X | None`
    |
106 |     # 2. Risk & Why-Flagged evidence from investigative leads
    -     risk_dossier: Optional[RiskDossier] = None
107 +     risk_dossier: RiskDossier | None = None
108 |     evidence_items: List[EvidenceItem] = []
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\routers\investigations.py:108:21
    |
106 |     # 2. Risk & Why-Flagged evidence from investigative leads
107 |     risk_dossier: Optional[RiskDossier] = None
108 |     evidence_items: List[EvidenceItem] = []
    |                     ^^^^
109 |
110 |     if has_analysis_data():
    |
help: Replace with `list`
    |
107 |     risk_dossier: Optional[RiskDossier] = None
    -     evidence_items: List[EvidenceItem] = []
108 +     evidence_items: list[EvidenceItem] = []
109 |
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\routers\investigations.py:156:16
    |
154 |                         feature=r.get("feature"),
155 |                     ))
156 |         except Exception:
    |                ^^^^^^^^^
157 |             # If leads table is unreadable, proceed gracefully without failing the entire dossier
158 |             risk_dossier = None
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\routers\investigations.py:181:23
    |
179 |         tx_df = con.execute(tx_query, [tx_path, clean_id, clean_id, tx_limit]).fetch_df()
180 |
181 |         transactions: List[InvestigationTransaction] = []
    |                       ^^^^
182 |         for _, tr in tx_df.iterrows():
183 |             in_addrs = [str(a) for a in tr["input_addresses"]] if tr["input_addresses"] is not None else []
    |
help: Replace with `list`
    |
180 |
    -         transactions: List[InvestigationTransaction] = []
181 +         transactions: list[InvestigationTransaction] = []
182 |         for _, tr in tx_df.iterrows():
    |

UP006 [*] Use `list` instead of `List` for type annotation
   --> backend\app\routers\investigations.py:233:22
    |
231 |         net_df = con.execute(net_query, [net_path, tx_path, clean_id, clean_id, net_limit]).fetch_df()
232 |
233 |         network_obs: List[InvestigationNetworkObservation] = []
    |                      ^^^^
234 |         for _, nr in net_df.iterrows():
235 |             network_obs.append(InvestigationNetworkObservation(
    |
help: Replace with `list`
    |
232 |
    -         network_obs: List[InvestigationNetworkObservation] = []
233 +         network_obs: list[InvestigationNetworkObservation] = []
234 |         for _, nr in net_df.iterrows():
    |

BLE001 Do not catch blind exception: `Exception`
   --> backend\app\routers\investigations.py:291:12
    |
289 |                 country_count=0,
290 |             )
291 |     except Exception:
    |            ^^^^^^^^^
292 |         # Graceful fallback to table telemetry if graph layer is uninitialized
293 |         graph_summary = InvestigationGraphSummary(
    |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\routers\models.py:6:1
   |
 4 |   """
 5 |
 6 | / import json
 7 | | from pathlib import Path
 8 | | from typing import Dict, List, Literal
 9 | | from fastapi import APIRouter
10 | | from pydantic import BaseModel
   | |______________________________^
11 |
12 |   router = APIRouter()
   |
help: Organize imports
   |
8  | from typing import Dict, List, Literal
9  +
10 | from fastapi import APIRouter
   |

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> backend\app\routers\models.py:8:1
   |
 6 | import json
 7 | from pathlib import Path
 8 | from typing import Dict, List, Literal
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 9 | from fastapi import APIRouter
10 | from pydantic import BaseModel
   |

UP035 `typing.List` is deprecated, use `list` instead
  --> backend\app\routers\models.py:8:1
   |
 6 | import json
 7 | from pathlib import Path
 8 | from typing import Dict, List, Literal
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 9 | from fastapi import APIRouter
10 | from pydantic import BaseModel
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\routers\models.py:25:15
   |
24 | class ModelFeaturesResponse(BaseModel):
25 |     features: List[ModelFeatureImportance]
   |               ^^^^
help: Replace with `list`
   |
24 | class ModelFeaturesResponse(BaseModel):
   -     features: List[ModelFeatureImportance]
25 +     features: list[ModelFeatureImportance]
26 |
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\routers\models.py:42:25
   |
40 |     evaluated_at: str
41 |     evaluation_methodology: str
42 |     class_distribution: Dict[str, int]
   |                         ^^^^
43 |     confusion_matrix: List[List[int]]
44 |     confusion_matrix_labels: List[str]
   |
help: Replace with `dict`
   |
41 |     evaluation_methodology: str
   -     class_distribution: Dict[str, int]
42 +     class_distribution: dict[str, int]
43 |     confusion_matrix: List[List[int]]
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\routers\models.py:43:23
   |
41 |     evaluation_methodology: str
42 |     class_distribution: Dict[str, int]
43 |     confusion_matrix: List[List[int]]
   |                       ^^^^
44 |     confusion_matrix_labels: List[str]
   |
help: Replace with `list`
   |
42 |     class_distribution: Dict[str, int]
   -     confusion_matrix: List[List[int]]
43 +     confusion_matrix: list[List[int]]
44 |     confusion_matrix_labels: List[str]
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\routers\models.py:43:28
   |
41 |     evaluation_methodology: str
42 |     class_distribution: Dict[str, int]
43 |     confusion_matrix: List[List[int]]
   |                            ^^^^
44 |     confusion_matrix_labels: List[str]
   |
help: Replace with `list`
   |
42 |     class_distribution: Dict[str, int]
   -     confusion_matrix: List[List[int]]
43 +     confusion_matrix: List[list[int]]
44 |     confusion_matrix_labels: List[str]
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\routers\models.py:44:30
   |
42 |     class_distribution: Dict[str, int]
43 |     confusion_matrix: List[List[int]]
44 |     confusion_matrix_labels: List[str]
   |                              ^^^^
help: Replace with `list`
   |
43 |     confusion_matrix: List[List[int]]
   -     confusion_matrix_labels: List[str]
44 +     confusion_matrix_labels: list[str]
45 |
   |

UP035 `typing.Dict` is deprecated, use `dict` instead
 --> backend\app\schemas\analysis.py:8:1
  |
6 | """
7 |
8 | from typing import Any, Dict, List, Optional
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
9 | from pydantic import BaseModel, Field
  |

UP035 `typing.List` is deprecated, use `list` instead
 --> backend\app\schemas\analysis.py:8:1
  |
6 | """
7 |
8 | from typing import Any, Dict, List, Optional
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
9 | from pydantic import BaseModel, Field
  |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\app\schemas\analysis.py:8:1
   |
 6 |   """
 7 |
 8 | / from typing import Any, Dict, List, Optional
 9 | | from pydantic import BaseModel, Field
10 | |
11 | | from app.ml.evidence import EvidenceReason
   | |__________________________________________^
help: Organize imports
   |
8  | from typing import Any, Dict, List, Optional
   - from pydantic import BaseModel, Field
9  |
10 | from app.ml.evidence import EvidenceReason
11 + from pydantic import BaseModel, Field
12 |
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\schemas\analysis.py:26:19
   |
24 |     model_type: str = "IsolationForest"
25 |     analysis_duration_seconds: float
26 |     output_files: Dict[str, str]
   |                   ^^^^
27 |     # Phase 9 extensions:
28 |     clustering_enabled: bool = True
   |
help: Replace with `dict`
   |
25 |     analysis_duration_seconds: float
   -     output_files: Dict[str, str]
26 +     output_files: dict[str, str]
27 |     # Phase 9 extensions:
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\schemas\analysis.py:31:26
   |
29 |     cluster_count: int = 6
30 |     clustered_wallets: int = 0
31 |     silhouette_score_k6: Optional[float] = None
   |                          ^^^^^^^^^^^^^^^
32 |     clustering_runtime_ms: float = 0.0
   |
help: Convert to `X | None`
   |
30 |     clustered_wallets: int = 0
   -     silhouette_score_k6: Optional[float] = None
31 +     silhouette_score_k6: float | None = None
32 |     clustering_runtime_ms: float = 0.0
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\schemas\analysis.py:38:18
   |
36 |     """Status metadata for existing analysis results on disk."""
37 |     has_analysis: bool
38 |     analyzed_at: Optional[str] = None
   |                  ^^^^^^^^^^^^^
39 |     wallets_analyzed: int = 0
40 |     anomalies_detected: int = 0
   |
help: Convert to `X | None`
   |
37 |     has_analysis: bool
   -     analyzed_at: Optional[str] = None
38 +     analyzed_at: str | None = None
39 |     wallets_analyzed: int = 0
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\schemas\analysis.py:43:17
   |
41 |     high_risk_leads: int = 0
42 |     critical_risk_leads: int = 0
43 |     model_type: Optional[str] = None
   |                 ^^^^^^^^^^^^^
44 |     cluster_count: Optional[int] = None
   |
help: Convert to `X | None`
   |
42 |     critical_risk_leads: int = 0
   -     model_type: Optional[str] = None
43 +     model_type: str | None = None
44 |     cluster_count: Optional[int] = None
   |

UP045 [*] Use `X | None` for type annotations
  --> backend\app\schemas\analysis.py:44:20
   |
42 |     critical_risk_leads: int = 0
43 |     model_type: Optional[str] = None
44 |     cluster_count: Optional[int] = None
   |                    ^^^^^^^^^^^^^
help: Convert to `X | None`
   |
43 |     model_type: Optional[str] = None
   -     cluster_count: Optional[int] = None
44 +     cluster_count: int | None = None
45 |
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\schemas\analysis.py:68:12
   |
66 |     filtered_count: int
67 |     returned_count: int
68 |     leads: List[AlertItem]
   |            ^^^^
help: Replace with `list`
   |
67 |     returned_count: int
   -     leads: List[AlertItem]
68 +     leads: list[AlertItem]
69 |
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\schemas\analysis.py:80:16
   |
78 |     anomaly_score: float
79 |     anomaly_percentile: float
80 |     subscores: Dict[str, float]
   |                ^^^^
81 |     reasons: List[EvidenceReason]
82 |     feature_metrics: Dict[str, Any]
   |
help: Replace with `dict`
   |
79 |     anomaly_percentile: float
   -     subscores: Dict[str, float]
80 +     subscores: dict[str, float]
81 |     reasons: List[EvidenceReason]
   |

UP006 [*] Use `list` instead of `List` for type annotation
  --> backend\app\schemas\analysis.py:81:14
   |
79 |     anomaly_percentile: float
80 |     subscores: Dict[str, float]
81 |     reasons: List[EvidenceReason]
   |              ^^^^
82 |     feature_metrics: Dict[str, Any]
83 |     transaction_summary: Dict[str, Any]
   |
help: Replace with `list`
   |
80 |     subscores: Dict[str, float]
   -     reasons: List[EvidenceReason]
81 +     reasons: list[EvidenceReason]
82 |     feature_metrics: Dict[str, Any]
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\schemas\analysis.py:82:22
   |
80 |     subscores: Dict[str, float]
81 |     reasons: List[EvidenceReason]
82 |     feature_metrics: Dict[str, Any]
   |                      ^^^^
83 |     transaction_summary: Dict[str, Any]
84 |     network_summary: Dict[str, Any]
   |
help: Replace with `dict`
   |
81 |     reasons: List[EvidenceReason]
   -     feature_metrics: Dict[str, Any]
82 +     feature_metrics: dict[str, Any]
83 |     transaction_summary: Dict[str, Any]
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\schemas\analysis.py:83:26
   |
81 |     reasons: List[EvidenceReason]
82 |     feature_metrics: Dict[str, Any]
83 |     transaction_summary: Dict[str, Any]
   |                          ^^^^
84 |     network_summary: Dict[str, Any]
   |
help: Replace with `dict`
   |
82 |     feature_metrics: Dict[str, Any]
   -     transaction_summary: Dict[str, Any]
83 +     transaction_summary: dict[str, Any]
84 |     network_summary: Dict[str, Any]
   |

UP006 [*] Use `dict` instead of `Dict` for type annotation
  --> backend\app\schemas\analysis.py:84:22
   |
82 |     feature_metrics: Dict[str, Any]
83 |     transaction_summary: Dict[str, Any]
84 |     network_summary: Dict[str, Any]
   |                      ^^^^
help: Replace with `dict`
   |
83 |     transaction_summary: Dict[str, Any]
   -     network_summary: Dict[str, Any]
84 +     network_summary: dict[str, Any]
   |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\scripts\verify_phase3.py:26:1
   |
24 |   """
25 |
26 | / import os
27 | | import shutil
28 | | import csv
29 | | import json
30 | | from decimal import Decimal
31 | | import sys
32 | | import tempfile
33 | | from pathlib import Path
   | |________________________^
34 |
35 |   # Add backend directory to sys.path so app modules can be imported
   |
help: Organize imports
   |
25 |
26 + import csv
27 + import json
28 | import os
29 | import shutil
   - import csv
   - import json
   - from decimal import Decimal
30 | import sys
31 | import tempfile
32 + from decimal import Decimal
33 | from pathlib import Path
   |

F401 [*] `os` imported but unused
  --> backend\scripts\verify_phase3.py:26:8
   |
24 | """
25 |
26 | import os
   |        ^^
27 | import shutil
28 | import csv
   |
help: Remove unused import: `os`
   |
25 |
   - import os
26 | import shutil
   |

F401 [*] `shutil` imported but unused
  --> backend\scripts\verify_phase3.py:27:8
   |
26 | import os
27 | import shutil
   |        ^^^^^^
28 | import csv
29 | import json
   |
help: Remove unused import: `shutil`
   |
26 | import os
   - import shutil
27 | import csv
   |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\scripts\verify_phase3.py:40:1
   |
38 |       sys.path.insert(0, str(backend_dir))
39 |
40 | / import duckdb
41 | | import polars as pl
42 | | from fastapi.testclient import TestClient
43 | | from app.main import app
44 | | from app.pipeline.loader import load_transactions
45 | | from app.pipeline.normalizer import normalize_dataset
46 | | from app.pipeline.storage import (
47 | |     DEFAULT_STORAGE_DIR,
48 | |     get_dataset_analytics_summary,
49 | |     get_network_observation_count,
50 | |     get_parquet_paths,
51 | |     get_time_range,
52 | |     get_top_wallets_by_tx_count,
53 | |     get_top_wallets_by_volume,
54 | |     get_total_transaction_volume,
55 | |     get_transaction_count,
56 | |     get_unique_ip_count,
57 | |     get_wallet_count,
58 | |     has_normalized_data,
59 | |     save_normalized_tables,
60 | | )
   | |_^
help: Organize imports
   |
41 | import polars as pl
   - from fastapi.testclient import TestClient
42 | from app.main import app
--------------------------------------------------------------------------------
59 | )
60 + from fastapi.testclient import TestClient
61 |
   |

F401 [*] `duckdb` imported but unused
  --> backend\scripts\verify_phase3.py:40:8
   |
38 |     sys.path.insert(0, str(backend_dir))
39 |
40 | import duckdb
   |        ^^^^^^
41 | import polars as pl
42 | from fastapi.testclient import TestClient
   |
help: Remove unused import: `duckdb`
   |
39 |
   - import duckdb
40 | import polars as pl
   |

F401 [*] `app.pipeline.storage.DEFAULT_STORAGE_DIR` imported but unused
  --> backend\scripts\verify_phase3.py:47:5
   |
45 | from app.pipeline.normalizer import normalize_dataset
46 | from app.pipeline.storage import (
47 |     DEFAULT_STORAGE_DIR,
   |     ^^^^^^^^^^^^^^^^^^^
48 |     get_dataset_analytics_summary,
49 |     get_network_observation_count,
   |
help: Remove unused import
   |
46 | from app.pipeline.storage import (
   -     DEFAULT_STORAGE_DIR,
   -     get_dataset_analytics_summary,
47 |     get_network_observation_count,
   |

F401 [*] `app.pipeline.storage.get_dataset_analytics_summary` imported but unused
  --> backend\scripts\verify_phase3.py:48:5
   |
46 | from app.pipeline.storage import (
47 |     DEFAULT_STORAGE_DIR,
48 |     get_dataset_analytics_summary,
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
49 |     get_network_observation_count,
50 |     get_parquet_paths,
   |
help: Remove unused import
   |
46 | from app.pipeline.storage import (
   -     DEFAULT_STORAGE_DIR,
   -     get_dataset_analytics_summary,
47 |     get_network_observation_count,
   |

RUF059 Unpacked variable `json_rejected` is never used
   --> backend\scripts\verify_phase3.py:103:19
    |
101 |     # 2. Normalization with Polars from JSON
102 |     print("\n[Step 2] Verifying JSON Normalization with Polars...")
103 |     json_records, json_rejected = load_transactions(json_file)
    |                   ^^^^^^^^^^^^^
104 |     assert len(json_records) == 5000
105 |     json_tables = normalize_dataset(json_records)
    |
help: Prefix it with an underscore or any other dummy variable pattern
    |
102 |     print("\n[Step 2] Verifying JSON Normalization with Polars...")
    -     json_records, json_rejected = load_transactions(json_file)
103 +     json_records, _json_rejected = load_transactions(json_file)
104 |     assert len(json_records) == 5000
    |
note: This is an unsafe fix and may change runtime behavior

F841 Local variable `written` is assigned to but never used
   --> backend\scripts\verify_phase3.py:115:9
    |
113 |     with tempfile.TemporaryDirectory() as tmpdir:
114 |         test_sdir = Path(tmpdir) / "normalized"
115 |         written = save_normalized_tables(tables, storage_dir=test_sdir)
    |         ^^^^^^^
116 |         paths = get_parquet_paths(test_sdir)
    |
help: Remove assignment to unused variable `written`
    |
114 |         test_sdir = Path(tmpdir) / "normalized"
    -         written = save_normalized_tables(tables, storage_dir=test_sdir)
115 +         save_normalized_tables(tables, storage_dir=test_sdir)
116 |         paths = get_parquet_paths(test_sdir)
    |
note: This is an unsafe fix and may change runtime behavior

PERF102 When using only the values of a dict use the `values()` method
   --> backend\scripts\verify_phase3.py:118:24
    |
116 |         paths = get_parquet_paths(test_sdir)
117 |
118 |         for name, p in paths.items():
    |                        ^^^^^^^^^^^
119 |             assert p.exists(), f"File {p} was not created!"
120 |             assert p.stat().st_size > 0, f"File {p} is empty!"
    |
help: Replace `.items()` with `.values()`
    |
117 |
    -         for name, p in paths.items():
118 +         for p in paths.values():
119 |             assert p.exists(), f"File {p} was not created!"
    |
note: This is an unsafe fix and may change runtime behavior

F841 Local variable `tmp_empty_dir` is assigned to but never used
   --> backend\scripts\verify_phase3.py:210:43
    |
208 |     # 7. Invalid dataset does NOT write Parquet tables
209 |     print("\n[Step 7] Verifying invalid dataset does NOT write normalized tables...")
210 |     with tempfile.TemporaryDirectory() as tmp_empty_dir:
    |                                           ^^^^^^^^^^^^^
211 |         bad_csv = "timestamp,src_ip,dst_ip,src_port,dst_port,txid,input_addresses,output_addresses,input_amounts,output_amounts,fee,s…
212 |         bad_csv += "2026-09-01T00:00:00Z,1.1.1.1,2.2.2.2,50000,8333,0000000000000000000000000000000000000000000000000000000000000001,…
    |
help: Remove assignment to unused variable `tmp_empty_dir`
    |
209 |     print("\n[Step 7] Verifying invalid dataset does NOT write normalized tables...")
    -     with tempfile.TemporaryDirectory() as tmp_empty_dir:
210 +     with tempfile.TemporaryDirectory():
211 |         bad_csv = "timestamp,src_ip,dst_ip,src_port,dst_port,txid,input_addresses,output_addresses,input_amounts,output_amounts,fee,script_type,geo_country,ASN\n"
    |
note: This is an unsafe fix and may change runtime behavior

I001 [*] Import block is un-sorted or un-formatted
  --> backend\scripts\verify_phase5.py:33:1
   |
31 |   """
32 |
33 | / import json
34 | | from pathlib import Path
35 | | import subprocess
36 | | import sys
   | |__________^
37 |
38 |   # Ensure backend root is on sys.path
   |
help: Organize imports
   |
33 | import json
   - from pathlib import Path
34 | import subprocess
35 | import sys
36 + from pathlib import Path
37 |
   |

I001 [*] Import block is un-sorted or un-formatted
  --> backend\scripts\verify_phase5.py:43:1
   |
41 |       sys.path.insert(0, str(backend_dir))
42 |
43 | / from fastapi.testclient import TestClient
44 | | import networkx as nx
45 | | import polars as pl
46 | |
47 | | from app.main import app
48 | | from app.graph.builder import (
49 | |     build_investigation_graph,
50 | |     get_graph_stats,
51 | |     get_graph_storage_paths,
52 | |     has_graph_data,
53 | |     load_or_build_graph,
54 | | )
55 | | from app.graph.queries import (
56 | |     find_shortest_path,
57 | |     get_entity_details,
58 | |     get_neighborhood_subgraph,
59 | |     search_entities,
60 | | )
61 | | from app.pipeline.storage import get_parquet_paths, has_normalized_data
   | |_______________________________________________________________________^
help: Organize imports
   |
42 |
   - from fastapi.testclient import TestClient
43 | import networkx as nx
44 | import polars as pl
   -
   - from app.main import app
45 | from app.graph.builder import (
--------------------------------------------------------------------------------
57 | )
58 + from app.main import app
59 | from app.pipeline.storage import get_parquet_paths, has_normalized_data
60 + from fastapi.testclient import TestClient
61 |
   |

F401 [*] `app.graph.builder.get_graph_stats` imported but unused
  --> backend\scripts\verify_phase5.py:50:5
   |
48 | from app.graph.builder import (
49 |     build_investigation_graph,
50 |     get_graph_stats,
   |     ^^^^^^^^^^^^^^^
51 |     get_graph_storage_paths,
52 |     has_graph_data,
   |
help: Remove unused import
   |
49 |     build_investigation_graph,
   -     get_graph_stats,
50 |     get_graph_storage_paths,
   -     has_graph_data,
   -     load_or_build_graph,
51 | )
   |

F401 [*] `app.graph.builder.has_graph_data` imported but unused
  --> backend\scripts\verify_phase5.py:52:5
   |
50 |     get_graph_stats,
51 |     get_graph_storage_paths,
52 |     has_graph_data,
   |     ^^^^^^^^^^^^^^
53 |     load_or_build_graph,
54 | )
   |
help: Remove unused import
   |
49 |     build_investigation_graph,
   -     get_graph_stats,
50 |     get_graph_storage_paths,
   -     has_graph_data,
   -     load_or_build_graph,
51 | )
   |

F401 [*] `app.graph.builder.load_or_build_graph` imported but unused
  --> backend\scripts\verify_phase5.py:53:5
   |
51 |     get_graph_storage_paths,
52 |     has_graph_data,
53 |     load_or_build_graph,
   |     ^^^^^^^^^^^^^^^^^^^
54 | )
55 | from app.graph.queries import (
   |
help: Remove unused import
   |
49 |     build_investigation_graph,
   -     get_graph_stats,
50 |     get_graph_storage_paths,
   -     has_graph_data,
   -     load_or_build_graph,
51 | )
   |

F401 [*] `app.graph.queries.get_entity_details` imported but unused
  --> backend\scripts\verify_phase5.py:57:5
   |
55 | from app.graph.queries import (
56 |     find_shortest_path,
57 |     get_entity_details,
   |     ^^^^^^^^^^^^^^^^^^
58 |     get_neighborhood_subgraph,
59 |     search_entities,
   |
help: Remove unused import: `app.graph.queries.get_entity_details`
   |
56 |     find_shortest_path,
   -     get_entity_details,
57 |     get_neighborhood_subgraph,
   |

PLW1510 `subprocess.run` without explicit `check` argument
  --> backend\scripts\verify_phase5.py:65:11
   |
64 | def run_cmd(cmd_args, desc):
65 |     res = subprocess.run(cmd_args, capture_output=True, text=True)
   |           ^^^^^^^^^^^^^^
66 |     if res.returncode != 0:
67 |         print(f"FAILED: {desc}")
   |
help: Add explicit `check=False`
   |
64 | def run_cmd(cmd_args, desc):
   -     res = subprocess.run(cmd_args, capture_output=True, text=True)
65 +     res = subprocess.run(cmd_args, check=False, capture_output=True, text=True)
66 |     if res.returncode != 0:
   |
note: This suggestion may be incorrect or produce invalid syntax. It requires manual review and cannot be applied automatically

C401 Unnecessary generator (rewrite as a set comprehension)
   --> backend\scripts\verify_phase5.py:114:18
    |
112 |     # -------------------------------------------------------------
113 |     print("\n[6/24] Verifying Node Types...")
114 |     node_types = set(data.get("type") for _, data in G.nodes(data=True))
    |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
115 |     expected_types = {"wallet", "transaction", "ip", "asn", "country"}
116 |     assert expected_types.issubset(node_types), f"Missing node types: {expected_types - node_types}"
    |
help: Rewrite as a set comprehension
    |
113 |     print("\n[6/24] Verifying Node Types...")
    -     node_types = set(data.get("type") for _, data in G.nodes(data=True))
114 +     node_types = {data.get("type") for _, data in G.nodes(data=True)}
115 |     expected_types = {"wallet", "transaction", "ip", "asn", "country"}
    |
note: This is an unsafe fix and may change runtime behavior

C401 Unnecessary generator (rewrite as a set comprehension)
   --> backend\scripts\verify_phase5.py:124:18
    |
122 |     # -------------------------------------------------------------
123 |     print("\n[7/24] Verifying Edge Types...")
124 |     edge_types = set(data.get("type") for _, _, data in G.edges(data=True))
    |                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
125 |     expected_edge_types = {"input", "output", "counterparty", "network_observation"}
126 |     assert expected_edge_types.issubset(edge_types), f"Missing edge types: {expected_edge_types - edge_types}"
    |
help: Rewrite as a set comprehension
    |
123 |     print("\n[7/24] Verifying Edge Types...")
    -     edge_types = set(data.get("type") for _, _, data in G.edges(data=True))
124 +     edge_types = {data.get("type") for _, _, data in G.edges(data=True)}
125 |     expected_edge_types = {"input", "output", "counterparty", "network_observation"}
    |
note: This is an unsafe fix and may change runtime behavior

F541 [*] f-string without any placeholders
   --> backend\scripts\verify_phase5.py:178:62
    |
176 |     asn_val = sample_tx["ASN"]
177 |     if asn_val:
178 |         assert G.has_edge(f"ip:{src_ip}", f"asn:{asn_val}"), f"Missing IP->ASN edge"
    |                                                              ^^^^^^^^^^^^^^^^^^^^^^^
179 |         assert G.edges[f"ip:{src_ip}", f"asn:{asn_val}"]["type"] == "network_observation"
180 |     print("   [PASS] IP-ASN association edges verified.")
    |
help: Remove extraneous `f` prefix
    |
177 |     if asn_val:
    -         assert G.has_edge(f"ip:{src_ip}", f"asn:{asn_val}"), f"Missing IP->ASN edge"
178 +         assert G.has_edge(f"ip:{src_ip}", f"asn:{asn_val}"), "Missing IP->ASN edge"
179 |         assert G.edges[f"ip:{src_ip}", f"asn:{asn_val}"]["type"] == "network_observation"
    |

F541 [*] f-string without any placeholders
   --> backend\scripts\verify_phase5.py:188:70
    |
186 |     country_val = sample_tx["geo_country"]
187 |     if country_val:
188 |         assert G.has_edge(f"ip:{src_ip}", f"country:{country_val}"), f"Missing IP->Country edge"
    |                                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^
189 |         assert G.edges[f"ip:{src_ip}", f"country:{country_val}"]["type"] == "network_observation"
190 |     print("   [PASS] IP-Country geolocation edges verified.")
    |
help: Remove extraneous `f` prefix
    |
187 |     if country_val:
    -         assert G.has_edge(f"ip:{src_ip}", f"country:{country_val}"), f"Missing IP->Country edge"
188 +         assert G.has_edge(f"ip:{src_ip}", f"country:{country_val}"), "Missing IP->Country edge"
189 |         assert G.edges[f"ip:{src_ip}", f"country:{country_val}"]["type"] == "network_observation"
    |

F541 [*] f-string without any placeholders
   --> backend\scripts\verify_phase5.py:283:11
    |
281 |     assert s_ip.total_matches > 0
282 |     assert any(r.type == "ip" for r in s_ip.results)
283 |     print(f"   [PASS] Search successfully resolves wallets, txids, and IPs.")
    |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
284 |
285 |     # -------------------------------------------------------------
    |
help: Remove extraneous `f` prefix
    |
282 |     assert any(r.type == "ip" for r in s_ip.results)
    -     print(f"   [PASS] Search successfully resolves wallets, txids, and IPs.")
283 +     print("   [PASS] Search successfully resolves wallets, txids, and IPs.")
284 |
    |

PLW1510 `subprocess.run` without explicit `check` argument
   --> backend\scripts\verify_phase5.py:326:18
    |
324 |     # -------------------------------------------------------------
325 |     print("\n[23/24] Verifying Frontend Files are Untouched in Phase 5...")
326 |     git_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
    |                  ^^^^^^^^^^^^^^
327 |     modified_lines = [l for l in git_status.strip().split("\n") if l.strip()]
328 |     frontend_mods = [l for l in modified_lines if "frontend/" in l]
    |
help: Add explicit `check=False`
    |
325 |     print("\n[23/24] Verifying Frontend Files are Untouched in Phase 5...")
    -     git_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
326 +     git_status = subprocess.run(["git", "status", "--porcelain"], check=False, capture_output=True, text=True).stdout
327 |     modified_lines = [l for l in git_status.strip().split("\n") if l.strip()]
    |
note: This suggestion may be incorrect or produce invalid syntax. It requires manual review and cannot be applied automatically

I001 [*] Import block is un-sorted or un-formatted
 --> backend\tests\test_phase0_security.py:2:1
  |
1 |   """Phase 0 API security regressions."""
2 | / from uuid import UUID
3 | | from urllib.parse import quote
4 | |
5 | | import polars as pl
6 | |
7 | | from fastapi.testclient import TestClient
8 | | from app.main import allow_origins, app
9 | | from app.routers import alerts, analysis
  | |________________________________________^
help: Organize imports
  |
1 | """Phase 0 API security regressions."""
2 + from urllib.parse import quote
3 | from uuid import UUID
  - from urllib.parse import quote
4 |
5 | import polars as pl
  -
  - from fastapi.testclient import TestClient
6 | from app.main import allow_origins, app
7 | from app.routers import alerts, analysis
8 + from fastapi.testclient import TestClient
9 |
  |

Found 224 errors.
[*] 184 fixable with `--fix` (6 unsafe fixes available with `--fix --unsafe-fixes`).
Check failed (1): (WindowsPath('D:/NirikshakM/.venv/Scripts/python.exe'), '-m', 'ruff', 'check', 'backend/app/graph/builder.py', 'backend/app/main.py', 'backend/app/ml/__init__.py', 'backend/app/ml/analyzer.py', 'backend/app/ml/anomaly.py', 'backend/app/ml/clustering.py', 'backend/app/ml/evidence.py', 'backend/app/ml/features.py', 'backend/app/ml/risk.py', 'backend/app/pipeline/loader.py', 'backend/app/pipeline/storage.py', 'backend/app/routers/alerts.py', 'backend/app/routers/analysis.py', 'backend/app/routers/clusters.py', 'backend/app/routers/datasets.py', 'backend/app/routers/graph.py', 'backend/app/routers/investigations.py', 'backend/app/routers/models.py', 'backend/app/schemas/analysis.py', 'backend/app/schemas/clustering.py', 'backend/scripts/seed_demo.py', 'backend/scripts/verify_phase3.py', 'backend/scripts/verify_phase5.py', 'scripts/tasks.py', 'backend/tests/test_phase0_security.py')
+ D:\NirikshakM\.venv\Scripts\python.exe -m mypy --explicit-package-bases D:\NirikshakM\backend\app\graph\builder.py D:\NirikshakM\backend\app\main.py D:\NirikshakM\backend\app\ml\__init__.py D:\NirikshakM\backend\app\ml\analyzer.py D:\NirikshakM\backend\app\ml\anomaly.py D:\NirikshakM\backend\app\ml\clustering.py D:\NirikshakM\backend\app\ml\evidence.py D:\NirikshakM\backend\app\ml\features.py D:\NirikshakM\backend\app\ml\risk.py D:\NirikshakM\backend\app\pipeline\loader.py D:\NirikshakM\backend\app\pipeline\storage.py D:\NirikshakM\backend\app\routers\alerts.py D:\NirikshakM\backend\app\routers\analysis.py D:\NirikshakM\backend\app\routers\clusters.py D:\NirikshakM\backend\app\routers\datasets.py D:\NirikshakM\backend\app\routers\graph.py D:\NirikshakM\backend\app\routers\investigations.py D:\NirikshakM\backend\app\routers\models.py D:\NirikshakM\backend\app\schemas\analysis.py D:\NirikshakM\backend\app\schemas\clustering.py D:\NirikshakM\backend\scripts\seed_demo.py D:\NirikshakM\backend\scripts\verify_phase3.py D:\NirikshakM\backend\scripts\verify_phase5.py D:\NirikshakM\scripts\tasks.py D:\NirikshakM\backend\tests\test_phase0_security.py
scripts\generate_dataset.py:101: error: Incompatible default for parameter "start_time" (default has type "None", parameter has type "datetime")  [assignment]
scripts\generate_dataset.py:101: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
scripts\generate_dataset.py:101: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
scripts\generate_dataset.py:218: error: Need type annotation for "anomaly_breakdown" (hint: "anomaly_breakdown: dict[<type>, <type>] = ...")  [var-annotated]
app\graph\serializers.py:9: error: Library stubs not installed for "networkx"  [import-untyped]
app\pipeline\loader.py:65: error: Argument 1 to "float" has incompatible type "str | Any | float | None"; expected "str | Buffer | SupportsFloat | SupportsIndex"  [arg-type]
app\graph\queries.py:14: error: Library stubs not installed for "networkx"  [import-untyped]
app\graph\queries.py:219: error: Incompatible types in assignment (expression has type "str", target has type "float")  [assignment]
app\graph\queries.py:316: error: Incompatible types in assignment (expression has type "str", target has type "None")  [assignment]
app\graph\queries.py:322: error: Incompatible types in assignment (expression has type "None", variable has type "str")  [assignment]
app\pipeline\normalizer.py:63: error: Argument "schema" to "DataFrame" has incompatible type "dict[str, object]"; expected "Mapping[str, DataTypeClass | DataType | type[int] | type[float] | type[bool] | type[str] | type[date] | <9 more items> | None] | Sequence[str | tuple[str, DataTypeClass | DataType | type[int] | type[float] | type[bool] | type[str] | type[date] | <9 more items> | None]] | None"  [arg-type]
app\pipeline\normalizer.py:71: error: Need type annotation for "wallets_info"  [var-annotated]
app\pipeline\normalizer.py:81: error: "object" has no attribute "add"  [attr-defined]
app\pipeline\normalizer.py:82: error: Unsupported operand types for + ("object" and "float")  [operator]
app\pipeline\normalizer.py:83: error: "object" has no attribute "append"  [attr-defined]
app\pipeline\normalizer.py:85: error: "object" has no attribute "add"  [attr-defined]
app\pipeline\normalizer.py:86: error: Unsupported operand types for + ("object" and "float")  [operator]
app\pipeline\normalizer.py:87: error: "object" has no attribute "append"  [attr-defined]
app\pipeline\normalizer.py:92: error: Unsupported left operand type for | ("object")  [operator]
app\pipeline\normalizer.py:96: error: Argument 1 to "len" has incompatible type "object"; expected "Sized"  [arg-type]
app\pipeline\normalizer.py:97: error: Argument 1 to "len" has incompatible type "object"; expected "Sized"  [arg-type]
app\pipeline\normalizer.py:98: error: No overload variant of "round" matches argument types "object", "int"  [call-overload]
app\pipeline\normalizer.py:98: note: Possible overload variants:
app\pipeline\normalizer.py:98: note:     def [_T] round(number: _SupportsRound1[_T], ndigits: None = ...) -> _T
app\pipeline\normalizer.py:98: note:     def [_T] round(number: _SupportsRound2[_T], ndigits: SupportsIndex) -> _T
app\pipeline\normalizer.py:99: error: No overload variant of "round" matches argument types "object", "int"  [call-overload]
app\pipeline\normalizer.py:99: note: Possible overload variants:
app\pipeline\normalizer.py:99: note:     def [_T] round(number: _SupportsRound1[_T], ndigits: None = ...) -> _T
app\pipeline\normalizer.py:99: note:     def [_T] round(number: _SupportsRound2[_T], ndigits: SupportsIndex) -> _T
app\pipeline\normalizer.py:100: error: No overload variant of "min" matches argument type "object"  [call-overload]
app\pipeline\normalizer.py:100: note: Possible overload variants:
app\pipeline\normalizer.py:100: note:     def [SupportsRichComparisonT: SupportsDunderLT[Any] | SupportsDunderGT[Any]] min(SupportsRichComparisonT, SupportsRichComparisonT, /, *_args: SupportsRichComparisonT, key: None = ...) -> SupportsRichComparisonT
app\pipeline\normalizer.py:100: note:     def [_T] min(_T, _T, /, *_args: _T, key: Callable[[_T], SupportsDunderLT[Any] | SupportsDunderGT[Any]]) -> _T
app\pipeline\normalizer.py:100: note:     def [SupportsRichComparisonT: SupportsDunderLT[Any] | SupportsDunderGT[Any]] min(Iterable[SupportsRichComparisonT], /, *, key: None = ...) -> SupportsRichComparisonT
app\pipeline\normalizer.py:100: note:     def [_T] min(Iterable[_T], /, *, key: Callable[[_T], SupportsDunderLT[Any] | SupportsDunderGT[Any]]) -> _T
app\pipeline\normalizer.py:100: note:     def [SupportsRichComparisonT: SupportsDunderLT[Any] | SupportsDunderGT[Any], _T] min(Iterable[SupportsRichComparisonT], /, *, key: None = ..., default: _T) -> SupportsRichComparisonT | _T
app\pipeline\normalizer.py:100: note:     def [_T1, _T2] min(Iterable[_T1], /, *, key: Callable[[_T1], SupportsDunderLT[Any] | SupportsDunderGT[Any]], default: _T2) -> _T1 | _T2
app\pipeline\normalizer.py:101: error: No overload variant of "max" matches argument type "object"  [call-overload]
app\pipeline\normalizer.py:101: note: Possible overload variants:
app\pipeline\normalizer.py:101: note:     def [SupportsRichComparisonT: SupportsDunderLT[Any] | SupportsDunderGT[Any]] max(SupportsRichComparisonT, SupportsRichComparisonT, /, *_args: SupportsRichComparisonT, key: None = ...) -> SupportsRichComparisonT
app\pipeline\normalizer.py:101: note:     def [_T] max(_T, _T, /, *_args: _T, key: Callable[[_T], SupportsDunderLT[Any] | SupportsDunderGT[Any]]) -> _T
app\pipeline\normalizer.py:101: note:     def [SupportsRichComparisonT: SupportsDunderLT[Any] | SupportsDunderGT[Any]] max(Iterable[SupportsRichComparisonT], /, *, key: None = ...) -> SupportsRichComparisonT
app\pipeline\normalizer.py:101: note:     def [_T] max(Iterable[_T], /, *, key: Callable[[_T], SupportsDunderLT[Any] | SupportsDunderGT[Any]]) -> _T
app\pipeline\normalizer.py:101: note:     def [SupportsRichComparisonT: SupportsDunderLT[Any] | SupportsDunderGT[Any], _T] max(Iterable[SupportsRichComparisonT], /, *, key: None = ..., default: _T) -> SupportsRichComparisonT | _T
app\pipeline\normalizer.py:101: note:     def [_T1, _T2] max(Iterable[_T1], /, *, key: Callable[[_T1], SupportsDunderLT[Any] | SupportsDunderGT[Any]], default: _T2) -> _T1 | _T2
app\ml\risk.py:7: error: Library stubs not installed for "scipy.stats"  [import-untyped]
app\graph\builder.py:19: error: Library stubs not installed for "networkx"  [import-untyped]
app\graph\builder.py:19: note: Hint: "python3 -m pip install types-networkx"
app\graph\builder.py:19: note: (or run "mypy --install-types" to install all missing stub packages)
app\graph\builder.py:19: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
app\ml\clustering.py:16: error: Skipping analyzing "sklearn.cluster": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\ml\clustering.py:17: error: Skipping analyzing "sklearn.decomposition": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\ml\clustering.py:18: error: Skipping analyzing "sklearn.metrics": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\ml\clustering.py:19: error: Skipping analyzing "threadpoolctl": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\ml\clustering.py:88: error: Argument "average_risk_score" to "ClusterProfile" has incompatible type "int | float | Decimal | date | time | timedelta | str | bytes | ndarray[Any, Any] | list[Any] | None"; expected "float"  [arg-type]
app\ml\clustering.py:89: error: Argument "anomaly_rate" to "ClusterProfile" has incompatible type "int | float | Decimal | date | time | timedelta | str | bytes | ndarray[Any, Any] | list[Any] | None"; expected "float"  [arg-type]
app\ml\anomaly.py:12: error: Library stubs not installed for "scipy.stats"  [import-untyped]
app\ml\anomaly.py:12: note: Hint: "python3 -m pip install scipy-stubs"
app\ml\anomaly.py:13: error: Skipping analyzing "sklearn.ensemble": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\routers\clusters.py:78: error: Argument "wallets" to "ClusterDetailResponse" has incompatible type "list[dict[str, Any]]"; expected "list[WalletClusterAssignment]"  [arg-type]
app\ml\analyzer.py:55: error: Argument 1 to "float" has incompatible type "int | float | Decimal | date | time | timedelta | str | bytes | ndarray[Any, Any] | list[Any] | None"; expected "str | Buffer | SupportsFloat | SupportsIndex"  [arg-type]
app\routers\investigations.py:163: error: Value of type "tuple[Any, ...] | None" is not indexable  [index]
app\routers\investigations.py:210: error: Value of type "tuple[Any, ...] | None" is not indexable  [index]
app\routers\alerts.py:46: error: Value of type "tuple[Any, ...] | None" is not indexable  [index]
app\routers\alerts.py:47: error: Value of type "tuple[Any, ...] | None" is not indexable  [index]
scripts\verify_phase5.py:44: error: Library stubs not installed for "networkx"  [import-untyped]
Found 40 errors in 14 files (checked 25 source files)
Check failed (1): (WindowsPath('D:/NirikshakM/.venv/Scripts/python.exe'), '-m', 'mypy', '--explicit-package-bases', WindowsPath('D:/NirikshakM/backend/app/graph/builder.py'), WindowsPath('D:/NirikshakM/backend/app/main.py'), WindowsPath('D:/NirikshakM/backend/app/ml/__init__.py'), WindowsPath('D:/NirikshakM/backend/app/ml/analyzer.py'), WindowsPath('D:/NirikshakM/backend/app/ml/anomaly.py'), WindowsPath('D:/NirikshakM/backend/app/ml/clustering.py'), WindowsPath('D:/NirikshakM/backend/app/ml/evidence.py'), WindowsPath('D:/NirikshakM/backend/app/ml/features.py'), WindowsPath('D:/NirikshakM/backend/app/ml/risk.py'), WindowsPath('D:/NirikshakM/backend/app/pipeline/loader.py'), WindowsPath('D:/NirikshakM/backend/app/pipeline/storage.py'), WindowsPath('D:/NirikshakM/backend/app/routers/alerts.py'), WindowsPath('D:/NirikshakM/backend/app/routers/analysis.py'), WindowsPath('D:/NirikshakM/backend/app/routers/clusters.py'), WindowsPath('D:/NirikshakM/backend/app/routers/datasets.py'), WindowsPath('D:/NirikshakM/backend/app/routers/graph.py'), WindowsPath('D:/NirikshakM/backend/app/routers/investigations.py'), WindowsPath('D:/NirikshakM/backend/app/routers/models.py'), WindowsPath('D:/NirikshakM/backend/app/schemas/analysis.py'), WindowsPath('D:/NirikshakM/backend/app/schemas/clustering.py'), WindowsPath('D:/NirikshakM/backend/scripts/seed_demo.py'), WindowsPath('D:/NirikshakM/backend/scripts/verify_phase3.py'), WindowsPath('D:/NirikshakM/backend/scripts/verify_phase5.py'), WindowsPath('D:/NirikshakM/scripts/tasks.py'), WindowsPath('D:/NirikshakM/backend/tests/test_phase0_security.py'))
+ D:\NirikshakM\.venv\Scripts\python.exe -m bandit -r app
[main]	INFO	profile include tests: None
[main]	INFO	profile exclude tests: None
[main]	INFO	cli include tests: None
[main]	INFO	cli exclude tests: None
[main]	INFO	running on Python 3.11.15
Run started:2026-11-26 20:40:56.712293+00:00

Test results:
	No issues identified.

Code scanned:
	Total lines of code: 3461
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
Files skipped (0):
+ D:\NirikshakM\.venv\Scripts\python.exe -m pip_audit
No known vulnerabilities found
+ C:\Program Files\nodejs\npm.cmd run lint

> frontend@0.0.0 lint
> eslint .


D:\NirikshakM\frontend\src\components\WalletInvestigation.tsx
  149:8  warning  React Hook useEffect has a missing dependency: 'fetchDossier'. Either include it or remove the dependency array  react-hooks/exhaustive-deps

D:\NirikshakM\frontend\src\components\graph\GraphPathInvestigator.tsx
  66:8  warning  React Hook useEffect has a missing dependency: 'selectedSource'. Either include it or remove the dependency array  react-hooks/exhaustive-deps

✖ 2 problems (0 errors, 2 warnings)

+ C:\Program Files\nodejs\npm.cmd run build

> frontend@0.0.0 build
> tsc -b && vite build

vite v7.3.8 building client environment for production...
transforming...
✓ 2317 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                     0.50 kB │ gzip:   0.32 kB
dist/assets/index-DeN1LMJ2.css     97.55 kB │ gzip:  15.46 kB
dist/assets/index-Denx1xTR.js   1,956.65 kB │ gzip: 541.47 kB

(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rollupOptions.output.manualChunks to improve chunking: https://rollupjs.org/configuration-options/#output-manualchunks
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.
✓ built in 20.07s
+ C:\Program Files\nodejs\npm.cmd audit --omit=dev --audit-level=high
found 0 vulnerabilities
+ docker compose build backend
 Image nirikshak-backend:latest Building 
#1 [internal] load local bake definitions
#1 reading from stdin 515B done
#1 DONE 0.0s

#2 [internal] load build definition from Dockerfile
#2 transferring dockerfile: 1.30kB 0.0s done
#2 DONE 0.0s

#3 [internal] load metadata for docker.io/library/python:3.11-slim
#3 DONE 0.1s

#4 [internal] load .dockerignore
#4 transferring context: 180B done
#4 DONE 0.0s

#5 [1/6] FROM docker.io/library/python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c
#5 resolve docker.io/library/python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c 0.0s done
#5 DONE 0.0s

#6 [internal] load build context
#6 transferring context: 20.79MB 0.8s done
#6 DONE 0.8s

#7 [2/6] WORKDIR /app
#7 CACHED

#8 [3/6] RUN apt-get update && apt-get install -y --no-install-recommends     curl     && rm -rf /var/lib/apt/lists/*
#8 CACHED

#9 [4/6] COPY requirements*.txt ./
#9 CACHED

#10 [5/6] RUN pip install --no-cache-dir -r requirements-dev.txt
#10 CACHED

#11 [6/6] COPY . .
#11 DONE 0.1s

#12 exporting to image
#12 exporting layers
#12 exporting layers 0.3s done
#12 exporting manifest sha256:9b9336a2529777b1e1310572c5354bb7cd08ecbae2665a0dad0e9e9333d91f4f done
#12 exporting config sha256:9d573b80966e38ccbc156440243bd6209346e7b48a8aad1b0a8bdf08821a3b41 done
#12 exporting attestation manifest sha256:78c4b08680e2879dc3bf8716c8a8be8b38e37904813c46ae794757fa8ef06de3 done
#12 exporting manifest list sha256:33c9f3cb122f7e4333495e6c41164a03edf29076723db6d253a1dd8683d094d7 0.0s done
#12 naming to docker.io/library/nirikshak-backend:latest done
#12 unpacking to docker.io/library/nirikshak-backend:latest 0.1s done
#12 DONE 0.5s

#13 resolving provenance for metadata file
#13 DONE 0.0s
 Image nirikshak-backend:latest Built 
+ docker compose run --rm backend python scripts/seed_demo.py
 Container nirikshakm-backend-run-62f4973b38e9 Creating 
 Container nirikshakm-backend-run-62f4973b38e9 Created 
synthetic: 5000 transactions, 4915 wallets, 10650 graph nodes
+ docker compose run --rm backend pytest -q
 Container nirikshakm-backend-run-5e31b1103f81 Creating 
 Container nirikshakm-backend-run-5e31b1103f81 Created 
...............................................                          [100%]
=============================== warnings summary ===============================
../usr/local/lib/python3.11/site-packages/fastapi/testclient.py:1
  /usr/local/lib/python3.11/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
47 passed, 1 warning in 6.52s
+ docker compose stop
 Container nirikshak_frontend Stopping 
 Container nirikshak_frontend Stopped 
 Container nirikshak_backend Stopping 
 Container nirikshak_backend Stopped 
2 checks failed
~~~~
