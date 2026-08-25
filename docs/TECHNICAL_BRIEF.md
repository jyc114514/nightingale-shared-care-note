# Nightingale technical brief - Phase 3 / Gate C local implementation

This brief records only behavior that exists in the local synthetic prototype. Gate C adds a
fail-closed redaction boundary, a typed deterministic fixture provider, synchronous write-path
processing, and a materialized Glance read model on top of the Gate A/Gate B foundation. It does
not claim a live external LLM, hosted PostgreSQL validation, deployment TLS, encryption at rest,
bonus learning, or final submission assets.

## Product boundary and runtime

Nightingale is a clinic-scoped longitudinal care-note workspace. Internal users see a compact
Glance View, a time-ordered timeline, immutable source navigation, comments, and revision trust
controls. Patient access remains a separate server-authorized projection containing only patient-
facing summaries and instructions.

The backend is FastAPI with SQLAlchemy 2, Pydantic, Alembic, and request-scoped sessions. SQLite
is the local/test database; PostgreSQL remains the target through `DATABASE_URL` but was not
provisioned or tested in this phase. The frontend is React/TypeScript/Vite with Tailwind CSS.
The browser sends credentialed requests and receives an HttpOnly signed session cookie; it never
receives a database service credential or a client-side role switch that changes authority.

The prototype intentionally reuses the existing Conda `ai_env` at Python 3.10.20. This is a
prototype limitation from the PM decision not to mutate a shared environment. Production
migration to Python 3.12+ is a follow-up. The repository root `requirements.txt` is the candidate
brief and is preserved unchanged.

## Data and trust model

```text
clinics
  ├── clinic_memberships ── users
  ├── patients ── patient_user_links ── users
  └── entries (stable identity, owner, visibility, occurred_at, source metadata)
        ├── entry_versions (full immutable content snapshots)
        ├── highlights (immutable source-version spans and review state)
        ├── comments (thread parent and resolution metadata)
        ├── conflicts (stale attempted content)
        └── audit_logs (metadata only; no note/comment body)
```

`occurred_at` is separate from creation time and the timeline uses deterministic
`occurred_at DESC, id DESC` ordering. Entries created by the system for doctor consult, nurse
consult, and patient AI-session summaries have distinct `source_kind` and non-empty
`source_reference` values. AI source text is never presented as clinician-confirmed by default.

Highlights store `source_entry_id`, `source_version_id`, inclusive/exclusive offsets, the exact
quote, a SHA-256 hash over its UTF-8 bytes, and `offset_unit=unicode_codepoint`. Creation checks
the source version, patient/clinic scope, Python string slice, and hash. Later entry revisions
create new `entry_versions`; they do not move or rewrite an existing highlight. Review state,
display priority, explicit `risk_level`, risk reason, action state, reviewer, and timestamps are
separate fields. `rejected` and `superseded` highlights remain resolvable through source history
but are excluded from the active Glance query.

Comments are internal, threaded by a self-reference, and scoped to one entry and clinic. Staff
and clinicians can read/write comments in their clinic; admins are read-only; patients cannot
read or mutate them. Resolve/unresolve stores reviewer metadata and an audit event without
copying the body into the audit row.

## Authorization and conflict semantics

| Actor | Read scope | Gate B mutation scope |
| --- | --- | --- |
| patient | linked patient-facing summaries/instructions and their timeline projection | none |
| staff | all internal entries, active Glance items, source spans, comments, history | own `staff_note` edits and comments; cannot review highlights |
| clinician | all internal entries, active Glance items, source spans, comments, history | own `clinician_section` edits, comments, manual highlights, accept/reject/review |
| admin | clinic-scoped internal read and source oversight | read-only |

The server resolves clinic membership and patient links on every protected route. Cookie-
authenticated writes require an allowed `Origin` when a browser sends one; production settings
fail closed unless `COOKIE_SECURE=true` and the session secret is sufficiently long. Direct
non-browser API tests without an `Origin` remain usable. A stale same-entry edit still returns a
deterministic `409`, preserves the attempted content in `conflicts`, and never uses silent
last-write-wins. A revert copies an earlier snapshot into a new version.

## Gate C redaction and processing boundary

The local provider boundary accepts only the Pydantic `RedactedPayload` contract. The processing
service first redacts deliberately supplied synthetic patient/staff/clinician names, Singapore
NRIC/FIN/IC/ID forms, and Singapore phone forms (+65, spaced/hyphenated, and local eight-digit
forms). It then runs a second detector. Any detector failure or remaining match creates a
`failed_redaction` job with a safe category code and does not call the provider.

`FixtureProvider` is deterministic and has no network, API key, or external model dependency.
Its validated output creates a new `system`-authored AI-scribed entry and a `suggested`
highlight anchored to that entry's first immutable version and exact codepoint span. It never
updates a human entry. Idempotency keys prevent duplicate entries; malformed or unavailable
provider output creates only a failed job. Job payloads, audit rows, and logs do not contain raw
input, provider prompts, or provider responses.

The active `GET /patients/{patient_id}/glance` endpoint reads only `patient_glance_items`, with
clinic authorization, deterministic ordering, a six-item cap, and rejection/supersession filters.
Highlight creation/review and seed updates refresh the projection. This is a local materialized
read model; no external provider is present on the warm read path.

## Gate B API and UI path

The implemented routes include:

- `GET /patients/{patient_id}/timeline` with server-side patient projection;
- `GET /patients/{patient_id}/glance` with a maximum of six active items;
- `GET /highlights/{highlight_id}/source` for exact immutable source resolution;
- `POST /entry-versions/{version_id}/highlights` for clinician-created manual highlights;
- `PATCH /highlights/{highlight_id}/review` for clinician trust decisions;
- `GET/POST /entries/{entry_id}/comments` and `PATCH /comments/{comment_id}/resolution`;
- Gate A login, `/auth/me`, patient, version, diff, edit, revert, and conflict routes.
- `POST /patients/{patient_id}/ai-processing` and `GET /ai-processing/{job_id}` for the local
  redacted fixture write path and safe job metadata.

The UI uses real cookie login and `/auth/me`, clinic-scoped patient selection, a calm light
clinical layout, a six-or-fewer-item Top Card, timeline source labels, AI review badges, source
navigation with validated `Array.from` codepoint quote highlighting and deep-link restoration,
comments/replies/resolve controls, history/diff/revert controls, optimistic-concurrency conflict
comparison, and role-aware review/edit controls. The patient projection does not render
internal Glance, comments, raw AI notes, or review states because the server does not return them.

## Verification actually performed

- Backend full pytest, Ruff check/format, mypy `app tests`, and `pip check` pass in the existing
  Python 3.10.20 environment. The required Gate A tests remain present; Gate B and Gate C add
  migration, provenance, API, security, comments, timeline, trust, redaction, provider-boundary,
  AI-processing, materialized-read, and log-safety coverage.
- `test_migrations.py` runs real Alembic upgrade/check/downgrade/re-upgrade against temporary
  file-backed SQLite, checks the revision and key indexes/columns, proves seed fails before
  migration, and proves consecutive seed counts are stable without `Base.metadata.create_all`.
- The exact twelve-check `test_highlight_provenance.py` exercises manual/AI source identity,
  exact slices, hash, Unicode offsets, old-version resolution, invalid offsets/quotes,
  cross-source, patient, cross-clinic, and review authorization behavior.
- Frontend Vitest, ESLint, Prettier check, TypeScript type-check, and Vite production build pass.
  Playwright completed `8 passed` against real Uvicorn, real Vite, migrated synthetic SQLite, and
  two viewports: 1440x900 and 390x844. It covered exact source/deep-link/review, diff/revert/
  thread, real 409 conflict, and patient privacy. The runner cleaned ports 8000/5173, the
  temporary database, and the generated password.

- The real-TCP warm-path benchmark used file-backed SQLite, 26 synthetic patients, 208 benchmark
  entries/highlights/materialized rows, 50 warm-up requests, 1,000 measured requests, and
  concurrency 10. It recorded P50 55.736 ms, P95 78.477 ms, P99 106.919 ms, max 129.497 ms,
  zero errors, and six response items. See
  `docs/evidence/gate_c_warm_path.md` and its JSON companion. This is a measured local
  approximation, not hosted PostgreSQL production evidence. UX-01 still needs a human timed
  review.

PostgreSQL integration, external provider authorization, deployment TLS/encryption-at-rest,
bonus importance/data decay, voice, final PDF, attribution audit, and video remain uncompleted.
