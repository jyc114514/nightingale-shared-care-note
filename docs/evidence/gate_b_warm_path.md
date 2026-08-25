# Gate B exploratory Glance timing

This is a recorded local measurement of the current deterministic Gate B Glance endpoint. It is
not the Gate C performance gate: the endpoint is still a direct database query, not a
materialized read model, and this run used HTTPX `ASGITransport` rather than a network hop.

## Method

- Database: fresh Alembic `upgrade head` SQLite file, then the synthetic seed.
- Actor/path: seeded Clinic A staff session, `GET /patients/{patient_id}/glance`.
- Warm-up: 20 requests.
- Samples: 100 sequential requests.
- Measurement: `time.perf_counter()` around the application request; aggregate timings only.
- Script: [`benchmark_glance.py`](../../backend/app/scripts/benchmark_glance.py).
- Environment: existing Conda `ai_env`, Python 3.10.20, 2026-08-25.

## Observed result

```json
{
  "glance_items": 5,
  "max_ms": 5.347,
  "measured_requests": 100,
  "p50_ms": 4.348,
  "p95_ms": 4.845,
  "transport": "httpx ASGITransport",
  "warmup_requests": 20
}
```

This result is useful as a reproducible Gate B baseline only. It does not establish `PERF-01`
(`P95 <= 300 ms`) for a production deployment, PostgreSQL, concurrent traffic, or the future
materialized warm path; the acceptance row remains planned.
