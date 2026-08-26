# Nightingale Technical Brief

## A trust-centered longitudinal shared-care note

Status: Phase 8 local prototype with an optional DeepSeek adapter, measured on 2026-08-26 at
application checkpoint `d0caff7`.

Nightingale is a clinic-scoped collaboration layer for the moment when a care team needs to
understand what changed and what needs action quickly. It is not an EHR replacement, diagnostic
system, or autonomous medical decision-maker. AI-scribed content remains a suggestion until
clinician review; explicit risk, display ranking, provenance, and human confirmation are separate.

## 1. System boundary and architecture

The browser uses a real FastAPI application through credentialed cookie requests. Authorization is
resolved server-side from clinic membership or a patient link on every protected route. The local
database is SQLite; PostgreSQL is the target through `DATABASE_URL`, but was not provisioned. The
shared `ai_env` remains at Python 3.10.20 by PM decision; production migration to Python 3.12+
remains follow-up work.

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

## 4. Evidence, trade-offs, and remaining boundary

Implemented and independently checked at the Phase 8 application checkpoint:

- Backend: **71 passed**, **88%** reproducible coverage, Ruff, mypy, pip check; Alembic head
  `0008_collaboration_events`, including fresh, legacy, downgrade/re-upgrade, and `alembic check`.
- Frontend: **19 Vitest tests**, ESLint, Prettier, TypeScript, and Vite production build.
- Browser: **12 Playwright checks** at 1440x900 and 390x844, including Chinese chrome, exact
  provenance persistence, distinguishable original-record rows, contextual comments/tasks,
  Desktop/Mobile preview, mentions, assignments, two-browser SSE invalidation, conflict handling,
  and patient privacy.
- Clean clone: the prior clean-clone rehearsal from `3129da3` passed the Phase 7 baseline; no
  Phase 8 clean-clone rehearsal or hosted-provider guarantee is claimed in this local run.
- Warm path: real Uvicorn TCP, file-backed SQLite approximation, 26 patients, 208 entries/highlights,
  50 warm-up, 1,000 measured requests, concurrency 10, zero errors; P50 **49.774 ms**, P95
  **67.823 ms**, P99 **80.593 ms**, max **86.835 ms**.

The central trade-off remains trust over automation. Materialized reads and the fixture provider
make the default prototype reproducible; the optional adapter adds network, balance, provider-data
processing, and latency dependencies. SSE is invalidation only, not simultaneous character editing;
CRDT/OT is intentionally not implemented. One-click startup is a Windows convenience, not
deployment. Hosted PostgreSQL, TLS/encryption-at-rest, model quality, production retention/deletion
policy, final video, and human UX-01 sign-off remain unclaimed.

## Demo scenarios

Scenario A: switch English/中文 chrome, open a Glance source, inspect the exact immutable span,
wait beyond the focus animation, and close the source without changing the clinical text.

Scenario B: staff edits/reverts a note, opens the contextual Comments drawer, types `@` and selects
a clinic collaborator, opens the contextual task drawer, creates/completes an assigned task linked
to the comment, while a second browser receives the metadata-only SSE invalidation.

Scenario C: two writes use one expected version; the stale write returns `409` and remains beside
the winner. Historical context discloses a derived summary that is not the original record and
offers labelled immutable original-record rows.

Optional Phase 8: staff or clinician opens **AI Scribe Demo**, confirms the synthetic-only warning,
checks the active fixture/DeepSeek provider badge, and generates a suggestion. The resulting entry
is system-authored, suggested, source-linked, and requires clinician review.

## Delivery limitation

The PDF, screenshots, source ZIP, and local rehearsal package are delivery artifacts, not hosted
compliance evidence. No GitHub push, deployment, or email submission is implied by this brief. The
DeepSeek adapter is integrated as an optional live path, but one smoke does not establish model
quality, provider compliance, or production reliability. Voice capture remains explicitly out of
scope.
