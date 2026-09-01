# Round 3/10 safe failure, provider resilience, and logging evidence

Date: 2026-09-02

Runtime checkpoint: `481db06`; final Scenario E test checkpoint: `cc99b1c`

Result: **PASS for the bounded local synthetic prototype**.

This round makes provider failure safe and visible without changing the Voice path, allergy
vocabulary, patient publication, deployment, or external provider configuration. It does not claim
third-party retention compliance, a durable queue, or a clinical service-level agreement.

## Implemented controls

- `0013_ai_provider_resilience` adds `ai_provider_circuits` and nullable job retry metadata. The
  circuit is unique per clinic/provider and uses `closed`, `open`, and `half_open` states with a
  versioned database CAS.
- The optional provider uses an 8-second per-attempt timeout, a 12-second monotonic total budget,
  and at most 2 attempts. Timeout, connection, and transient 5xx are bounded retry classes;
  auth/balance/429/invalid output/provenance are not blindly retried.
- Three counted failures open a circuit for 60 seconds. One half-open probe is reserved through a
  database conditional update; success resets it and failure reopens it. Fixture mode bypasses the
  external circuit and remains the default.
- `safe_event()` emits only closed-vocabulary JSON metadata. The defensive record filter and
  `SafeExceptionMiddleware` prevent raw exception text, common PHI/credential patterns, and control
  injection from reaching the local application log.
- `audit_phi_logs.py` scans only explicit paths and returns non-zero for synthetic name/ID/phone,
  Authorization, key, database-URL, cookie/session, or unreadable-file findings without echoing
  values.
- AI events are ordered as `ai_job_created`, `ai_redaction_completed`,
  `ai_provider_call_started`, safe provider completion/failure, and provenance completion. A
  redaction failure emits no provider-start event and makes zero provider calls.
- Internal provider status returns safe availability, circuit, bounded retry-after, and existing
  workspace availability. The bilingual AI panel displays available/degraded/temporarily
  unavailable states, offers one manual status check, keeps existing workspace controls usable,
  and never silently falls back to fixture output.

## Verification results

| Check | Result |
| --- | --- |
| Backend full suite | 131 passed; 88% coverage |
| Backend quality | Ruff check/format, mypy, pip check passed |
| Migration | Fresh `0001` -> `0013`, downgrade/re-upgrade, legacy repair, and `alembic check` on a writable copy passed |
| Existing local DB | Original `backend/nightingale.db` remains unchanged at `0012` because the managed workspace marks it read-only; an exact synthetic copy upgraded to `0013` and passed `alembic check` |
| Seed | Fresh migrated seed twice remained idempotent; 9 entries, 6 highlights, 6 Glance items |
| Frontend | Frozen install, 44 Vitest tests, Prettier, TypeScript, ESLint, and build passed |
| Core browser | 18/18 Playwright checks passed: 9 at 1440x900 and 9 at 390x844 |
| Voice regression | 4/4 existing fixture checks passed; Voice behavior was not changed |
| Log audit | Clean synthetic log exited 0; dirty synthetic log and missing log exited non-zero without value echo |
| Warm Glance | 50 warm-up + 1,000 real-TCP requests, concurrency 10, zero errors; P50 56.818 ms, P95 70.639 ms, P99 93.048 ms, max 107.593 ms |
| Circuit-open fail-fast | 100 synthetic submissions, zero errors, P50 16.721 ms, P95 17.911 ms, P99 18.111 ms, max 20.628 ms, zero provider calls during measured open window |

Detailed machine-readable warm-path data is in [round3_warm_path.json](round3_warm_path.json),
and the fail-fast result is in [round3_circuit_failfast.json](round3_circuit_failfast.json). The
fail-fast script is [benchmark_circuit_failfast.py](../../backend/app/scripts/benchmark_circuit_failfast.py).

## Scenario E browser evidence

Scenario E route-mocks a provider timeout/503 rather than making a live call. It verifies that a
Staff user sees a safe degraded state, no fixture fallback, and no internal error code while
Glance/source, comments, tasks, and history remain available. It then logs in as Patient and
confirms no outage panel or internal AI surface is rendered. The same workflow passes at both
viewports.

- [Desktop degraded panel](../../artifacts/gate-b/desktop-1440-scenario-e-degraded.png)
- [Desktop Patient view](../../artifacts/gate-b/desktop-1440-scenario-e-patient.png)
- [Mobile degraded panel](../../artifacts/gate-b/mobile-390-scenario-e-degraded.png)
- [Mobile Patient view](../../artifacts/gate-b/mobile-390-scenario-e-patient.png)

## Status changes and limits

- **#3 PHI beyond model redaction — PARTIAL:** local application logging, exception output, and
  explicit log auditing are hardened. Render/host/provider retention is still **Unknown**.
- **#4 Redaction ordering — SURVIVES, strengthened:** ordered safe events and provider spies prove
  redaction precedes provider calls; the provider also performs a second typed-payload scan.
- **#8 Model hangs 45 seconds — PARTIAL:** total wait is bounded to the configured budget, but the
  endpoint remains synchronous and can still occupy one request worker during that bounded call.
- **#9 Provider 503 for an hour — PARTIAL:** persistent fail-fast circuit, provider status, and
  degraded UI preserve existing records; no durable queue, scheduled retry, or automatic replay
  exists.

Other known limits remain: the provider adapter is optional and not called in this verification;
the benchmark is local SQLite/Uvicorn rather than hosted PostgreSQL; and this remains synthetic
prototype evidence, not clinical production certification.
