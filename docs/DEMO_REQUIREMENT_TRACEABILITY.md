# Nightingale demo requirement traceability

录制时以 [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) 为唯一操作主文件；本文件只负责 requirement 对照和证据边界。

Rehearsal date: 2026-08-27
Deployed URL: `https://nightingale-shared-care-note.onrender.com`
Final observed deployed commit: `42a01b6`
Historical rehearsal commit: `e766fe9`
UI language used for the rehearsal: English

This document maps the candidate brief to what can be shown in a short demo. It separates
authenticated production rehearsal from local automated evidence. It does not turn a demo
observation into a claim of clinical validation.

The original `e766fe9` rehearsal and its screenshots remain historical evidence. The final
release-candidate UI was pushed as `42a01b6` and verified on the same HTTPS service; the final
online addendum below supersedes only the old pending-deployment wording.

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
| 3-4 | Fragmented notes become a shared, real-time longitudinal workspace | English workspace for Sarah Tan; the current product label is `Record status: Up to date`. A second-browser realtime demo was not reproducible in this session. | Online verified for workspace/SSE status; realtime multi-browser step removed |
| 8-9 | Glance View with content, open actions, flags, and rapid readability | Staff-first `Glance View` showed six-or-fewer cards. Cards displayed content, `Next step`, status, item kind, risk label, source, and priority disclaimer. An independent Simplified Chinese participant completed the defined glance task in approximately nine seconds without coaching. | Online and independent UX evidence verified |
| 10-13 | Continuous timeline and entry metadata | Timeline showed multiple dates, care notes, patient entries, timestamps, author and owner labels, versions, and source-linked entries. | Online verified |
| 15 | Threaded collaboration with resolve/unresolve; optional mentions and assignments | The final recording plan creates one synthetic task from the visible comment using `Assign task`, `Task title`, `Assign to`, and `Create task`, then shows its `Open` card. The earlier rehearsal only verified the drawer; the new task creation is not claimed as completed online. | Planned recording action; historical online evidence remains comment/mention/toggle/drawer only |
| 17-19 | Full revision snapshots, compare, and revert | Clinician plan was edited, History opened, `Compare` showed `Diff v1 → v2` with Before/After, and `Revert` created v3 while retaining v1 and v2. | Online verified |
| 21-26 | Three distinct system-authored AI-scribed entry types and provenance | Doctor, nurse, and patient-conversation types were visible in the internal UI. Voice processing created a system-authored suggestion with a reviewable source link and original-record excerpt. | Online verified for visible types and Voice source; live LLM not claimed |
| 28-31 | Importance logic and fast clinician review | Staff `Pin` → `Unpin` was exercised as feedback. Local bonus tests cover priority adaptation; the browser demo does not claim that one click proves learning. | Online verified for feedback control; local evidence for learning |
| 32 | Hybrid storage / data decay | Historical context showed Recent context, Earlier context, and a historical summary with original-record pointers. | Online verified for representation; no production compression claim |
| 34-40 | Server-side role permissions and clinic scope | Clinical/Staff sessions showed internal resources. Patient session showed only patient-facing entries, no Glance, team discussions, tasks, or history controls. Local direct API tests remain the enforcement evidence. | Online privacy projection plus local server-side evidence |
| 42-44 | Provenance and conflict trust | Glance `Open source` jumped to the correct nurse entry, saved version, and exact highlighted quote. The UI keeps AI items reviewable; conflict handling is covered by local API tests. | Online verified for provenance; local evidence for conflict resolution |
| 45-48 | Ambient consult capture | The deployed Voice path exposed prerecorded synthetic audio, prepared timestamped transcript segments, reviewable output, and source navigation. The recording does not present this as live model or capture quality evidence. | Online verified for the supported evaluation path |
| 51 | RBAC implementation constraints | Role-specific browser projections matched the server response. Clinician editing was limited to the Clinician plan; Staff editing was limited to the Staff note. Accept/Reject remains Clinician-only. | Online smoke plus local authorization tests |
| 52 | Warm Glance P95 ≤ 300 ms | The measured warm-path benchmark remains in `docs/evidence/gate_c_warm_path.md`; the video does not invent a new performance number. | Local benchmark evidence |
| 53 | Synthetic-only data, redaction boundary, TLS, encryption at rest | The app disclosed synthetic-only use. HTTPS and Render PostgreSQL evidence are documented separately; no credential or config screen is part of the recording. | Online deployment/security evidence; no live external LLM claim |
| 56-72 | Required micro-tests and bonus test | The required backend test files and `test_self_learning_importance.py` remain the executable evidence. | Local evidence |
| 74-85 | Repository, brief, attribution, and demo deliverables | Repository/docs/PDF/attribution already exist; this phase refreshes the final video-planning/operator documents. No final video is recorded here. | Documentation prepared; final video remains pending |
| 87-89 | Scenario A: Glance and AI Scribe | Staff opens Glance View → nurse AI card → `Open source` → saved-version timeline excerpt. | Online verified in the rehearsal; current product-language labels are covered locally |
| 90-93 | Scenario B: collaboration and audit trail | The final plan uses Staff existing-note edit, comment mention/toggle, one assigned task, Clinician task progress, and Clinician AI review. The missing new-note/manual-highlight controls remain replaced and are not claimed. | Recording plan; only earlier comment/mention/toggle and revision evidence was previously performed |
| 94-97 | Scenario C: longitudinal context and bonus decay | April 2025 source entries, February 2026 AI entry, current entries, derived summary, and original-record navigation were shown. Pin feedback was exercised. | Online verified for visible path; data-decay explanation only |
| 99-104 | Scoring dimensions | The script foregrounds glanceability, collaboration, provenance, privacy, and trade-offs. | Coverage mapped; no score claimed |

## Final task lifecycle and AI review update - 2026-08-28

The recording materials now distinguish two independent state machines:

- Assignment is optional collaboration: Staff creates one task titled Review synthetic follow-up plan
  for Clinician A; it is active immediately and moves Open → In progress → Done.
- AI highlight review is a mandatory Clinician path: Accept one actual reviewable suggestion and
  wait for Reviewed; Reject another and wait for it to leave active Glance. Neither action rewrites
  or deletes the original source.

This is a recording plan, not new online rehearsal evidence. No task creation, task transition,
Accept, or Reject was executed while updating these documents. The historical browser evidence in
docs/evidence/demo_rehearsal.md remains unchanged.

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

## Final release-candidate online addendum - 2026-08-27

The final online pass used the Live `42a01b6` deployment `dep-da84vcp5efls73dm07vg` and manual
English Staff, Clinician, and Patient sessions. It confirmed the product-language labels used by
the recording materials: `Record status: Up to date`, `Glance View`, `Voice note`, `Ready for
review`, `Original source`, `Team discussion`, `Current`, `Compare`, `Before`, `After`, `Patient
view`, and `Your care summary`.

The Staff Voice path produced one authorized synthetic suggestion, sought the second transcript
segment to `8.0s`, and opened the exact immutable source span. Clinician History/Compare and the
Glance source path passed without a write action. Patient projection showed two patient-facing
timeline records and patient Voice only; internal buttons and raw suggestion text were absent.
The final online evidence and screenshot paths are recorded in
[`docs/evidence/demo_rehearsal.md`](evidence/demo_rehearsal.md) and
[`docs/evidence/deployment_security.md`](evidence/deployment_security.md).

## Final candidate-brief audit - 2026-08-28

The complete line-by-line audit is recorded in
[`FINAL_REQUIREMENTS_AUDIT.md`](FINAL_REQUIREMENTS_AUDIT.md). It finds no failed or unproven
non-Voice Mandatory requirement. The deployed UI's unavailable new-note/manual-highlight steps
remain `recommended substep not shown`, not a Mandatory blocker. The final MP4 is user-supplied;
the user explicitly waived further content QA, so no Codex full-playback claim is made.
