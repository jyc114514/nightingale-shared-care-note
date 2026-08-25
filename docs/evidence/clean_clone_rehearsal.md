# Clean-clone rehearsal - 2026-08-26

This rehearsal used the final local checkpoint `f745574` and a newly created clone. The clone was
checked out with the repository `.gitattributes`, so Windows checkout line endings remained LF and
the committed Prettier check was reproducible.

## Backend

- `python -m alembic upgrade head`: passed from an empty SQLite database; migrations reached
  `0006_gate_d_archival`.
- Synthetic seed: two consecutive runs passed with stable counts: 2 clinics, 5 users, 2 patients,
  7 entries, 5 highlights, 5 materialized Glance rows, 2 comments, 1 archival summary, and 2
  archival source pointers.
- `pytest --cov=app --cov-report=term-missing --basetemp=<clone>/.pytest-tmp`: **46 passed**;
  the reproducible output is 87% coverage (2,210 statements, 286 missed), including standalone
  benchmark scripts that are not exercised by the application suite.
- Ruff check, Ruff format check, `mypy app tests`, and `pip check`: passed.

## Frontend and browser

- `pnpm install --frozen-lockfile`: passed; the lockfile policy check covered 339 entries.
- ESLint, Prettier check, Vitest (**8 passed**), TypeScript type-check, and Vite production build:
  passed.
- Playwright: **8 passed** across desktop `1440x900` and mobile `390x844`, covering Scenarios A-C
  and patient privacy with real Uvicorn, Vite, Alembic, and synthetic seed data.

## Rehearsal fixes

- `.gitattributes` makes future Windows clones use LF for text files, preventing a false Prettier
  failure caused by global `autocrlf` settings.
- E2E global setup now creates the ignored `.uv-cache` parent directory before opening its temporary
  SQLite database, so a truly clean clone does not depend on a pre-existing local folder.

Temporary clone, database, dependency tree, browser report, and rehearsal logs were removed after
validation. No source database, patient data, credentials, API key, or external provider call was
used.
