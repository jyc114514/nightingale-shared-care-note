# Gate C warm-path benchmark

Result: **PASS** for the local approximation target P95 <= 300 ms.

This is a measured local SQLite + Uvicorn TCP benchmark, not a hosted PostgreSQL
production result and not evidence of deployment TLS or encryption-at-rest.

| Field | Value |
| --- | --- |
| Commit | 3129da3 |
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
| P50 | 49.774 ms |
| P95 | 67.823 ms |
| P99 | 80.593 ms |
| Max | 86.835 ms |

The measured endpoint is GET /patients/{patient_id}/glance with a real
cookie session. It reads patient_glance_items; provider processing is only on
the authenticated write path.
