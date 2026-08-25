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

The Phase 0 prompt permits 3.11–3.13 and also requires reusing the confirmed existing
environment rather than creating an alternate environment. This run preserved the existing
Python 3.10.20 Conda environment and selected compatible pinned dependencies; no `.venv`, uv
managed interpreter, conda-base activation, or global pip installation was used.

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
- Backend pytest: passed, 1 test; the cache provider is disabled because the restricted runner
  cannot create `.pytest_cache`. A FastAPI/Starlette `httpx` deprecation warning remains.
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
- Git is installed locally but is not on this PowerShell session's PATH; repository commands use
  its explicit executable path. The VS Code shortcut is not a dependency or blocker.
- Clinical data, authentication, authorization, database schema, AI processing, redaction,
  provenance, Glance View P95, and all bonus features remain unimplemented.
