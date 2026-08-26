# Clean-clone rehearsal - 2026-08-26

This rehearsal cloned the feature-freeze application checkpoint `3129da3` into a new Chinese-path
directory with no inherited `node_modules`, `dist`, database, `.env`, coverage, or Playwright report.
The isolated clone then ran the manual setup, full test suite, and one-click launcher smoke.

## Backend

- `pip check`, Ruff check/format, and `mypy app tests`: passed.
- Alembic reached `0008_collaboration_events`; fresh upgrade, `alembic check`, downgrade/re-upgrade,
  and legacy Gate A index repair passed.
- Synthetic seed ran twice with stable counts: 2 clinics, 5 users, 2 patients, 7 entries, 5
  highlights, 5 materialized Glance rows, 2 comments, and 1 archival summary.
- Full backend suite: **51 passed**.
- Reproducible coverage: **88%** (2,608 statements, 320 missed) using an audit-root coverage file
  and audit-root pytest basetemp.

## Frontend and browser

- `pnpm install --frozen-lockfile`: passed; the lockfile policy covered 339 entries.
- ESLint, Prettier, Vitest (**14 passed**), TypeScript type-check, and Vite production build:
  passed.
- Playwright: **10 passed** across desktop `1440x900` and mobile `390x844`, covering provenance,
  bilingual chrome, mention autocomplete, assignments, two-browser SSE invalidation, revisions,
  conflicts, and patient privacy.

## One-click launcher

- `scripts/test_demo_launcher.ps1` passed in the clean clone with `-NoBrowser -Setup`.
- The smoke exercised migration, synthetic seed, backend/frontend health, second-start idempotency,
  runtime secret/password scan, exact-PID safe stop, and port cleanup.
- The smoke runtime, database, logs, and child processes were removed after validation. No source
  database, real patient data, credential, API key, external provider call, or remote Git action
  was used.
