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

## Final release-candidate rehearsal attempt - 2026-08-28

The final release candidate was cloned from commit `189d315` into an isolated temporary directory;
the primary worktree and the untracked original MP4 were not copied into the clone.

- Fresh clone checkout: passed at `189d315`.
- Alembic upgrade through `0010_postgres_compat`, `alembic check`, twice-run synthetic seed, and
  backend test suite: passed; the backend suite reported **85 passed**.
- Fresh frontend `pnpm install --frozen-lockfile` and production build: passed.
- The repository launcher started the isolated backend/frontend and both health endpoints returned
  200. Its official smoke script then exited non-zero because the managed Windows environment
  denied `taskkill.exe` while cleaning its own child-process tree. This is an environment cleanup
  failure, not a product assertion pass.
- A second launcher retry was not forced after the safety review could not prove port ownership
  from available process metadata. Ports 8000, 8010, and 5173 were verified clear afterward.
- Result: **partial rehearsal only; FINAL-CLEAN-CLONE remains in progress**. Do not claim a fully
  green clean-clone launcher gate from this record until it is rerun on a host that permits the
  repository's ownership-checked cleanup.

No password file, API key, database URL, runtime secret, production database, Render write, or
GitHub write was used by this rehearsal.

## Round 5 final clean-clone rehearsal - 2026-09-02

Tracked-only clean clone v3 at code checkpoint `39ab0f0` was created outside the repository and
contained no MP4, database, cache, `node_modules`, test-results, or password/API-key files.

- Backend lockfile install, fresh Alembic `0001→0014`, `alembic check`, seed twice, 175 tests,
  Ruff check/format, mypy, and pip check: passed.
- Frontend frozen install, 45 Vitest tests, lint, Prettier, type-check, and build: passed.
- Gate B: 18/18; Voice: 4/4; Scenario F: 2/2, each across 1440×900 and 390×844: passed.
- One-click launcher smoke: migration/seed, health, second-start idempotency, runtime/log secret
  checks, owned stop, and port cleanup: passed after the Round 5 path-space fixes.

The first attempt exposed Windows path-space handling in the launcher child arguments and test
harness; both were fixed in local commits `7587e30` and `47497f3`. The final v3 source run was
green. Cleanup was attempted only after verifying no clone-owned processes and no target ports;
Windows ACL/deep-path restrictions prevented deleting the temporary clone directories, so no
ownership or permission changes were made. This is a local reproducibility record, not external
PostgreSQL or Render evidence.
