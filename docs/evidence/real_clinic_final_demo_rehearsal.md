# Real Clinic Final Demo Rehearsal Evidence

Date: 2026-09-03
URL: `https://nightingale-shared-care-note.onrender.com`
Mode: browser UI observation only; no credentials, cookies, storage, API keys, dashboard values,
or database access used.
Overall result: **PASS WITH RECORDING CONDITIONS**

This is a pre-shoot desk rehearsal, not the final video QA and not a claim that every role was
re-run on the exact closure commit. The existing Round 9 WebM and original MP4 were not opened.
No persistent application write was performed during this rehearsal; only UI expansion, drawer
open/close, and a short native audio playback were used.

## Staff direct UI observations

| Area | Observed result | Evidence type | Recording decision |
| --- | --- | --- | --- |
| Identity/start | `Staff A`, `Staff view`, `Sarah Tan`, `Record status: Up to date`, `English` visible | Direct UI | Recordable after closing drawers |
| Glance | Six items visible; `Conflicting allergy information` is first | Direct UI | Core recording path |
| Ranking explanation | `Why is this here?` shows `Protected attention` and protected-first explanation; priority is distinguished from medical risk | Direct UI | Core recording path |
| Conflict | `Review conflict` opens `Allergy conflict review`; Staff read-only boundary is visible | Direct UI | Core recording path |
| Dual sources | `View source: Allergy reported` and `View source: Allergy denied` both open their immutable source panels | Direct UI | Core recording path |
| History | First Timeline entry `History` opens a History region with current version; no fixed version number assumed | Direct UI | Conditional; use actual earlier row if available |
| Comments | `Comments` opens a contextual drawer with `Team discussion` and `Comment body` | Direct UI | Optional short insert; do not add comment |
| Tasks | `Assign task` opens `Tasks`; current drawer contains multiple rehearsal-labelled test items | Direct UI | Do not show contents; use evidence branch or skip |
| Voice | `Voice note`, native audio, `Length: 24.0s`, `About this example`, and prerecorded/prepared-transcript disclosure visible; playback control worked | Direct UI | Show boundary only; do not create result |
| Historical context | `Historical summary · not the original record` and two `View original record` buttons visible | Direct UI | Use only if direct target navigation is visually confirmed |
| Historical source click | One `View original record` click was not represented as a new Source panel in the AX-only observation window | Direct UI limitation | Do not claim it opens an exact-span panel; prefer direct timeline/source path |

## Timing and selector observations

- `History` opened after the first click and needed a short loading wait before its region was visible.
- The first `Assign task` click did not expose the drawer immediately; a second Timeline entry opened it after a bounded wait.
- This is not treated as a product blocker because the final recording does not require task creation or task-state mutation.
- The final Master therefore includes waits, a no-write fallback, and a rule to hide rehearsal-labelled task data.

## Role recheck boundary

- Clinician was not re-authenticated in this session. `History`/`Compare`/adjudication controls are
  supported by existing Playwright and backend evidence, but the Master marks the exact current
  take `REVERIFY AFTER MANUAL LOGIN BEFORE RECORDING`.
- Patient was not re-authenticated in this session. Patient privacy projection is supported by
  existing tests/evidence, but the Master marks the exact current take for manual recheck.
- No old screenshot, old commit, or remembered version number is used as a substitute for those
  manual checks.

## No-write and safety confirmation

- No comment was added.
- No task was created or changed.
- No revision was saved.
- No Accept/Reject, adjudication, approval, publish, pin, or unpin action was performed.
- No password, cookie, token, API key, environment value, raw log, or source UUID was recorded.

## Rehearsal conclusion

The protected ranking, conflict/provenance, Staff boundary, publication Draft entry point,
Comments entry point, Task drawer existence, and Voice fixture boundary are sufficiently mapped
for a controlled recording. The final take remains conditional on clean synthetic state, manual
Clinician/Patient login checks, and the post-recording video QA checklist. This evidence does not
close UX-01 as an independent study and does not claim hosted authenticated benchmark latency.
