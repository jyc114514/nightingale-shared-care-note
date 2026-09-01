# Round 2 warm-path benchmark

Result: **PASS** for the local approximation target P95 <= 300 ms.

This is a measured local SQLite + Uvicorn TCP benchmark. It is not a hosted PostgreSQL
production result and is not evidence of deployment TLS or encryption-at-rest.

| Field | Value |
| --- | --- |
| Application/test checkpoint | `803733d` |
| Python | 3.10.20 |
| Database | File-backed SQLite local approximation |
| Transport | Real TCP HTTP via Uvicorn and `httpx.Client` |
| Patients | 26 |
| Benchmark entries | 208 |
| Benchmark highlights/materialized rows | 208 |
| Warm-up requests | 50 |
| Measured requests | 1,000 |
| Concurrency | 10 |
| Response item count | 6 |
| Warm-up errors | 0 |
| Measured errors | 0 |
| P50 | 64.165 ms |
| P95 | 83.045 ms |
| P99 | 99.848 ms |
| Max | 137.349 ms |

The measured endpoint was `GET /patients/{patient_id}/glance` with a real cookie session. It
reads the materialized `patient_glance_items`/`task_glance_items` projections; provider processing
is not on this authenticated read path. The run used only synthetic benchmark data and removed its
temporary database after completion.
