# Round 7 compatibility bridge

Status: **bridge design prepared from the baseline tree; external bridge CI is the next gate.**
This branch preserves the baseline product surface while making the database migration ledger
forward-compatible with the expanded iteration schema.

## Lineage and purpose

- Base: `origin/main` / `573f897a69864707f64b1846b2802a2674f69597`.
- Branch: `codex/real-clinic-compat-bridge`.
- The bridge copies only migrations `0011`–`0015` and updates
  `backend/app/db/migration.py` to the current head.
- Baseline application models, routes, frontend, and product behavior remain otherwise unchanged.
- The existing Render entrypoint is unchanged: it validates settings, runs `alembic upgrade head`,
  optionally seeds synthetic data, and then starts Uvicorn.

## Migration identity

The following files were copied byte-for-byte from the PostgreSQL-tested feature branch:

- `backend/migrations/versions/0011_real_clinic_safety.py`
- `backend/migrations/versions/0012_glance_impressions.py`
- `backend/migrations/versions/0013_ai_provider_resilience.py`
- `backend/migrations/versions/0014_patient_publications.py`
- `backend/migrations/versions/0015_feedback_backward_compat.py`
- `backend/app/db/migration.py`

The bridge does not edit any historical migration. `0015` restores PostgreSQL default `TRUE` for
the legacy feedback omission path and keeps SQLite default `1`; production remains forward-only.

## What bridge CI must prove

The `compat-bridge-postgres.yml` workflow uses PostgreSQL 18, Python 3.12, locked dependencies,
synthetic values, and no deployment step. It checks:

1. bridge `alembic upgrade head` reaches `0015_feedback_backward_compat`;
2. the `applied_to_profile` column is non-null with a true database default;
3. the baseline synthetic seed is idempotent;
4. the unchanged baseline entrypoint starts against the 0015 ledger;
5. baseline login, Glance, source, comments, and feedback write work;
6. an omitted `applied_to_profile` is stored as true;
7. baseline backend tests excluding the metadata-shape test, static checks, and Docker build pass.

The baseline `tests/test_migrations.py` is intentionally excluded from bridge regression because
its ORM metadata stops at 0010 and therefore correctly reports the new tables/columns as removed.
That is an expected bridge limitation, not a clean-schema claim. The full feature branch owns the
clean `alembic check` assertion against the complete ORM metadata.

## Rollback meaning

The bridge is the Stage A rollback target after it is proven Live. It knows the 0015 revision and
can execute its entrypoint against the migrated ledger while retaining baseline UI/API behavior.
The original baseline commit is not a valid rollback target after the database reaches 0015,
because its entrypoint cannot locate that revision. No production DB downgrade is permitted.
