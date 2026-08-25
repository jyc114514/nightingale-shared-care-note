# Nightingale

Nightingale is a synthetic-data prototype for a clinic-scoped longitudinal care-note
collaboration product. The repository is at **Phase 4 / local Bonus implementation**: Gate A
authentication, clinic-scoped RBAC, immutable revisions, audit metadata, and optimistic
concurrency are joined by a Glance View, occurred-time timeline, immutable source navigation,
threaded comments, trust-state controls, and a redacted deterministic AI write path.

The local Gate C boundary is implemented and measured, and the Bonus adaptive-importance and
hybrid hot/warm/cold context paths are implemented with clinic-scoped deterministic logic. This is
not a hosted production
deployment: external-provider integration, PostgreSQL execution, TLS/encryption-at-rest
evidence, data decay, voice capture, final video, and external submission remain deferred. The
repository-root `requirements.txt` is the candidate brief, **not** a
pip requirements file; never run `pip install -r requirements.txt`.

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
distinct system AI-scribed entry types, five source-linked highlights/materialized Glance rows,
a threaded internal comment fixture, and a derived archival summary with immutable source
pointers. Re-running it preserves aggregate counts.

## Gate B API and UI

- `POST /auth/login`, `GET /auth/me`, and `POST /auth/logout` use an HttpOnly signed cookie.
- `GET /patients` and `GET /patients/{patient_id}/timeline` are clinic/link scoped; patient
  projections omit internal entries, comments, raw AI notes, conflicts, and revision history.
- `GET /patients/{patient_id}/glance` returns at most six deterministic active highlights and
  excludes rejected/superseded items. It reads only the `patient_glance_items` materialized
  projection; it does not call a provider.
- `GET /highlights/{highlight_id}/source` resolves the immutable entry version, exact quote,
  Python Unicode-codepoint offsets, and source reference.
- Clinicians can create manual highlights and review suggestions; staff can read/comment but
  cannot accept/reject; admins are read-only; patients cannot access internal highlights.
- `GET/POST /entries/{entry_id}/comments` supports same-entry threaded replies and
  `PATCH /comments/{comment_id}/resolution` supports resolve/unresolve.
- Existing Gate A routes provide role-owned edits, immutable version history, diff, revert-as-new-
  version, and deterministic `409` stale-write conflicts.
- `POST /patients/{patient_id}/ai-processing` accepts the three AI-scribed entry types through a
  typed redacted payload and deterministic fixture provider. It creates a new system-authored
  entry and suggested immutable highlight; it never overwrites a human entry.
- `GET /ai-processing/{job_id}` exposes job metadata and safe error codes, not raw input,
  provider prompts, or provider responses.
- `POST /highlights/{highlight_id}/feedback` records clinic-scoped staff/clinician feedback with
  an idempotency key. Feedback updates a bounded adaptive ranking contribution and the
  materialized Glance projection; it never mutates explicit risk or provenance.
- `GET /patients/{patient_id}/context` returns hot full-detail entries, warm metadata indexes,
  and derived archival periods. `POST /patients/{patient_id}/context/refresh` rebuilds only the
  derivative summaries for staff/clinicians; canonical entries and immutable versions are never
  deleted or rewritten.
- Cold summaries carry a policy version, manifest hash, source entry/version pointers, and an
  explicit “Derived summary · not canonical source” disclosure. Open actions, explicit risk,
  active conflicts, unresolved discussion, pinned/accepted highlights, and clinician-confirmed
  care-plan entries remain protected from compression.

The frontend uses real cookie login and `/auth/me`, a clinic-scoped patient list, a calm light
clinical workspace, Top Card, timeline, source click-to-focus/scroll, immutable Unicode
codepoint highlighting, comments, version history, diff/revert, conflict comparison, AI review
badges, role-aware controls, and a collapsed **Why ranked?** explanation with pin/unpin feedback.
There is no UI-only role switch.

The Phase 5 delivery set includes the editable and rendered Technical Brief, attribution audit,
demo script/shot list, UX timing protocol, deployment checklist, and synthetic browser screenshots.
There is no final video claim while a reliable local recorder/codec is unavailable.

## Bonus importance logic

The adaptive ranking path uses a closed structured feature signature derived from entry type,
item kind, source kind, action state, explicit risk, and a normalized topic category. It does not
use embeddings, external LLM calls, patient identifiers, names, quotes, or raw free text.

```text
final display priority = clamp(
  base priority + recency + explicit risk + unresolved action
  + clinician confirmation + bounded adaptive feedback,
  0, 100
)
```

Adaptive feedback is bounded to `[-12, +12]`, is clinic-scoped and idempotent, and is kept
separate from medical risk, source provenance, and clinician truth. Glance reads remain provider-
free and consume only the materialized projection. The UI labels this as “Ranking priority, not a
medical risk score”.

## Verification

Backend:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
Push-Location backend
& $pyExe -m ruff check --no-cache app tests migrations
& $pyExe -m ruff format --check --no-cache app tests migrations
& $pyExe -m mypy app tests
& $pyExe -m pytest
Pop-Location
```

The repository contains the required real-application tests `test_rbac_scope.py`,
`test_revision_history.py`, `test_highlight_provenance.py`, and `test_concurrent_edits.py`, plus
`test_redaction.py`, `test_ai_provider_boundary.py`, `test_ai_processing.py`, and
`test_materialized_glance.py`, `test_self_learning_importance.py`, and `test_data_decay.py`. They use HTTPX `AsyncClient` with `ASGITransport`; no old
`TestClient/httpx` warning is hidden. Migration tests use Alembic to create the database and
prove that seed does not call `Base.metadata.create_all()`.

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
real Uvicorn and Vite processes on clean local ports, and runs Scenario A (exact source and
review), Scenario B (diff/revert/thread), Scenario C (real stale-write conflict plus derived
context/source pointer), and patient privacy at 1440x900 and 390x844. The custom setup records
only its own server PIDs and teardown
removes those processes, the temporary database, generated password, and ignored
`artifacts/gate-b/` screenshots.

Gate C warm-path benchmark:

```powershell
Push-Location backend
& $pyExe -m app.scripts.benchmark_warm_path
Pop-Location
```

This uses a fresh migrated file-backed SQLite database, 26 synthetic patients, 208 benchmark
entries/highlights, real Uvicorn TCP HTTP, 50 warm-up requests, 1,000 measured requests, and
10-way concurrency. The current evidence is
[`gate_c_warm_path.md`](docs/evidence/gate_c_warm_path.md). It is a local approximation, not a
hosted PostgreSQL production benchmark.

## Safety and repository boundary

- Only synthetic data is allowed. Do not add real patient data, credentials, API keys, access
  tokens, or identifying logs.
- The server is canonical for clinic and role authorization. Production requires secure cookies;
  credentialed browser writes are protected by the configured Origin allowlist.
- AI output is a suggestion. It cannot silently overwrite a human source or present an
  unsupported diagnosis as fact. Display priority, explicit risk, and clinician confirmation are
  separate fields.
- No external LLM, Docker, deployment, account creation, or email is configured. Both Bonus paths
  are local and deterministic; hosted PostgreSQL, TLS/encryption-at-rest, final video, and
  external submission remain explicit delivery gates. The local Technical Brief PDF is complete
  and QA-recorded under `docs/evidence/technical_brief_qa.md`.
- The local redaction/provider boundary and materialized warm path/P95 are implemented and
  evidenced, but do not establish hosted production guarantees.
