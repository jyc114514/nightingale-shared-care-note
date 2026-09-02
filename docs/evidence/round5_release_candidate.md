# Round 5 release-candidate evidence

Status: **local Release Candidate integration complete; Round 6 external gate complete**. The Round
5 sections below remain historical local evidence. The external PostgreSQL result, final evidence
run, and remote `rc2` tag are recorded in [`round6_postgres_ci.md`](round6_postgres_ci.md).

## Candidate identity

| Field | Value |
| --- | --- |
| Branch | `codex/real-clinic-safety` |
| Baseline tag | `72h-submission` → `573f897a69864707f64b1846b2802a2674f69597` |
| Code verification checkpoint | `39ab0f0` — `fix: enforce authenticated API boundary` |
| Migration head | `0014_patient_publications` |
| Requirements SHA-256 | `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5` |
| Final local tag | `real-clinic-rc1` (created after this evidence commit; no push) |

Round 5 local commits cover CI/temp boundaries (`46a89a5`), integration audit/docs (`e01e68f`),
space-safe launcher child arguments (`7587e30`), space-safe launcher smoke harness (`47497f3`),
authenticated logout (`681301c`), and authenticated login/Voice provider boundary (`39ab0f0`).

## Migration and reproducibility

- Fresh SQLite `0001→0014`: pass; 33 tables, publication tables present, 11 publication FKs,
  seed twice stable, `alembic check` pass.
- Disposable legacy paths `0010→0014`, `0011→0014`, `0012→0014`, and `0013→0014`: all pass;
  one synthetic entry/version/comment/highlight/task per probe was preserved; new publication
  tables were initially empty; seed twice/check passed; probe databases were removed.
- Disposable `0014→0013→0014`: pass; publication row count 1→0 is expected destructive downgrade
  behavior because the new tables are dropped. No real/user database was downgraded.
- PostgreSQL offline SQL `0010→0014`: pass; 307 lines, publication/evidence tables, four
  self-reference references, no `_alembic_tmp` token. Fresh `base→head` offline generation is
  limited by the pre-existing `0003_gate_b_repair` reflection call and is not called pass.

## PostgreSQL status and prepared workflow

No Docker, Podman, local PostgreSQL server, `psql`, `pg_isready`, or `actionlint` was available in
the Round 5 environment. Real PostgreSQL execution was therefore **PENDING EXTERNAL CI at that
checkpoint**. Round 6 later executed the prepared workflow:
[`real-clinic-postgres.yml`](../../.github/workflows/real-clinic-postgres.yml): PostgreSQL 18,
Python 3.12, locked dependencies, current 0014 head/check, schema/FK assertions, seed twice,
full backend tests, Ruff, mypy, pip check, fixture AI, Voice disabled, read-only repository
permissions, and no deployment step. Run `33592195446` passed at code commit `2af8073`; see
[`Round 6 PostgreSQL evidence`](round6_postgres_ci.md). Its database values are disposable CI
fixtures, not user or production credentials.

## Clean clone

Tracked-only clean clone v3 at `39ab0f0` passed locked backend install, fresh migration/seed/check,
175 backend tests, Ruff/format/mypy/pip check, frozen frontend install, 45 Vitest tests,
lint/Prettier/type-check/build, launcher smoke, Gate B 18/18, Voice 4/4, and Scenario F 2/2 at
1440×900 and 390×844. The clone tree contained zero forbidden tracked files. Its disposable
database, runtime and test outputs were isolated; cleanup was attempted after zero processes and
ports were confirmed, but Windows ACL/deep-path restrictions prevented removing the temporary
clone directories. No ownership or permissions were changed.

## Primary integrated regression

| Check | Result |
| --- | --- |
| Backend | 175 passed; 85% coverage; Ruff check/format, mypy, pip check passed |
| Frontend | 45 Vitest; lint, Prettier, type-check and build passed |
| Browser | 18 Gate B + 4 Voice + 2 Scenario F passed at both viewports |
| API/privacy | 54 OpenAPI routes; unauthenticated non-bootstrap 0; write routes missing Origin 0; forbidden Patient projection fields 0; OpenAPI secret-pattern 0 |
| Logs | clean fixture exit 0; dirty negative fixture exit 1; matched values not echoed |
| Tracked tree/history | forbidden current names 0; high-confidence current/history token/private-key hits 0; only user MP4 remains untracked |

## Comparable local performance

These are separate local SQLite/Uvicorn or ASGI measurements; different rounds/datasets must not
be read as a trend.

| Path | Protocol/result |
| --- | --- |
| Glance | 50 warm-up + 1,000 real-TCP requests, concurrency 10, 0 errors; P50 86.852 ms, P95 113.998 ms, P99 142.345 ms, max 159.988 ms, 6 items |
| Circuit-open fail-fast | 100 submissions after 3 synthetic provider failures, 0 errors, 0 measured provider calls; P50 25.529 ms, P95 27.571 ms, P99 31.806 ms, max 33.553 ms |
| Published-care | 50 warm-up + 1,000 real-TCP requests, concurrency 10, 0 errors; P50 63.247 ms, P95 82.264 ms, P99 126.876 ms, max 145.557 ms, 1 update |

## Known limitations and Round 6 handoff

Scenario #3, #8, #9, #12, #13, #14 and #15 remain PARTIAL; #16 remains SURVIVES. The candidate
does not claim FHIR conformance, clinical production safety, general medication NLP, external
message delivery/receipt/recall, durable queue/replay, or hosted PostgreSQL performance.

Round 6 authorized and completed the iteration-branch push, bounded repair, final evidence commit,
exact-SHA PostgreSQL 18 run, and `real-clinic-rc2` tag. Round 7 is the separate main/Render handoff;
do not infer a Render deployment from this local release-candidate record.

Round 5 did not modify or regenerate the final video, Technical Brief PDF, or submission ZIP.
