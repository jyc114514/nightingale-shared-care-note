# Nightingale Technical Brief

## A trust-centered longitudinal shared-care note

Status: Phase 9 final release candidate with an optional DeepSeek adapter, a live Render evaluation,
bounded prerecorded Voice fixtures, and independent UX-01 evidence, measured on 2026-08-28.

Nightingale is a clinic-scoped collaboration layer for the moment when a care team needs to
understand what changed and what needs action quickly. It is not an EHR replacement, diagnostic
system, or autonomous medical decision-maker. AI-scribed content remains a suggestion until
clinician review; explicit risk, display ranking, provenance, and human confirmation are separate.

## 1. System boundary and architecture

The browser uses a real FastAPI application through credentialed cookie requests. Authorization is
resolved server-side from clinic membership or a patient link on every protected route. The local
database is SQLite; the live Render service runs against the managed PostgreSQL 18 resource using
the normalized psycopg URL path. The shared `ai_env` remains at Python 3.10.20 by PM decision; the
production Docker image targets Python 3.12.

```text
Browser: React + TypeScript + Vite + Tailwind
       | HttpOnly session cookie / Origin guard / bilingual chrome
       v
FastAPI routes
       | clinic + role authorization
       | immutable writes / CAS conflicts / redaction boundary
       | metadata-only collaboration events -> SSE invalidation
       v
Canonical records
  entries -> entry_versions -> highlights -> exact source spans
  comments -> mentions
  tasks -> task_conflicts -> task_glance_items
  audit_logs -> collaboration_events (no raw content)
       |
Materialized projections
  patient_glance_items + task_glance_items -> bounded Glance read
  importance profiles -> explainable ranking feedback
  archival summaries -> hot/warm/cold derived context pointers
```

AI processing remains fixture-first and deterministic by default. A typed redacted payload is
validated before either provider; a second detector makes redaction fail closed. DeepSeek is an
explicit optional adapter, not a default dependency. No API key, patient identifier, quote,
embedding, or raw note text is required by the local fixture path.

## 2. Data, provenance, and collaboration semantics

Every highlight stores `source_entry_id`, immutable `source_version_id`, Unicode-codepoint offsets,
the exact quote, and a SHA-256 hash. Later edits create a new version; a revert copies an earlier
snapshot into a new version. A stale same-section write preserves the attempted content and returns
`409`.

Mentions are stable `comment_id` to `mentioned_user_id` records. The server accepts only active
staff/clinician members of the same clinic and deduplicates the pair. Comment bodies are never
parsed to guess an identity. Patients cannot read or create internal comments/mentions.

Tasks are clinic-scoped internal records with optional entry/comment source pointers, title,
assignee, `open`/`in_progress`/`done` status, version, and completion timestamp. Assignees are
validated server-side. A stale task update creates a preserved task conflict and returns `409`;
audit rows contain identifiers and versions, never titles or bodies. Open/in-progress tasks are
materialized as Glance actions; completing a task removes its active projection without changing
any explicit risk or provenance field.

`GET /patients/{patient_id}/events` is a persisted metadata-only SSE invalidation stream. It uses
cookie authentication, clinic/patient scope, monotonic `event_id`, `Last-Event-ID` reconnect,
heartbeat, bounded polling, and disconnect cleanup. Its payload contains only resource type/id
and event kind. The browser refetches canonical comments/tasks/Glance APIs; it never treats SSE as
source of truth and does not overwrite a dirty editor.

The UI supports English and Simplified Chinese for application chrome, Help, labels, statuses,
ARIA names, safety explanations, and the Desktop/Mobile demo-preview selector. Comments and task
actions open in a fixed contextual drawer rather than a distant responsive aside. It deliberately
does not translate clinical notes, comments, quotes, revisions, conflict content, source references,
or other user-entered source data.

## 3. Optional DeepSeek provider boundary

`LLM_PROVIDER=fixture` remains the default and makes ordinary tests and demos network-free. An
explicit `LLM_PROVIDER=deepseek` selects the `deepseek-v4-flash` Chat Completions adapter at
`https://api.deepseek.com`; JSON output and disabled thinking are requested with a bounded token
limit and at most one retry for transient connection/5xx failures.

The external request contains only the system safety instruction, interaction type, redacted
synthetic interaction text, and the JSON shape example. `source_reference`, patient/clinic/user
IDs, names, phones, IC/ID values, comments, tasks, cookies, and raw note text stay local. The model
returns only summary/quote/action fields. The application sets `risk_level=null`, status
`suggested`, system authorship, immutable local codepoint offsets, quote hash, provenance, and
materialized Glance state. Invalid/duplicate/missing quotes fail closed; provider failures never
silently become fixture output.

The Windows launcher reads an external key file only when `.nightingale-local.json` explicitly
selects DeepSeek. It passes the key to the backend child process, clears the parent variable before
starting Vite, and writes no key or key-file path to logs, runtime metadata, browser responses, or
artifacts. The bounded synthetic live smoke is recorded in
[`deepseek_live_smoke.md`](evidence/deepseek_live_smoke.md); it is not a quality evaluation.

## 4. Prerecorded Voice and Render boundary

The local Voice path is intentionally fixture-first. It contains two small, prerecorded synthetic
WAV signal fixtures, immutable prepared timestamped transcript segments, timestamp links, audio
hashes, safe role/patient scope, and the existing redaction-gated fixture/DeepSeek summary path.
The UI labels the achieved state as: “Architecture/demo only: prerecorded synthetic audio with
prepared timestamped transcript; ASR inference unavailable in this environment.” The optional
faster-whisper adapter is lazy and injection-testable, but the Turbo model download did not
complete and no model weights are committed or packaged. There is no microphone, diarization,
continuous ambient capture, production PHI audio, or ASR accuracy claim.

The production readiness path uses a multi-stage Docker build, same-origin FastAPI static serving,
Alembic-before-seed startup, secure production settings, one Free Render Web Service, and one Free
Render Postgres database. Render is configured for `LLM_PROVIDER=fixture` and
`VOICE_PROVIDER=fixture` for the deployed prerecorded fixture path. The external deployment now runs against
Render PostgreSQL 18 at `https://nightingale-shared-care-note.onrender.com`; migration/seed,
HTTPS, provider encryption, and authenticated Clinical/Staff/Patient browser evidence are recorded
separately. The online prerecorded Voice fixture passed for both Clinical and Patient projections
without claiming full Ambient Voice.

## 5. Evidence, trade-offs, and remaining boundary

Implemented and independently checked at the Phase 9 local checkpoint:

- Backend: **85 passed**, actual coverage recorded after the Voice addition, Ruff, mypy, pip check;
  Alembic head `0010_postgres_compat`, including fresh, legacy, downgrade/re-upgrade, and
  `alembic check`. A real PostgreSQL 18 GitHub Actions gate also passed the full migration chain,
  schema/FK assertions, seed idempotency, and the backend suite.
- Frontend: **37 Vitest tests**, ESLint, Prettier, TypeScript, and Vite production build.
- Browser: **18 Playwright checks** at 1440x900 and 390x844, including Chinese chrome, exact
  provenance persistence, distinguishable original-record rows, contextual comments/tasks,
  Desktop/Mobile preview, mentions, assignments, two-browser SSE invalidation, conflict handling,
  patient privacy, Voice sample scope, timestamp seeking, and source navigation.
- Clean clone: the final-source clean-clone rehearsal is recorded separately in
  [`clean_clone_rehearsal.md`](evidence/clean_clone_rehearsal.md); its result is a release gate and
  not a hosted-provider guarantee.
- Warm path: real Uvicorn TCP, file-backed SQLite approximation, 26 patients, 208 entries/highlights,
  50 warm-up, 1,000 measured requests, concurrency 10, zero errors; P50 **44.283 ms**, P95
  **56.053 ms**, P99 **81.509 ms**, max **89.495 ms**.

The central trade-off remains trust over automation. Materialized reads and the fixture provider
make the default prototype reproducible; the optional adapter adds network, balance, provider-data
processing, and latency dependencies. SSE is invalidation only, not simultaneous character editing;
CRDT/OT is intentionally not implemented. One-click startup is a Windows convenience, not
deployment. Render PostgreSQL, HTTPS/TLS, and provider encryption-at-rest evidence are now recorded
for the synthetic evaluation deployment. Model quality and production retention/deletion policy
  remain outside this evaluation; independent UX-01 evidence is recorded separately. The original
  final video is a local submission artifact and its content QA remains a separate human-review gate.

### Independent UX-01 evidence

An anonymous independent participant using the supported Simplified Chinese interface completed the
defined glance task in approximately nine seconds without coaching. The highest-priority item,
action/state, risk-versus-ranking distinction, and source affordance were all correct. Role and
viewport were not separately recorded. This is evidence of information hierarchy in a supported
locale, not a formal usability study or a statistical claim.

## Demo scenarios

Scenario A: Staff opens the English workspace, reads the Glance card, opens an AI-scribed source,
inspects the exact immutable span, and closes the source without changing clinical text. The
independent Simplified Chinese UX result is recorded separately: approximately nine seconds,
without coaching, with all four defined answers correct.

Scenario B: Staff edits the existing Staff note because the deployed UI has no new-note composer,
opens the contextual Comments drawer, types `@` and selects a clinic collaborator, creates an
assigned task, and then Clinician reviews task progress and a plan revision with History, Compare,
and Revert. Task lifecycle and second-browser SSE are covered by local application evidence; the
final recording's actual content is assessed separately.

Scenario C: two writes use one expected version; the stale write returns `409` and remains beside
the winner. Historical context discloses a derived summary that is not the original record and
offers labelled immutable original-record rows.

Optional Phase 8: staff or clinician opens **AI Scribe Demo**, confirms the synthetic-only warning,
checks the active fixture/DeepSeek provider badge, and generates a suggestion. The resulting entry
is system-authored, suggested, source-linked, and requires clinician review.

Optional Voice path: staff or clinician opens **Ambient Voice Prototype**, plays a prerecorded
synthetic fixture, selects a prepared timestamped transcript segment, and opens its generated
source. Patients receive only the patient sample and no internal source identifiers. The deployed
Voice path is bounded prerecorded synthetic audio; ASR inference is unavailable, and there is no
diarization or microphone capture.

## Delivery limitation

The PDF, screenshots, source ZIP, submission ZIP, and local rehearsal package are delivery artifacts,
not clinical compliance evidence. The GitHub repository remains private; the original MP4 is
included only in the submission ZIP and is not uploaded to GitHub. No email submission or public
visibility change is implied by this brief. The DeepSeek adapter is integrated as an optional live
path, but one smoke does not establish model quality, provider compliance, or production
reliability. Full Voice capture remains out of scope beyond the prerecorded synthetic demo path.
