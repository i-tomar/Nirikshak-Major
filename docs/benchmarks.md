# Phase 1 ingestion benchmark

Measured on 27 November 2026 with `backend/scripts/benchmark_ingest.py`. The script writes source rows sequentially, then calls `ingest_file` and verifies exact valid/rejected counts. It reports elapsed ingestion time separately from generation time. Peak memory is the operating system's peak working set for the Python process on Windows and `ru_maxrss` peak RSS on Linux. The peak covers generation plus ingestion; source generation itself holds one row at a time. Each case uses a temporary source and output directory, which is removed after the run. `docker compose` sets the backend limit to 12 GB. Output tables contain transactions, wallets, network observations, input and output edges, rejected rows and IP enrichment. The benchmark used supplied synthetic geo/ASN for 250 IPs and offline MMDB for one destination IP.

| Runtime | Rows | Format | Source bytes | Generation s | Ingestion s | Peak process MiB | Valid | Rejected |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Windows | 100,000 | CSV | 20,534,722 | 1.371 | 2.492 | 315.9 | 100,000 | 0 |
| Windows | 100,000 | JSON array | 38,134,627 | 0.814 | 6.661 | 330.7 | 100,000 | 0 |
| Windows | 100,000 | XML | 57,334,609 | 0.994 | 6.346 | 317.7 | 100,000 | 0 |
| Windows | 1,000,000 | CSV | 205,345,942 | 13.760 | 5.702 | 1,926.1 | 1,000,000 | 0 |
| Windows | 1,000,000 | JSON array | 381,345,847 | 7.819 | 47.473 | 1,923.2 | 1,000,000 | 0 |
| Windows | 1,000,000 | XML | 573,345,829 | 9.928 | 51.526 | 2,041.4 | 1,000,000 | 0 |
| Docker Linux, 12 GB limit | 100,000 | CSV | 20,534,722 | 1.194 | 4.398 | 494.4 | 100,000 | 0 |
| Docker Linux, 12 GB limit | 100,000 | JSON array | 38,134,627 | 0.727 | 13.262 | 525.2 | 100,000 | 0 |
| Docker Linux, 12 GB limit | 100,000 | XML | 57,334,609 | 0.884 | 9.436 | 623.9 | 100,000 | 0 |
| Docker Linux, 12 GB limit | 1,000,000 | CSV | 205,345,942 | 11.896 | 14.317 | 2,131.7 | 1,000,000 | 0 |
| Docker Linux, 12 GB limit | 1,000,000 | JSON array | 381,345,847 | 11.410 | 43.311 | 2,392.1 | 1,000,000 | 0 |
| Docker Linux, 12 GB limit | 1,000,000 | XML | 573,345,829 | 8.745 | 41.093 | 2,441.0 | 1,000,000 | 0 |

Five million rows were not run. The measured one million row case was below the configured 12 GB container memory limit for each format. This measures the data ingestion path, not the subsequent graph or ML analysis runtime.
