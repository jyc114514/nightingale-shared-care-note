# Nightingale 72-hour build: project plan

## 1. Current conclusion

The web ChatGPT analysis identified the correct product thesis: this is a trust-centered longitudinal collaboration layer, not a generic medical chatbot or an EHR replacement. Its strongest recommendations are the Glance View, span-level provenance, real server-side RBAC, immutable revision history, async AI processing, and deferring ambient voice.

It is not safe to execute that analysis unchanged. The corrected plan below addresses the material gaps.

| Web analysis claim | Judgment | Correction |
| --- | --- | --- |
| Prioritize Glance View, timeline, provenance, RBAC, and revision history | Correct | These are mandatory gates. |
| Bonus is numerically large | Correct but incomplete | Bonus is up to 10 versus 20 base points, but it must not displace a broken mandatory gate. |
| Put comments/mentions after bonus work | Incorrect for comments | Threaded comments and their demo path are core collaboration. Mentions and assignment are optional. |
| Use span-level provenance | Correct | Anchor to an immutable source version as well as offsets; otherwise edits invalidate offsets. |
| Use an explainable adaptive weight system | Viable | Scope learning per clinic, separate ranking from medical risk, include negative feedback, and prove the before/after effect. |
| Old medical data is never deleted | Unsupported generalization | Preserve canonical sources in this prototype, but describe retention as policy-controlled. Summaries are derivatives, never the source of truth. |
| Supabase is automatically the best stack | Plausible, not established | Hosted PostgreSQL is useful, but local Docker, Supabase CLI, and `psql` are absent. Prefer an app stack that can start without Docker and add a hosted database through one connection string. |
| Resolve concurrent conflicts by role priority | Unsafe if used as overwrite logic | Return `409`, preserve both submissions, and require review. Clinician authority applies to semantic confirmation, not silent data loss. |
| “No PHI Redaction Pipeline” is definitely a typo | Strong inference, not a fact | Follow the unambiguous next sentence: redact names, IC/ID, and phones before any external LLM call. Document the wording ambiguity. |
| Leave all documentation and demo work to the final six hours | Too risky | Create delivery skeletons at the start and freeze features roughly 11 hours before the deadline. |

## 2. Verified baseline at plan time

- Source brief: `requirements.txt`
- Current SHA-256: `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5`
- During planning, another writer reformatted the brief from 3 long lines to 116 readable lines at 18:07. The initial hash was `09E68CF80294387F355C243DD70F14CD50AB35D15FFEFE0B11C7F6346DA0E471`; all core clauses, test names, scoring rows, deadline, and deliverables were rechecked in the current version. Preserve the current version rather than restoring the earlier formatting.
- Actual workspace path: `D:\NTU学习\Nightingale_project`
- The path `D:\NTU学习\Nightingale\_project\requirements.txt` does not exist; it was a path typo in the request.
- Workspace initially contains only `requirements.txt`; it is not yet a Git repository.
- Snapshot time: 2026-08-25 18:00 +08:00.
- Submission deadline: 2026-08-28 17:30 SGT/MYT (+08:00), leaving about 71.5 hours at the snapshot.
- Available: Git 2.53, Node 24.16, npm 11.13, pnpm 11.22, and uv 0.11.
- Not on PATH: Python, Docker, Supabase CLI, `psql`, and the VS Code `code` command.
- A `.vscode/extensions` directory exists with Python, Pylance, Jupyter, and PowerShell extensions, but no VS Code executable was found in normal install locations or Start Apps. Verify/install VS Code before relying on it.

## 3. Product contract

### One-sentence product

A clinic-scoped shared care note that lets staff and clinicians understand what changed and what needs action in under ten seconds, while every suggestion remains traceable to immutable human or AI-scribed evidence.

### Primary demo user journey

1. A staff user signs in and opens a synthetic patient.
2. The Glance View shows no more than six ranked items: new information, unresolved actions, explicit flags, and clinician-confirmed context.
3. Each item displays status, reason for ranking, source, and available action.
4. Clicking the source jumps to the exact source span in the longitudinal timeline.
5. Staff adds a note and comment; clinician signs in, reviews it, edits a clinician-owned section, accepts or rejects an AI suggestion, inspects the diff, and reverts by creating a new version.
6. An attempted cross-role or cross-clinic write fails at the API layer.
7. A second similar item rises in display priority after scoped clinician feedback, without changing its explicit medical risk level.

### Non-goals for the first submission

- EHR replacement or clinical decision support.
- Diagnosis or treatment recommendations.
- Character-perfect Google Docs collaboration or CRDT/OT.
- Production identity verification, billing, or a real patient portal.
- Real PHI or real clinic data.
- Ambient voice unless all mandatory acceptance gates and delivery assets are already complete.

### Minimum screen map

1. Demo sign-in with separate seeded identities; no client-side role dropdown that changes authority.
2. Clinic-scoped patient list.
3. Shared Care Note page containing the Glance View and longitudinal timeline.
4. Entry detail/history panel containing exact source span, comments, diff, revert, and conflict state.
5. Patient-facing page containing only approved summaries and instructions.

Admin needs clinic-scoped oversight, but a separate admin dashboard is not required for the scored demo if the authorization path is proven by API tests.

## 4. Scope and gates

### Gate A: mandatory data and security foundation

- Four roles with real authenticated demo identities: patient, staff, clinician, admin.
- Clinic-scoped reads and writes enforced in backend dependencies/services.
- Role-owned sections and entry types; staff cannot edit clinician content and vice versa.
- Patient response DTOs omit internal comments and raw AI-scribed notes.
- Immutable versions, metadata-only audit log, revert-as-new-version.
- Optimistic concurrency with `expected_version`; stale same-section writes produce `409` and a preserved conflict record.

### Gate B: mandatory clinical communication experience

- Patient page with a glanceable Top Card and continuous timeline.
- Three distinct system-authored AI-scribed entry types.
- Threaded comments with resolve/unresolve.
- Optional lightweight mention and assignment only after comments work.
- Exact source navigation for manual and AI-derived highlights.
- Human confirmation states: suggested, accepted, rejected, superseded, conflict-review.

### Gate C: AI, privacy, and performance

- Provider interface plus deterministic synthetic fixture, so the demo does not depend on a live model call.
- External LLM integration only after server-side redaction and schema validation.
- Async write-path processing; Glance View reads materialized rows.
- Warm-path P95 measurement artifact with method, request count, concurrency, dataset, and result.

### Gate D: bonus

- Explainable per-clinic feedback adaptation for display priority.
- Hot/warm/cold retrieval representation with canonical source links and a policy-controlled retention statement.
- No voice work unless Gates A–C, all required tests, README, brief skeleton, and demo script are already green.

## 5. Recommended architecture

### Stack

- Backend: Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, Alembic, pytest.
- Frontend: React, TypeScript, Vite, Tailwind CSS, shadcn/ui, TanStack Query.
- Database target: managed PostgreSQL through `DATABASE_URL` (Supabase Postgres or Neon are both acceptable).
- Local bootstrap: SQLite may unblock the first scaffold, but final authorization, concurrency, and provenance integration tests must run against PostgreSQL before submission.
- Authentication: server-issued signed HttpOnly session/JWT for seeded synthetic users. Do not use a client-side role switcher as authentication.
- Live update: start with invalidation/polling; add SSE only if the mandatory path is already stable.
- Deployment: prefer one backend service that can serve the built frontend, plus managed PostgreSQL. This reduces demo failure points.

### Why this is preferred over a pure Next.js/Supabase build

- The brief names exact Python micro-test files; a Python backend makes those tests first-class instead of wrappers around a TypeScript implementation.
- Server-side permission tests, optimistic concurrency, revision transactions, and redaction tests are direct and deterministic.
- React still gives enough speed for a polished Top Card and timeline.
- It avoids making Docker or a local Supabase stack a critical dependency on this machine.

The cost is two development processes and a small API boundary. Keep the API narrow and serve the built frontend from the backend for the final demo.

### Minimum API contract

- `POST /auth/login` and `POST /auth/logout`
- `GET /me`
- `GET /patients`
- `GET /patients/{patient_id}/glance`
- `GET /patients/{patient_id}/timeline`
- `POST /patients/{patient_id}/entries`
- `PATCH /entries/{entry_id}` with `expected_version`
- `GET /entries/{entry_id}/versions`
- `POST /entries/{entry_id}/revert`
- `POST /entries/{entry_id}/comments`
- `POST /comments/{comment_id}/resolve`
- `POST /highlights/{highlight_id}/feedback`
- `POST /ingest/ai-scribed` for the three required interaction types

The final route names may differ, but every capability must have one canonical authorization and transaction path.

### Request and processing paths

```text
Browser
  -> authenticated FastAPI endpoint
  -> clinic and role authorization
  -> PostgreSQL transaction
  -> immutable version + audit metadata
  -> async redaction / extraction / ranking job
  -> materialized patient_glance_items

Warm Glance read
  -> authenticated endpoint
  -> one clinic-scoped materialized query
  -> response without any LLM call
```

## 6. Data model decisions

Minimum entities:

- `clinics`
- `users`
- `clinic_memberships` with role
- `patients` with clinic ownership
- `entries` as stable identity and ownership/type metadata
- `entry_versions` as immutable snapshots
- `comments` and `comment_events`
- `tasks`
- `highlights`
- `provenance_anchors`
- `highlight_feedback`
- `importance_profiles` scoped to clinic
- `conflicts`
- `audit_logs` containing metadata only
- `patient_glance_items` as materialized read model
- `archival_summaries` for the data-decay bonus

Provenance anchor fields must include at least:

- `source_entry_id`
- `source_version_id`
- `span_start`
- `span_end`
- `quoted_text`
- `quoted_text_hash`

Offsets alone are insufficient because later edits change text. A highlight remains linked to the exact immutable version that produced it.

### Authorization matrix

| Resource/action | Patient | Staff | Clinician | Admin |
| --- | --- | --- | --- | --- |
| Patient-facing summary/instruction in own record | Read | Read | Read/write | Read |
| Raw AI-scribed entry | No | Only if explicitly allowed by clinic policy; default read for staff demo | Read | Read |
| Internal comment | No | Read/write | Read/write | Read |
| Staff-owned note | No | Create/edit own role section | Read | Read |
| Clinician-owned note/plan | No | Read only | Create/edit own role section | Read |
| Highlight accept/reject | No | Yes | Yes | Oversight only |
| Cross-clinic patient data | No | No | No | No |

The brief explicitly grants clinicians access to staff notes and all AI-scribed notes. It is less explicit about staff access to raw AI-scribed notes; the final implementation must document the chosen policy and keep the patient prohibition absolute.

### Synthetic test topology

- Clinic A: one admin, one staff user, one clinician, and patient Sarah Tan.
- Clinic B: one staff user, one clinician, and a different patient.
- Sarah's story covers a medication dose change, a later patient-reported symptom, an overdue follow-up task, a clinician confirmation, and one deliberately conflicting AI suggestion.
- Clinic B exists primarily to prove cross-clinic denial and that learning weights do not leak across clinics.
- Redaction fixtures use clearly labeled synthetic names/IDs/phones and are never presented as real records.

## 7. Trust and conflict semantics

- AI suggestions never edit a human source entry.
- An accepted suggestion changes the suggestion state and may create a clinician-confirmed derived item; it does not rewrite history.
- A rejected suggestion remains auditable but disappears from the active Glance View.
- Semantic disagreement between AI/patient memory and a clinician entry creates a visible conflict or supersession relationship.
- Concurrent write conflict and clinical truth conflict are different concepts and use different records.
- Same-section concurrency never silently chooses the clinician or latest timestamp; it preserves both payloads and asks for adjudication.

## 8. Importance learning design

The bonus mechanism changes display ranking only. It must not infer a new risk level, diagnosis, or treatment urgency.

Suggested initial score:

```text
display_priority =
    recency_feature
  + explicit_source_risk_feature
  + unresolved_task_feature
  + entity_feature
  + clinician_confirmed_feature
  + bounded_feedback_adjustment
```

- Use normalized, documented weights.
- Positive events: accept, pin, manual highlight, resolved-after-action.
- Negative events: reject, unpin, dismiss.
- Store feature counters or weights per clinic; do not learn across clinics.
- Define “similar” deterministically from entry type, tagged entity category, and normalized topic/keyword features for the prototype; do not add an embedding service unless the deterministic test is already green.
- Bound the feedback adjustment so repeated clicks cannot bury explicit high-risk or unresolved items.
- The bonus test must show the same base features before and after one or more interactions and assert a real ranking/score increase for a similar item.

## 9. PHI and LLM boundary

- The brief's phrase “No PHI Redaction Pipeline” is grammatically ambiguous. The following sentence is operationally clear and takes precedence: redact names, IC/ID numbers, and phones before sending text to an LLM.
- The application uses synthetic data, but the redaction path must still be real and tested.
- Perform deterministic regex redaction for SG-style IC/ID and phone patterns plus a known-entity/name pass for the synthetic dataset.
- Validate the redacted payload before the provider call; fail closed if a detector still finds a prohibited pattern.
- Never put raw note content in application logs, exception messages, analytics, or audit logs.
- Voice is deferred because cloud transcription would create an earlier PHI boundary that the text-only redactor does not solve.

## 10. Timebox from the verified snapshot

| Absolute checkpoint (+08:00) | Elapsed | Exit condition |
| --- | ---: | --- |
| Aug 25 22:00 | 4 h | Git/scaffold, dependency lockfiles, DB/auth spike, README and brief skeletons, CI/test skeleton. |
| Aug 26 14:00 | 20 h | Gate A data model, backend RBAC, revision/audit/concurrency tests green. |
| Aug 27 06:00 | 36 h | Gate B Top Card, timeline, source jump, comments, revert happy path usable. |
| Aug 27 16:00 | 46 h | Gate C redaction, AI fixture/provider boundary, accept/reject, materialized glance. |
| Aug 28 00:00 | 54 h | Bonus cutoff; self-learning/data decay kept only if core remains green. |
| Aug 28 06:00 | 60 h | Feature freeze. All mandatory automated tests green. |
| Aug 28 14:00 | 68 h | Video, 2–3 page brief, README, attribution, clean clone rehearsal complete. |
| Aug 28 16:30 | 70.5 h | Submission package ready, leaving a one-hour send buffer. |

The brief says a hint may arrive roughly 48 hours into the challenge. Check once near Aug 27 18:00; only change course if it affects a scored acceptance criterion.

## 11. Decisions that can wait, and real blockers

These do not block the local scaffold:

- Hosted PostgreSQL provider and connection string.
- External LLM provider and API key.
- Final deployment host and public/private repository choice.

## Phase 7 local feature-freeze record

The local prototype now includes bilingual application chrome and a closed-by-default bilingual
Learning Guide, a safe Windows one-click launcher, clinic-scoped stable-ID mentions, internal
assignments/tasks with materialized open actions, metadata-only DB-backed SSE invalidation, and a
low-risk accessibility pass. These additions do not translate clinical source text, add a live LLM,
change RBAC/provenance, or implement CRDT/OT.

The Phase 7.1 application checkpoint is `30a90bf`. Final local evidence is 51 backend tests,
88% reproducible coverage, 17 Vitest tests, 12 Playwright tests, and a real-TCP warm-path P95 of
67.823 ms on the SQLite approximation. Hosted PostgreSQL, TLS/encryption-at-rest, production
retention/deletion policy, human UX-01 sign-off, final video, GitHub upload, and email remain
outside the local implementation boundary.
- Candidate name in the submission subject.

They must be resolved before the relevant phase. Never paste secrets into chat or commit them; use local environment files and an `.env.example` with placeholders.
