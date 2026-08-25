# Nightingale Technical Brief

## A trust-centered longitudinal shared-care note

Status: Phase 4 local synthetic prototype, measured on 2026-08-26.

Nightingale is a clinic-scoped collaboration layer for the moment when a care team needs to
understand what changed and what needs action in under ten seconds. It is not an EHR replacement,
diagnostic system, or autonomous medical decision-maker. AI-scribed content is a suggestion until
clinician review; explicit medical risk, display ranking, provenance, and human confirmation are
separate fields.

## 1. System boundary and architecture

The browser uses a real FastAPI application through credentialed cookie requests. Authorization is
resolved server-side from clinic membership or a patient link on every protected route. The local
database is SQLite; PostgreSQL is the target through `DATABASE_URL` but was not provisioned in this
prototype. The existing shared `ai_env` remains at Python 3.10.20 by PM decision; production
migration to Python 3.12+ is a follow-up.

```text
Browser: React + TypeScript + Vite + Tailwind
       │ HttpOnly session cookie / Origin guard
       ▼
FastAPI routes ──► clinic + role authorization
       │                     │
       │                     ├── immutable EntryVersion + metadata audit
       │                     ├── CAS edit ──► 409 Conflict record
       │                     ├── exact Highlight ──► source version/span
       │                     └── async write path: redact → typed fixture provider
       ▼
Materialized projections
  patient_glance_items  ◄── bounded per-clinic importance feedback
  archival_summaries    ◄── deterministic hot/warm/cold refresh
       │
       └── warm reads contain no provider/LLM call
```

The AI boundary is deliberately local and deterministic. A typed redacted payload is validated
before the fixture provider; a second detector makes the redaction path fail closed. No API key,
external model, raw note text, patient identifier, quote, or embedding is required by the local
implementation.

## 2. Data, provenance, and retention semantics

```text
Clinic ── Membership ── User
   │
   └── Patient ── PatientUserLink ── User
          │
          └── Entry (stable identity, owner, visibility, occurred_at, source metadata)
                 ├── EntryVersion (immutable full snapshot)
                 ├── Highlight (immutable version + exact codepoint span + quote hash)
                 ├── Comment (parent thread + resolution metadata)
                 ├── Conflict (expected/actual version + attempted content)
                 └── AuditLog (metadata only)

Highlight ── PatientGlanceItem (materialized ranking/read projection)
Highlight ── FeedbackEvent ── ImportanceProfile (clinic-scoped, rebuildable)
Entry/Version ── ArchivalSummary ── ArchivalSummarySource (derived pointers only)
```

Every highlight stores `source_entry_id`, immutable `source_version_id`, inclusive/exclusive
Unicode-codepoint offsets, the exact quote, and a SHA-256 hash. Later edits create a new version;
they do not move the old highlight. A revert copies an earlier snapshot into a new version. A stale
same-section write preserves both submissions and returns `409`; it never silently chooses a
winner.

The context endpoint exposes three retrieval bands:

| Band | Local policy | Returned material |
| --- | --- | --- |
| Hot | last 14 days, or protected by open action/risk/conflict/discussion/pin/confirmation/care plan | full current immutable detail |
| Warm | 14–90 days and not protected | metadata index; source remains canonical |
| Cold | older than 90 days and not protected | deterministic period summary + manifest + source entry/version pointers |

Archival summaries are derivatives, not canonical records. Refresh is an explicit write operation
for staff/clinicians; a context read never generates or calls a provider. Patient projection filters
both hot/warm entries and archival source pointers to patient-facing summary/instruction records,
excluding internal comments and raw AI-scribed notes.

Adaptive ranking is explainable and bounded:

```text
final display priority = clamp(
  base + recency + explicit risk + unresolved action
  + clinician confirmation + adaptive feedback,
  0, 100
)
```

Adaptive feedback is clinic-scoped, idempotent, based only on a closed structured feature
signature, and bounded to `[-12, +12]`. It changes display priority only; it cannot mutate
`risk_level`, source spans, or clinician truth. The UI explicitly says: “Ranking priority, not a
medical risk score.”

## 3. Evidence, trade-offs, and remaining boundary

Implemented and checked locally:

- Backend: 46 real-application tests, 97% coverage, Ruff check/format, mypy, pip check.
- Schema: Alembic head `0006_gate_d_archival`; fresh, downgrade/re-upgrade, legacy repair, and
  `alembic check` paths pass without `Base.metadata.create_all()` in seed.
- Seed: two consecutive synthetic runs preserve 2 clinics, 5 users, 2 patients, 7 entries, 5
  highlights/Glance rows, 2 comments, 1 archival summary, and 2 source pointers.
- Frontend: 8 Vitest tests, ESLint, Prettier, TypeScript, and production Vite build pass.
- Browser: 8 Playwright checks pass at 1440x900 and 390x844, including provenance/deep-link,
  ranking feedback, revisions/comments, a real `409`, Historical context source pointers, and
  patient privacy.
- Gate C warm path: real Uvicorn TCP benchmark with 26 patients, 208 entries/highlights, 50
  warm-up requests, 1,000 measured requests, concurrency 10, zero errors; P50 55.736 ms, P95
  78.477 ms, P99 106.919 ms, max 129.497 ms.

The central trade-off is trust over automation: materialized reads and deterministic providers
make the demo reproducible and auditable, while real external-provider quality and hosted database
behavior remain unclaimed. SQLite is a fast local approximation, not PostgreSQL production proof.
TLS/encryption-at-rest evidence depends on a deployment platform. UX-01 still needs a human timed
10-second review. Voice, self-learning beyond the bounded bonus, and live LLM integration are out
of scope for this prototype.

## Demo scenarios

Scenario A: clinician opens a Glance item, expands “Why ranked?”, pins/unpins it, follows the exact
immutable source span, and accepts/rejects a suggestion.

Scenario B: staff edits a role-owned note, compares versions, reverts as a new version, and adds a
nested internal comment that can be resolved/unresolved.

Scenario C: two writes use the same expected version; the stale write returns `409` and remains
visible beside the winner. The user then refreshes Historical context and opens a canonical source
pointer from a derived summary.

## Delivery limitation

The PDF, screenshots, and local rehearsal package are delivery artifacts, not deployment evidence.
The GitHub mirror is only acceptable as a private repository after explicit user-authorized upload;
no public repository, email, or deployment is implied by this brief.
