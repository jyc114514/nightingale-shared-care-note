# Nightingale

Nightingale is a synthetic-data prototype for a clinic-scoped longitudinal care-note
collaboration product. The repository is currently at **Phase 1 / Gate A**: authentication,
clinic-scoped RBAC, the data model, immutable revisions, audit metadata, and optimistic
concurrency are implemented. The frontend intentionally remains a health-only shell.

Timeline/Glance View UX, comments workflow, provenance/highlights, AI processing and redaction,
warm-path performance measurement, self-learning importance, data decay, and voice capture are
deferred to later phases. No deferred feature is represented as implemented here.

The repository-root `requirements.txt` is the candidate brief, **not** a pip requirements file.
Never run `pip install -r requirements.txt`.

## Runtime and database

All backend commands use the already verified Conda environment:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
& $pyExe --version
& $pyExe -m pip check
```

The prototype is deliberately running on Python 3.10.20 in that shared environment. This is a
documented prototype limitation, not a production recommendation; production migration to
Python 3.12+ is a follow-up. The shared environment is not upgraded or replaced during this
sprint.

Gate A uses SQLAlchemy 2 with file-backed SQLite for local development and tests. PostgreSQL is
the deployment target through the same `DATABASE_URL` setting and the pinned `psycopg` driver.
Copy `.env.example` to a local `.env`, set a random `SESSION_SECRET` of at least 32 characters,
and set `DEMO_SEED_PASSWORD` only when running the synthetic seed. `.env` is ignored by Git.

## Backend setup and migration

Install only the lockfile-pinned project dependencies:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
$uvExe = 'C:\Users\JI YANCHEN\.local\bin\uv.exe'
$env:UV_CACHE_DIR = Join-Path $PWD '.uv-cache'
& $uvExe pip install --python $pyExe --requirement backend\requirements.lock
```

From `backend`, create the schema with the real Alembic revision and start the API:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
Push-Location backend
& $pyExe -m alembic upgrade head
& $pyExe -m uvicorn app.main:app --reload --port 8000
Pop-Location
```

For a local synthetic demo, set a local-only password and run the idempotent seed. It prints
opaque IDs and aggregate counts only; it does not print note text or credentials:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
$env:DEMO_SEED_PASSWORD = 'set-a-local-only-password'
Push-Location backend
& $pyExe -m alembic upgrade head
& $pyExe -m app.scripts.seed_demo
Pop-Location
Remove-Item Env:DEMO_SEED_PASSWORD
```

The seed creates synthetic users in Clinic A and Clinic B, Sarah Tan as a synthetic patient,
patient-facing summary/instruction entries, staff and clinician entries, three distinct system
AI-scribed entry types, and one internal comment. Re-running it preserves the same counts.

## Gate A API boundary

- `POST /auth/login` sets an HttpOnly, SameSite cookie containing a signed JWT; the token is not
  returned to JavaScript. `POST /auth/logout` clears it and `GET /auth/me` reports the scoped
  identity.
- Passwords use `pwdlib`'s recommended Argon2 configuration. A missing or short session secret
  fails closed; tests provide an explicit test-only secret through a dependency override.
- `GET /patients` and `GET /patients/{patient_id}` are clinic/link scoped.
- Internal users can read patient entries; staff can create/edit `staff_note` only, clinicians
  can create/edit `clinician_section` only, and admins are read-only in Gate A.
- Patients can see only patient-facing summaries and instructions. Internal comments, raw
  AI-scribed entries, conflicts, and revision history are denied at the server API.
- Every edit compares `expected_version`. A successful edit appends a full immutable snapshot;
  a stale same-entry write returns `409`, stores the attempted content in a conflict record,
  and never silently overwrites the accepted version. Different entries update independently.
- Audit rows contain actor, action, entity, request, and version metadata only; note content is
  not stored in audit logs.

## Verification

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
Push-Location backend
& $pyExe -m ruff check --no-cache app tests migrations
& $pyExe -m ruff format --check --no-cache app tests migrations
& $pyExe -m mypy app tests
& $pyExe -m pytest
$env:COVERAGE_FILE = Join-Path (Get-Location).Parent '.uv-cache\phase1.coverage'
& $pyExe -m pytest --cov=app --cov-report=term-missing
Pop-Location
```

The required real-application tests are `test_rbac_scope.py`, `test_revision_history.py`, and
`test_concurrent_edits.py`. They use HTTPX `AsyncClient` with `ASGITransport` and independent
file-backed SQLite sessions. The health test follows the same async path, so the old
`TestClient/httpx` deprecation warning is not hidden.

The frontend remains limited to the health shell:

```powershell
$pnpmCmd = 'C:\Users\JI YANCHEN\AppData\Roaming\npm\pnpm.cmd'
Push-Location frontend
& $pnpmCmd install --frozen-lockfile
& $pnpmCmd lint
& $pnpmCmd test
& $pnpmCmd type-check
& $pnpmCmd build
Pop-Location
```

## Safety and repository boundary

- Only synthetic data is allowed. Do not add real patient data, credentials, API keys, access
  tokens, or identifying logs.
- The browser receives no database service credential. Server-side authorization is canonical;
  a UI control is never treated as a permission check.
- No external LLM, Docker, deployment, account creation, email, remote Git, or GitHub push is
  configured. The local Git repository intentionally has no remote.
- AI provenance, PHI redaction, TLS/encryption-at-rest evidence, Glance View P95, and the
  remaining mandatory product gates are explicitly deferred rather than implied by Gate A.
