# Phase 1 ingestion benchmark

Measured on 27 November 2026 with `backend/scripts/benchmark_ingest.py`. The script writes source rows sequentially, then calls `ingest_file` and verifies exact valid/rejected counts. It reports elapsed ingestion time separately from generation time. Peak memory is the operating system's peak working set for the Python process on Windows and `ru_maxrss` peak RSS on Linux. The peak covers generation plus ingestion; source generation itself holds one row at a time. Each case uses a temporary source and output directory, which is removed after the run. `docker compose` sets the backend limit to 12 GB. Output tables contain transactions, wallets, network observations, input and output edges, rejected rows and IP enrichment. The benchmark used supplied synthetic geo/ASN for 250 IPs and offline MMDB for one destination IP.

| Runtime | Rows | Format | Source bytes | Generation s | Ingestion s | Peak process MiB | Valid | Rejected |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Windows | 100,000 | CSV | 20,534,722 | 1.408 | 7.398 | 324.9 | 100,000 | 0 |
| Windows | 100,000 | JSON array | 38,134,627 | 0.803 | 25.163 | 318.7 | 100,000 | 0 |
| Windows | 100,000 | XML | 57,334,609 | 1.078 | 25.881 | 323.9 | 100,000 | 0 |
| Windows | 1,000,000 | CSV | 205,345,942 | 54.853 | 5.810 | 1,925.3 | 1,000,000 | 0 |
| Windows | 1,000,000 | JSON array | 381,345,847 | 8.193 | 192.351 | 1,914.2 | 1,000,000 | 0 |
| Windows | 1,000,000 | XML | 573,345,829 | 36.956 | 178.274 | 2,054.6 | 1,000,000 | 0 |
| Docker Linux, 12 GB limit | 100,000 | CSV | 20,534,722 | 1.181 | 5.235 | 543.7 | 100,000 | 0 |
| Docker Linux, 12 GB limit | 100,000 | JSON array | 38,134,627 | 0.692 | 6.971 | 649.4 | 100,000 | 0 |
| Docker Linux, 12 GB limit | 100,000 | XML | 57,334,609 | 0.798 | 9.880 | 571.7 | 100,000 | 0 |
| Docker Linux, 12 GB limit | 1,000,000 | CSV | 205,345,942 | 11.755 | 8.615 | 2,252.7 | 1,000,000 | 0 |
| Docker Linux, 12 GB limit | 1,000,000 | JSON array | 381,345,847 | 7.302 | 43.415 | 2,377.4 | 1,000,000 | 0 |
| Docker Linux, 12 GB limit | 1,000,000 | XML | 573,345,829 | 9.052 | 40.249 | 2,205.1 | 1,000,000 | 0 |

Five million rows were not run. The measured one million row case was below the configured 12 GB container memory limit for each format. This measures the data ingestion path, not the subsequent graph or ML analysis runtime.
