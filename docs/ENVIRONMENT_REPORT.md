# Phase 0 environment report

Date: 2026-08-25 (+08:00)

## Discovery and environment identity

- Search was limited to `C:\Users\JI YANCHEN\Desktop\ai_trading_playground`.
- Found `ai_env` at `C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env`.
- `conda-meta` exists and `pyvenv.cfg` does not; the environment is Conda, not venv/virtualenv.
- Python executable: `C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe`.
- Python: `3.10.20 | packaged by conda-forge | (main, Mar 5 2026, 16:36:49) [MSC v.1944 64 bit (AMD64)]`.
- `sys.prefix` is the same `ai_env` root.
- pip: `26.1.2`.

PM decision: the implemented prototype continues using the existing Python 3.10.20 Conda
environment. This is a prototype-only limitation; the production recommendation is Python
3.12+. The sprint does not upgrade the shared environment or create an alternate environment.
No `.venv`, uv-managed interpreter, conda-base activation, or global pip installation was used.

## Package change

The pre-install and post-install snapshots contain package names and versions only:

- [ai_env-before.txt](../artifacts/environment/ai_env-before.txt)
- [ai_env-after.txt](../artifacts/environment/ai_env-after.txt)
- [ai_env-package-delta.txt](../artifacts/environment/ai_env-package-delta.txt)

Added without upgrading or uninstalling existing packages:

| Package | Version |
| --- | ---: |
| alembic | 1.15.2 |
| coverage | 7.15.4 |
| iniconfig | 2.3.0 |
| mako | 1.4.1 |
| mypy | 1.15.0 |
| mypy-extensions | 1.1.0 |
| pluggy | 1.6.0 |
| psycopg | 3.2.6 |
| psycopg-binary | 3.2.6 |
| pwdlib | 0.3.0 |
| pydantic-settings | 2.7.1 |
| PyJWT | 2.10.1 |
| pytest | 8.3.5 |
| pytest-asyncio | 0.25.3 |
| pytest-cov | 6.0.0 |
| ruff | 0.9.10 |

FastAPI 0.136.3, Uvicorn 0.49.0, SQLAlchemy 2.0.50, and HTTPX 0.28.1 were already present
and were preserved. The lock was resolved against a constraints snapshot of the existing
environment to prevent unrelated upgrades.

## Verification evidence

- `ai_env python --version`: Python 3.10.20 (recorded above).
- `ai_env python -m pip check` before installation: exit 0, `No broken requirements found.`
- `ai_env python -m pip check` after installation: exit 0, `No broken requirements found.`
- `uv pip compile --python <ai_env python> ...`: resolved the pinned backend lock.
- Lockfile dry-run: 16 packages to install, 0 packages to upgrade, 0 packages to uninstall.
- Backend Ruff check: passed with `--no-cache`.
- Backend Ruff format check: passed with `--no-cache`.
- Backend mypy: passed, 4 source files checked.
- Backend pytest: passed, 1 async test; the cache provider is disabled because the restricted
  runner cannot create `.pytest_cache`. The health test uses `httpx.AsyncClient` with
  `ASGITransport`, so the former FastAPI/Starlette `TestClient` deprecation warning is gone.
- Live health check: a temporary Uvicorn process returned `status=ok`, `phase=0-scaffold`; it
  was stopped and port 8000 was confirmed free afterward.
- Frontend `pnpm install`: passed with the project lockfile; Playwright browser binaries were not
  downloaded. pnpm's project approval allows only the required `esbuild` build script.
- Frontend lint: passed.
- Frontend unit test: passed, 1 test.
- Frontend type-check: passed.
- Frontend production build: passed.
- Vite dev-server smoke check: temporary server returned HTTP 200 with the root mount and
  `/src/main.tsx` entry present; it was stopped and port 5173 was confirmed free afterward.
- No Docker, external LLM, external account, deployment, or remote Git was used.

## Known risks and limitations

- The existing environment is Python 3.10.20 rather than the project plan's preferred 3.12.
- Python 3.10.20 is accepted only for this prototype; production migration to Python 3.12+ is
  still required.
- Git is installed locally but is not on this PowerShell session's PATH; repository commands use
  its explicit executable path. The VS Code shortcut is not a dependency or blocker.
- Clinical data, authentication, authorization, database schema, AI processing, redaction,
  provenance, Glance View P95, and all bonus features remain unimplemented.

## Phase 1 / Gate A evidence - 2026-08-25

The Phase 0 history above is preserved as a historical snapshot. The implemented prototype
continues using the same Conda `ai_env` Python 3.10.20 environment. No package delta was needed
for Gate A and `backend/requirements.lock` remains the Phase 0 lockfile.

- The health test now uses `httpx.AsyncClient` with `ASGITransport` and pytest strict asyncio;
  the former `TestClient/httpx` deprecation warning is gone without suppressing warnings.
- Ruff check, Ruff format check, mypy, and eight real FastAPI tests passed after Gate A changes.
- Coverage run: `pytest --cov=app --cov-report=term-missing`, 8 passed, 83% total coverage.
- Real Alembic `upgrade head` on an empty temporary SQLite file created all 11 expected tables,
  including `alembic_version`.
- The synthetic seed ran twice against a temporary SQLite file with stable counts: 2 clinics,
  5 users, 2 patients, 7 entries, and 1 comment. It required an explicit local
  `DEMO_SEED_PASSWORD` and printed only IDs/counts.
- Gate A remains local/test SQLite with PostgreSQL as the target connection through
  `DATABASE_URL`. No Docker, hosted database, external LLM, or external account was used.

Gate A does not change the Python production limitation: Python 3.12+ remains the recommended
production runtime migration. Gate B/C items, including redaction, provenance, performance, and
the full product UI, remain deferred.
