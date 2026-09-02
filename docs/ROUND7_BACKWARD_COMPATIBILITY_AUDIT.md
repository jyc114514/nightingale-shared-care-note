# Round 7 backward-compatibility audit

Status: **audit completed for the `0015` compatibility design; production migration remains
forward-only.** The audit compares the baseline application at `origin/main` (`573f897`) with the
current iteration schema. It does not authorize a production downgrade.

## Baseline and startup boundary

The baseline migration directory ends at `0010_postgres_compat`, while the current iteration
reaches `0015_feedback_backward_compat`. The Render entrypoint runs `alembic upgrade head` before
starting Uvicorn. Therefore a baseline container that only knows revisions through `0010` cannot
start against a database whose ledger is already at `0015`; a compatibility bridge must carry the
new migration files and head constant while retaining baseline application behavior.

The baseline ORM also omits `highlight_feedback_events.applied_to_profile`, and its feedback
writer omits that value. Migration `0011` initially supplied a PostgreSQL default and then removed
it, so that old write path was incompatible even though the change was additive in shape.

## Existing-table column inventory

| Revision | Existing table | Column | Nullable | Default after revision | Baseline read/write behavior | Rollback impact | Status after `0015` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `0011` | `highlights` | `clinical_conflict_id` | yes | none | Baseline selects/inserts without it; PostgreSQL accepts omission | None; old code ignores the nullable column | compatible |
| `0011` | `highlights` | `safety_class` | yes | none | Baseline selects/inserts without it; PostgreSQL accepts omission | None; protected safety data remains available to new code | compatible |
| `0011` | `highlights` | `safety_floor` | yes | none | Baseline selects/inserts without it; PostgreSQL accepts omission | None; old code cannot express the new safety floor but does not erase it | compatible |
| `0011` | `patient_glance_items` | `clinical_conflict_id` | yes | none | Baseline selects/inserts without it; PostgreSQL accepts omission | None; old projection remains readable | compatible |
| `0011` | `patient_glance_items` | `safety_class` | yes | none | Baseline selects/inserts without it; PostgreSQL accepts omission | None; old projection remains readable | compatible |
| `0011` | `patient_glance_items` | `safety_floor` | yes | none | Baseline selects/inserts without it; PostgreSQL accepts omission | None; old projection remains readable | compatible |
| `0011` | `highlight_feedback_events` | `applied_to_profile` | no | `TRUE` restored by `0015` | Baseline ORM omits it; the database supplies `TRUE` | Without `0015`, old feedback writes fail with a NOT NULL violation | compatible through bridge/default |
| `0011` | `highlight_feedback_events` | `suppression_reason` | yes | none | Baseline omits it; PostgreSQL accepts omission | None; old code ignores the nullable explanation | compatible |
| `0013` | `ai_processing_jobs` | `retry_after_seconds` | yes | none | Baseline omits it; PostgreSQL accepts omission | None; old provider path remains readable | compatible |

Revisions `0011`, `0012`, and `0014` also create new tables. Those tables are invisible to the
baseline ORM and therefore have no old read/write obligation; their presence does not require
dropping data during a code rollback. Revision `0013` likewise creates `ai_provider_circuits`.
The new-table status is **not applicable** to baseline feature behavior, but their migration
identities are required by the bridge startup path.

## Required compatibility behavior

`0015_feedback_backward_compat` performs a defensive NULL-to-TRUE backfill, enforces the existing
non-null constraint, and restores a permanent PostgreSQL `TRUE` default. SQLite keeps an equivalent
`1` default through its batch-alter path. Ordinary historical feedback means “applied to profile,”
so `TRUE` is the only compatible omission value; current protected feedback explicitly writes
`FALSE` and remains suppressed from profile learning. `suppression_reason` stays nullable.

The current ORM declares the same server default so `alembic check` remains clean. The migration
has a disposable downgrade that removes only the default; production remains forward-only and
must never use that downgrade.

## Rollback conclusion

The baseline application can read the expanded schema and can write ordinary feedback only after
the `0015` default is present. It still cannot execute `alembic upgrade head` against an `0015`
ledger because it does not contain the later revision files. Consequently, the baseline commit is
**not** a valid rollback target. The bridge is the valid Stage A rollback target because it keeps
the baseline product surface while knowing revisions `0011`–`0015` and preserving the default.

The compatibility bridge and its PostgreSQL 18 startup/write tests are recorded separately in
[`ROUND7_COMPATIBILITY_BRIDGE.md`](ROUND7_COMPATIBILITY_BRIDGE.md) and the Round 7 evidence files.
