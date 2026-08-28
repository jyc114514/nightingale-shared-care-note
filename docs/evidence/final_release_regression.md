# Final release-candidate regression - 2026-08-28

This record captures the reproducible local checks run before the final release documentation and
packaging commits. The product code was unchanged from application checkpoint `a13e718`; the
documentation-only release commits follow it.

## Backend

- Environment: Python 3.10.20 in the existing `ai_env`.
- `ruff check --no-cache app tests migrations`: passed.
- `ruff format --check --no-cache app tests migrations`: passed; 113 files already formatted.
- `mypy app tests`: passed; 100 source files, no issues.
- `pytest --cov=app --cov-report=term-missing`: **85 passed in 54.56s**, total coverage **88%**.
- `pip check`: passed.
- Fresh temporary SQLite database: Alembic reached `0010_postgres_compat (head)` and
  `alembic check` reported no new upgrade operations.
- The synthetic seed ran twice with stable counts: 2 clinics, 5 users, 2 patients, 7 entries,
  2 comments, 5 highlights, 5 Glance items, 1 archival summary, and 2 archival sources.
- The temporary database and generated seed password were removed after the check; no password
  value was recorded.

## Frontend and browser

- `pnpm install --frozen-lockfile`: passed with pnpm 11.22.0.
- ESLint, Prettier, TypeScript type-check, and Vite production build: passed.
- Vitest: **37 tests passed**.
- Gate B Playwright: **14 passed** at desktop `1440x900` and mobile `390x844`.
- Voice fixture Playwright: **4 passed** at desktop `1440x900` and mobile `390x844`.
- The E2E harness used isolated migrated SQLite data and removed its generated runtime state after
  each run; no production database or online write was used.

## Additional measurements

- Warm-path measurement is recorded in [`gate_c_warm_path.md`](gate_c_warm_path.md): 1,000 real
  TCP requests, concurrency 10, zero errors, P95 56.053 ms.
- The repository-root `requirements.txt` SHA-256 remained
  `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5`.
- These checks do not claim human final-video content review, model quality, microphone capture,
  or clinical production compliance.
