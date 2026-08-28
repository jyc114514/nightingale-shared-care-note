# Gate C warm-path benchmark

Result: **PASS** for the local approximation target P95 <= 300 ms.

This is a measured local SQLite + Uvicorn TCP benchmark, not a hosted PostgreSQL
production result and not evidence of deployment TLS or encryption-at-rest.

| Field | Value |
| --- | --- |
| Commit | a13e718 |
| Python | 3.10.20 |
| Database | file-backed SQLite local approximation |
| Transport | real TCP HTTP via Uvicorn and httpx.Client |
| Patients | 26 |
| Benchmark entries | 208 |
| Benchmark highlights/materialized rows | 208 |
| Warm-up | 50 |
| Measured requests | 1000 |
| Concurrency | 10 |
| Response item count | 6 |
| Errors | 0 |
| P50 | 44.283 ms |
| P95 | 56.053 ms |
| P99 | 81.509 ms |
| Max | 89.495 ms |

The measured endpoint is GET /patients/{patient_id}/glance with a real
cookie session. It reads patient_glance_items; provider processing is only on
the authenticated write path.
