# Deployed English demo rehearsal evidence

Date: 2026-08-27
Deployment: `https://nightingale-shared-care-note.onrender.com`
Observed commit: `e766fe9`
Result: **PASS WITH REPLACEMENTS**

This is an authenticated synthetic-data browser rehearsal, separate from the independent UX-01
participant evidence and not a final video. The browser used one claimed Chrome user tab with
sequential manual role logins. No credentials, browser storage, raw logs, or configuration screens
were captured.

## Executed checks

| # | Role / surface | Action | Observed result | Timing / status |
| ---: | --- | --- | --- | --- |
| 1 | Clinical / workspace | Re-authenticate, select English and Sarah Tan | Header showed `Clinician A`, `Clinician · cookie session`, and `Live updates: Connected`; Voice panel was present. | About 6 s after page load; pass |
| 2 | Clinical / Voice | Select `Synthetic nurse follow-up · clinical`, click the native play control, wait | Native player visibly advanced from about `0:10` to `0:13` of `0:24`; fixture disclosure stayed visible. | About 3.2 s playback wait; pass |
| 3 | Clinical / Voice | Click `Process sample` once | `Voice session status: completed`; three segments showed `0.0s-8.0s`, `8.0s-16.0s`, `16.0s-24.0s`; provider was `mock-transcript-fixture · precomputed-v1`; confidence was unavailable. | About 1.3 s; pass |
| 4 | Clinical / Voice | Click segment 1 | Audio current time became `8.0` seconds. | About 0.25 s; pass |
| 5 | Clinical / Voice source | Click `Open generated source` | Timeline showed the generated Nurse consult entry, `Immutable source span`, immutable v1, and a mark containing the exact fixture quote. Source panel showed Python code-point offsets and a `voice_session:` reference. | About 0.6 s; pass |
| 6 | Clinical / Comments | Click Staff note `Comments`, observe initial stale page, refresh once, click again, wait 5.2 s | After the one refresh fallback, `Staff note · Internal discussion` remained open with `No comments yet.` and an explicit `Close` control. | 0.8 s open + 5.2 s hold; pass with fallback |
| 7 | Clinical / Tasks | Click Staff note `Assign task` | Contextual drawer opened with `Creating a task for: Staff note v1`, source entry context, assignee choices, and existing task list. No task was created in this rehearsal. | About 0.5 s; pass |
| 8 | Patient / privacy and Voice | Log out, manually log in as Sarah Patient, select English and Sarah Tan | Header showed `Sarah Patient · Patient · cookie session`; only `Synthetic patient follow-up · patient` was listed. No Top Card, internal comments, tasks, history controls, or clinical sample appeared. | About 6 s page load; pass |
| 9 | Patient / Voice | Play the native control and wait, then click `Process sample` once | Native player showed about `0:13 / 0:24`; processing completed with three mock timestamped segments and confidence unavailable. No `Open generated source` control appeared. | About 3.2 s playback + 1.3 s process; pass |
| 10 | Staff / edit and mention | Log out, manually log in as Staff A; edit Staff note; save; open `Comments`; type a synthetic comment ending in `@clinician`; choose `@Clinician A · clinician`; click `Add comment` | Staff note became v2. The drawer showed the root comment and `Mentions: @Clinician A`. | Save about 1.2 s; comment about 1.2 s; pass |
| 11 | Staff / collaboration | Click `Resolve`, then `Unresolve`; click `Pin`, then `Unpin` | Resolve state toggled in the comment drawer. The Glance card pin state toggled as adaptive feedback. | About 0.9 s per server mutation; pass |
| 12 | Staff / Glance | Open the AI nurse card `Unresolved cardiology referral` with `Open source` | Source panel showed Nurse consult v1, exact mark `Unresolved cardiology referral`, and the timeline target. `Close source` removed the panel/span and removed `highlight` while retaining `patient`. | About 0.9 s; pass |
| 13 | Staff / history | Click the first historical `View original record` button | The page scrolled to the canonical April 2025 Patient summary timeline entry. This control did not open the immutable source side panel. | About 0.8 s; pass with wording correction |
| 14 | Clinician / revision | Log out, manually log in as Clinician A; edit Clinician section; save; open `History`; click `Compare` for v1 | The panel showed `Diff v1 → v2`, Before and After text, and both version rows. | Save about 1.2 s; compare about 0.8 s; pass |
| 15 | Clinician / revert and review | Click `Revert` for v1; then review the available AI suggestion with `Accept` | Revert created v3, restored the original plan, and retained v1/v2. The accepted nurse suggestion no longer displayed Accept/Reject. | Revert about 1.3 s; pass |
| 16 | Render dashboard / logs | Inspect existing Deploys and Logs surfaces without opening Environment | Deploys showed `Live` and last successfully deployed commit `e766fe9`. Log content was classified without printing it: no raw Voice transcript, secret-like value, DeepSeek, or Whisper claim was found. | About 3 s dashboard load; pass |

## Probe limitations and replacements

- The browser extension blocked a direct navigation to `/health`, and the local Windows TLS
  clients could not perform a second direct HTTPS probe. Existing Render Logs/Deploys evidence
  showed successful health checks, and the authenticated app loaded from the Live service. The
  video therefore does not include a health-command shot.
- The first loaded Clinical page showed a partial stale state (`Authentication required`, no
  Voice panel, and reconnecting SSE). A clean logout/login followed by a wait produced
  `Connected` and the complete Voice panel. The recording setup uses that fallback.
- The exact brief step “Staff adds a new note” was removed because no new-note control appeared.
  The video says “edit the existing Staff note.”
- No manual text-selection/highlight control appeared. The video opens an existing AI-generated
  highlight and never claims manual highlight creation.
- A second-browser SSE propagation and live 409 conflict panel were not reproducible in this
  single-tab rehearsal. They remain local backend/test evidence and are removed from the spoken
  click path.
- Assignment drawer opening was verified, but task creation/completion was omitted to avoid an
  additional persistent mutation. Thread reply was also omitted from the short script.

## State mutations recorded

The rehearsal used synthetic data only. It created two Voice-derived entries, a Staff note
revision, one internal mention comment with a resolve/unresolve cycle, one pin/unpin feedback
cycle, a Clinician plan edit followed by a revert-created version, and one accepted AI suggestion.
The live database is therefore not a pristine seed after this rehearsal. This document records
that fact so a future recording does not silently assume baseline version numbers.

## Final reordered dry run

The revised order was run after the read-only state inventory: **Staff → Clinician → Patient**.
Role changes were two off-camera logout/login cuts. No Voice sample was reprocessed and no new
database mutation was created during this final dry run.

| Order | Role / target | Actual action and visible result | Time | Mutation / recording decision |
| ---: | --- | --- | ---: | --- |
| 1 | Staff A · Sarah Tan | `Top Card` showed action/ranking; `Open source` on the still-Suggested nurse card showed the exact mark and immutable source; `Close source` removed the panel; existing `Comments` drawer showed the `@Clinician A` metadata; Voice panel showed the clinical fixture disclosure. | ~7.4 s including waits | No mutation; repeatable. If Comments is stale, refresh once and repeat. |
| 2 | Clinician A · Sarah Tan | `Clinician section` → `History`; two earlier `Compare` buttons were available; one Compare showed Before/After; two `Revert` controls were available but deliberately not clicked. `View original record` scrolled to the April 2025 Patient summary. | ~6.7 s | No mutation; repeatable. Select an available earlier version immediately before recording. |
| 3 | Sarah Patient · Sarah Tan | `Patient view` and `Internal Glance View is hidden` were visible; only patient Voice sample was listed; no Top Card, internal controls, Clinical sample, or source result appeared. | ~61 ms DOM state check | No mutation; repeatable. Do not process Voice again if the result is already recorded. |

The current state inventory before this dry run recorded Staff note v3, Clinician section v3, two
remaining Suggested cards, one Conflict review card, existing `@Clinician A` comment metadata,
two Voice-derived timeline entries, and two historical original-record buttons. The final dry run
used those existing states rather than assuming a pristine seed.

## Video conclusion

The planned short demo is reproducible with the documented fallbacks and covers the strongest
deployed path. UX-01 is closed by the separate independent participant result; this browser
rehearsal is not presented as a second participant study. It also does not claim full ambient Voice,
ASR, diarization, clinical validation, or a final recorded video.

## Final release-candidate online verification - 2026-08-27

This addendum records the final online pass after the existing Render service deployed `42a01b6`
as `dep-da84vcp5efls73dm07vg`. It supersedes only the older “pending login” statements; earlier
rehearsal results remain historical. The user manually authenticated each session, and no password,
cookie, environment value, database URL, API key, or raw log content was read or recorded.

| Role | Verified online result | Mutation boundary |
| --- | --- | --- |
| Staff A | `Staff view` and `Record status: Up to date`; Glance, Source, Comments, Task, and History opened. One user-authorized `Create care-note suggestion` action produced `Ready for review`; the 24-second audio loaded, transcript segment 2 sought to exactly `8.0s`, and `View source` showed the exact highlighted immutable source span. | One new synthetic Voice suggestion only; no note/comment/task/review mutation in this final pass. |
| Clinician A | `Clinician view`; 24-second Voice audio metadata loaded. Clinician plan History showed `Current`, `Compare`, and `Revert`; Compare showed Before/After. The Glance source for `Unresolved cardiology referral` opened with the matching mark. | Read-only; no Edit, Save, Revert, Accept, or Reject. |
| Sarah Patient | `Patient view`, `Your care summary`, two patient-facing timeline records, and only `patient follow-up` Voice. Patient audio metadata loaded at 24 seconds with no media error. | Read-only; no processing, source navigation, or internal-control attempt. |

The Patient DOM contained zero buttons named `Comments`, `History`, `Assign task`, `Edit`, `Accept`,
`Reject`, `View source`, or `Open source`; it also contained no internal Glance, raw suggestion, or
team discussion text. The final normal English Staff DOM scan found zero occurrences of the recorded
developer/provider terms listed in [`ui_product_language_audit.md`](ui_product_language_audit.md).

Final online screenshots:

- [Staff Voice result](../../artifacts/gate-b/online-voice-result.png)
- [Staff Voice source](../../artifacts/gate-b/online-voice-source.png)
- [Clinician workspace](../../artifacts/gate-b/online-clinician.png)
- [Patient privacy projection](../../artifacts/gate-b/online-patient.png)

This pass confirms the deployed synthetic demo path and the server-side Patient projection. It does
not claim a final recorded video, live ASR/DeepSeek, diarization, microphone support, clinical
validation, or a pristine database; the one authorized Voice creation is recorded as synthetic
rehearsal state.
