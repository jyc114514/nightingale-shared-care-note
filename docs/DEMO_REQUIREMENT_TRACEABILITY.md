# Nightingale demo requirement traceability

Rehearsal date: 2026-08-27
Deployed URL: `https://nightingale-shared-care-note.onrender.com`
Observed deployed commit: `e766fe9`
UI language used for the rehearsal: English

This document maps the candidate brief to what can be shown in a short demo. It separates
authenticated production rehearsal from local automated evidence. It does not turn a demo
observation into a claim of clinical validation.

## Evidence legend

- **Online verified**: the action was performed against the deployed HTTPS service and the
  visible result was recorded in `docs/evidence/demo_rehearsal.md`.
- **Local evidence**: the behavior is covered by repository tests or documentation, but was not
  performed as a browser action in this rehearsal.
- **Replaced**: the exact brief step was not available in the deployed UI, so the script uses a
  narrower, reproducible path and says so.
- **Not claimed**: the capability is intentionally outside this prototype's honest scope.

## Requirement-to-demo map

| `requirements.txt` lines | Brief requirement | Demo surface and observed evidence | Recording status |
| --- | --- | --- | --- |
| 3-4 | Fragmented notes become a shared, real-time longitudinal workspace | English workspace for Sarah Tan; internal sessions showed `Live updates: Connected`. A second-browser realtime demo was not reproducible in this session. | Online verified for workspace/SSE status; realtime multi-browser step removed |
| 8-9 | Glance View with content, open actions, flags, and rapid readability | Staff-first `Top Card` / `What needs attention now` showed six-or-fewer cards. Cards displayed content, status, item kind, action label/state, risk label, source, and the ranking disclaimer. An independent Simplified Chinese participant completed the defined glance task in approximately nine seconds without coaching. | Online and independent UX evidence verified |
| 10-13 | Continuous timeline and entry metadata | Timeline showed multiple dates, manual notes, AI-scribed entries, patient entries, timestamps, author and owner labels, versions, and source-linked entries. | Online verified |
| 15 | Threaded collaboration with resolve/unresolve; optional mentions and assignments | Staff Comments drawer accepted a synthetic root comment, showed `@Clinician A · clinician` autocomplete and mention metadata, and toggled `Resolve` → `Unresolve`. The existing task drawer opened with the source entry and assignee context. | Online verified for comment/mention/toggle/drawer; task creation and reply omitted from the short script |
| 17-19 | Full revision snapshots, compare, and revert | Clinician section was edited, History opened, `Compare` showed `Diff v1 → v2` with Before/After, and `Revert` created v3 while retaining v1 and v2. | Online verified |
| 21-26 | Three distinct system-authored AI-scribed entry types and provenance | Doctor, nurse, and patient-session types were visible in the internal UI. Voice processing created a system-authored suggestion with a `voice_session:` source reference and immutable source span. | Online verified for visible types and Voice source; live LLM not claimed |
| 28-31 | Importance logic and fast clinician review | Staff `Pin` → `Unpin` was exercised as feedback. Local bonus tests cover priority adaptation; the browser demo does not claim that one click proves learning. | Online verified for feedback control; local evidence for learning |
| 32 | Hybrid storage / data decay | Historical context showed Hot context, Warm index, and a derived cold summary with source pointers. | Online verified for representation; no production compression claim |
| 34-40 | Server-side role permissions and clinic scope | Clinical/Staff sessions showed internal resources. Patient session showed only patient-facing entries, no Top Card, comments, tasks, or history controls. Local direct API tests remain the enforcement evidence. | Online privacy projection plus local server-side evidence |
| 42-44 | Provenance and conflict trust | Glance `Open source` jumped to the correct nurse entry, immutable v1, and exact `<mark>` quote. The UI labels AI items as suggested or review-required; conflict handling is covered by local API tests. | Online verified for provenance; local evidence for conflict resolution |
| 45-48 | Ambient consult capture | The deployed Level-C path exposed prerecorded synthetic WAV fixtures, mock timestamped transcripts, segment seeking, suggested output, and source navigation. No microphone, upload, ASR inference, diarization, or production audio was shown. | Online verified as Level C only |
| 51 | RBAC implementation constraints | Role-specific browser projections matched the server response. Clinician editing was limited to the Clinician section; Staff editing was limited to the Staff note. | Online smoke plus local authorization tests |
| 52 | Warm Glance P95 ≤ 300 ms | The measured warm-path benchmark remains in `docs/evidence/gate_c_warm_path.md`; the video does not invent a new performance number. | Local benchmark evidence |
| 53 | Synthetic-only data, redaction boundary, TLS, encryption at rest | The app disclosed synthetic-only use. HTTPS and Render PostgreSQL evidence are documented separately; no credential or config screen is part of the recording. | Online deployment/security evidence; no live external LLM claim |
| 56-72 | Required micro-tests and bonus test | The required backend test files and `test_self_learning_importance.py` remain the executable evidence. | Local evidence |
| 74-85 | Repository, brief, attribution, and demo deliverables | Repository/docs/PDF/attribution already exist; this phase refreshes the final video-planning/operator documents. No final video is recorded here. | Documentation prepared; final video remains pending |
| 87-89 | Scenario A: Glance and AI Scribe | Staff opens the Top Card → nurse AI card → `Open source` → exact immutable timeline span. | Online verified |
| 90-93 | Scenario B: collaboration and audit trail | Exact “new note” and manual text-highlighting controls were not present. The script replaces them with Staff existing-note edit, comment mention/toggle, and Clinician history/diff/revert, all actually performed. | Replaced and documented honestly |
| 94-97 | Scenario C: longitudinal context and bonus decay | April 2025 source entries, February 2026 AI entry, current entries, derived summary, and original-record navigation were shown. Pin feedback was exercised. | Online verified for visible path; data-decay explanation only |
| 99-104 | Scoring dimensions | The script foregrounds glanceability, collaboration, provenance, privacy, and trade-offs. | Coverage mapped; no score claimed |

## Independent UX-01 evidence

The independent result is recorded in [ux_01_independent_test.md](evidence/ux_01_independent_test.md):
anonymous independent participant, Simplified Chinese locale, approximately nine seconds, no
coaching, and all four defined glance answers correct. Role and viewport were not separately
recorded. The candidate brief does not require English for this task; automated desktop/mobile
checks remain separate responsive evidence.

## Deliberately removed from the recording path

The following are not presented as successful demo clicks because the deployed rehearsal did not
provide reliable evidence for them:

- two-browser SSE propagation and the browser conflict panel;
- a new-note composer (no such control was visible);
- manual phrase-selection/highlight creation (only existing generated highlights were available);
- task creation/completion and a threaded reply in the short recording;
- live DeepSeek calls, microphone capture, upload, Whisper inference, diarization, and model
  quality.

These boundaries preserve the distinction between what the prototype implements locally and what
the final video can honestly demonstrate from the deployed UI.
