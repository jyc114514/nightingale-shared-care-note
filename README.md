# Nightingale

Nightingale is a synthetic-data prototype for a clinic-scoped longitudinal care-note
collaboration product. The repository is at **Phase 2 / Gate B**: Gate A authentication,
clinic-scoped RBAC, immutable revisions, audit metadata, and optimistic concurrency are joined
by a Glance View, occurred-time timeline, immutable source navigation, threaded comments, and
trust-state controls for three AI-scribed entry types.

Gate C work is intentionally not represented as complete: external-provider integration,
redaction before any provider call, materialized warm reads, warm-path P95, PostgreSQL execution,
self-learning importance, data decay, voice capture, and final PDF/video/submission assets remain
deferred. The repository-root `requirements.txt` is the candidate brief, **not** a pip
requirements file; never run `pip install -r requirements.txt`.

## Runtime and database

All backend commands use the already verified Conda environment:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
& $pyExe --version
& $pyExe -m pip check
```

The prototype deliberately runs on Python 3.10.20 in that shared environment. This is a
documented prototype limitation, not a production recommendation; production migration to
Python 3.12+ is a follow-up. The shared environment is not upgraded or replaced during this
sprint.

SQLite is used for local development/tests. PostgreSQL is the target through `DATABASE_URL`, but
it has not been provisioned or claimed as locally verified. Copy `.env.example` to a local `.env`,
set a random `SESSION_SECRET` of at least 32 characters, and set `DEMO_SEED_PASSWORD` only when
running the synthetic seed. `.env` is ignored by Git.

## Backend setup

Install the lockfile-pinned dependencies and apply the real Alembic schema:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
$uvExe = 'C:\Users\JI YANCHEN\.local\bin\uv.exe'
$env:UV_CACHE_DIR = Join-Path $PWD '.uv-cache'
& $uvExe pip install --python $pyExe --requirement backend\requirements.lock

Push-Location backend
& $pyExe -m alembic upgrade head
& $pyExe -m uvicorn app.main:app --reload --port 8000
Pop-Location
```

For a local synthetic demo, use a local-only password and run the idempotent seed. The seed
refuses to run unless the database is at the current Alembic head and prints opaque IDs/counts,
not note text or credentials:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
$env:DEMO_SEED_PASSWORD = 'set-a-local-only-password'
Push-Location backend
& $pyExe -m alembic upgrade head
& $pyExe -m app.scripts.seed_demo
Pop-Location
Remove-Item Env:DEMO_SEED_PASSWORD
```

The seed creates two synthetic clinics, five users, two synthetic patients, seven entries, three
distinct system AI-scribed entry types, five source-linked highlights, and a threaded internal
comment fixture. Re-running it preserves aggregate counts.

## Gate B API and UI

- `POST /auth/login`, `GET /auth/me`, and `POST /auth/logout` use an HttpOnly signed cookie.
- `GET /patients` and `GET /patients/{patient_id}/timeline` are clinic/link scoped; patient
  projections omit internal entries, comments, raw AI notes, conflicts, and revision history.
- `GET /patients/{patient_id}/glance` returns at most six deterministic active highlights and
  excludes rejected/superseded items.
- `GET /highlights/{highlight_id}/source` resolves the immutable entry version, exact quote,
  Python Unicode-codepoint offsets, and source reference.
- Clinicians can create manual highlights and review suggestions; staff can read/comment but
  cannot accept/reject; admins are read-only; patients cannot access internal highlights.
- `GET/POST /entries/{entry_id}/comments` supports same-entry threaded replies and
  `PATCH /comments/{comment_id}/resolution` supports resolve/unresolve.
- Existing Gate A routes provide role-owned edits, immutable version history, diff, revert-as-new-
  version, and deterministic `409` stale-write conflicts.

The frontend uses real cookie login and `/auth/me`, a clinic-scoped patient list, a calm light
clinical workspace, Top Card, timeline, source click-to-focus/scroll, comments, version history,
diff/revert, AI review badges, and role-aware controls. There is no UI-only role switch.

## Verification

Backend:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
Push-Location backend
& $pyExe -m ruff check --no-cache app tests migrations
& $pyExe -m ruff format --check --no-cache app tests migrations
& $pyExe -m mypy app
& $pyExe -m pytest
Pop-Location
```

The repository contains the required real-application tests `test_rbac_scope.py`,
`test_revision_history.py`, `test_concurrent_edits.py`, and the Gate B files
`test_migrations.py`, `test_highlight_provenance.py`, and `test_gate_b_api.py`. They use HTTPX
`AsyncClient` with `ASGITransport`; no old `TestClient/httpx` warning is hidden. Migration tests
use Alembic to create the database and prove that seed does not call `Base.metadata.create_all()`.

Frontend unit/build checks:

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

Real browser checks:

```powershell
Push-Location frontend
& $pnpmCmd e2e
Pop-Location
```

`pnpm e2e` creates a temporary Alembic-migrated SQLite database, seeds synthetic data, starts
real Uvicorn and Vite processes on clean local ports, and runs Scenario A (clinician source
trace) and Scenario B (staff edit/history/comments) at 1440x900 and 390x844. The custom setup
records only its own server PIDs and teardown removes those processes, the temporary database,
generated password, and ignored `artifacts/gate-b/` screenshots.

## Safety and repository boundary

- Only synthetic data is allowed. Do not add real patient data, credentials, API keys, access
  tokens, or identifying logs.
- The server is canonical for clinic and role authorization. Production requires secure cookies;
  credentialed browser writes are protected by the configured Origin allowlist.
- AI output is a suggestion. It cannot silently overwrite a human source or present an
  unsupported diagnosis as fact. Display priority, explicit risk, and clinician confirmation are
  separate fields.
- No external LLM, Docker, deployment, account creation, email, remote Git, or GitHub push is
  configured. The local Git repository intentionally has no remote.
- PostgreSQL, redaction/provider boundary, TLS/encryption-at-rest, materialized warm path/P95,
  bonus learning/data decay, final brief PDF, and demo video are explicit remaining gates.
