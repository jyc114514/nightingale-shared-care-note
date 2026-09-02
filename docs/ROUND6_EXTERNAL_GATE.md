# Round 6 external PostgreSQL gate

Round 6 is the external database-compatibility gate for the Nightingale real-clinic iteration.
It does not add product functionality and it does not deploy Render.

## Current result

The code checkpoint `2af8073536817fa5f2a19a02d25bd069fa8d5803` passed the prepared
`Real clinic PostgreSQL 18 gate` workflow in run `33592195446`. The run was triggered by a push
to `codex/real-clinic-safety` and completed successfully.

The final evidence commit `eeff4cf7216be17b07fa76c24dd5a9e95190c677` also passed the exact-SHA
workflow in run `33592639722`. The remote annotated tag `real-clinic-rc2` was then created and
verified to point to that commit.

The first code-gate run at `6de7f0c35e1668a063f13b079a3ef4f6b8aae059` failed only at mypy because
the optional Voice adapter's missing `faster_whisper` module was annotated with the wrong ignore
code. The only repair was changing `import-untyped` to `import-not-found` on that import. The
second run passed without changing migrations, dependencies, runtime behavior, or the data model.

## What the gate proves

- PostgreSQL 18 can execute the full Alembic chain through `0014_patient_publications`.
- Fresh upgrade, `alembic check`, downgrade to `0013`, re-upgrade, and a second `alembic check`
  are green.
- PostgreSQL table, index, publication-column, FK, and Alembic-version assertions are green.
- Synthetic seed is idempotent across two runs with required publication evidence present.
- The complete backend regression/safety suite and backend static checks are green.

Detailed run evidence is in [`evidence/round6_postgres_ci.md`](evidence/round6_postgres_ci.md).

## Controlled handoff

Round 6 is complete. The next separately authorized action is Round 7 main integration and an
existing-Render deployment. No pull request, production database SQL, new resource, video/PDF/ZIP
change, or live provider call was part of Round 6.
