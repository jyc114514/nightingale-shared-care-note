# Nightingale technical brief - Phase 1 / Gate A

This brief records only behavior that exists in the local synthetic prototype. It does not
claim a Glance View, timeline UX, AI provider, provenance highlights, PHI redaction, TLS,
encryption at rest, warm-path P95, or bonus feature.

## Architecture and runtime boundary

The backend is FastAPI with SQLAlchemy 2 ORM, Pydantic schemas, Alembic migrations, and a
request-scoped SQLAlchemy session. SQLite is the file-backed local/test database; PostgreSQL is
the target database through `DATABASE_URL`. The React/TypeScript/Vite frontend remains a health
shell so Gate A authorization is exercised through direct HTTP API calls rather than a UI role
switch.

The implemented prototype intentionally reuses the existing Conda `ai_env` at Python 3.10.20.
This is a prototype limitation caused by the PM decision to avoid mutating a shared environment;
production migration to Python 3.12+ is a follow-up.

## Gate A data model

```text
clinics
  ├── clinic_memberships ── users
  └── patients ── patient_user_links ── users
        └── entries (stable identity, owner role, visibility, current_version)
              └── entry_versions (full immutable content snapshots)
              ├── comments (internal, read-only in Gate A)
              ├── conflicts (stale attempted content for internal review)
              └── audit_logs (metadata only; no note content)
```

The tables are `clinics`, `users`, `clinic_memberships`, `patients`, `patient_user_links`,
`entries`, `entry_versions`, `audit_logs`, `conflicts`, and `comments`. Entry types distinguish
patient-facing summary/instruction, staff notes, clinician sections, three system-authored
AI-scribed types, and system events. The seed uses synthetic values only.

## Authentication and authorization

`POST /auth/login` verifies an Argon2 password hash and sets a signed HS256 JWT in the
HttpOnly `nightingale_session` cookie. The token contains only `sub`, `iat`, and `exp`; no token
is placed in the JSON response. `GET /auth/me` derives memberships and patient links from the
database. Missing or short `SESSION_SECRET` values fail closed. Tests inject an explicit
test-only `Settings` object and never rely on a production fallback secret.

Every protected patient or entry lookup first resolves the authenticated user's membership or
exact patient link. An unknown or cross-clinic record returns `404`; an in-scope but forbidden
operation returns `403`; unauthenticated requests return `401`.

| Actor | Read scope | Gate A write scope |
| --- | --- | --- |
| patient | linked patient-facing summaries/instructions only | none |
| staff | all entries/comments in own clinic | own `staff_note` entries only |
| clinician | all entries/comments in own clinic | own `clinician_section` entries only |
| admin | all data in own clinic | read-only |
| system | seed/service records only | no login role |

Role, clinic, owner, and visibility are derived server-side. Extra client fields are ignored and
cannot turn a staff request into a clinician or cross-clinic write.

## Revision and conflict semantics

An entry starts at version 1 with a complete `entry_versions` snapshot. An edit executes an
atomic compare-and-swap on `entries.current_version = expected_version`. On success it appends a
new full snapshot, increments `current_version`, and records metadata-only audit fields. A revert
copies an earlier snapshot into a new version and records `reverted_from_version`; it never
deletes history.

If the compare-and-swap affects zero rows, the submitted text is stored in `conflicts` and the
API returns `409` with conflict ID, expected version, and actual version. The accepted snapshot
remains unchanged. This is deterministic stale-write handling, not role-priority overwrite.
Different entry IDs/sections use independent rows and therefore do not overwrite each other.

## Verification and trade-offs

Gate A evidence currently includes eight real FastAPI tests, `pytest --cov=app` at 83% total
coverage in the local run, a real Alembic `upgrade head` against an empty temporary SQLite
database, and two consecutive seed runs with stable counts of 2 clinics, 5 users, 2 patients,
7 entries, and 1 comment. The async tests use HTTPX `AsyncClient` plus `ASGITransport`, removing
the former `TestClient/httpx` warning rather than suppressing it.

SQLite keeps the 72-hour prototype runnable without Docker or a hosted service. PostgreSQL is
the stated target but is not claimed as locally provisioned. Full snapshots make audit and
revert behavior easy to inspect at prototype scale; a production deployment should revisit
retention, indexing, connection pooling, and migration operations after workload measurement.

Deferred work remains explicit: Gate B owns timeline/Glance View UX, complete comments workflow,
source-span provenance and trust interactions; Gate C owns redaction, provider boundary,
materialized warm reads and P95 measurement. No AI call is on the current read path.
