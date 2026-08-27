# Nightingale final demo shot list

Target runtime: 4:20 · English UI · synthetic data only.
The filenames below are recording targets, not files created by this phase. No final video or new
screenshots are claimed.

| Shot | Time | Role / profile | Visible action | Rehearsed result | Capture target |
| ---: | --- | --- | --- | --- | --- |
| 1 | 00:00-00:30 | Clinician A / existing Chrome tab | Confirm `English`, `Sarah Tan`, `Live updates: Connected` | Shared Care Note, Clinician view and trust boundary visible | `01-opening.mp4` |
| 2 | 00:30-01:08 | Clinician A / internal | Read `Top Card`; click `Open source` on `Unresolved cardiology referral` | Six-or-fewer card view; action/status/risk/ranking; immutable v1 source and exact mark | `02-glance-provenance.mp4` |
| 3 | 01:08-01:45 | Clinician A / internal | Play clinical WAV; `Process sample` once; click 8-second segment; open generated source | 24-second fixture, mock transcript, three timestamps, confidence unavailable, exact source | `03-voice-level-c.mp4` |
| 4 | 01:45-02:25 | Staff A / sequential session | `Staff note` → `Edit` → `Save revision`; `Comments`; `@clinician`; choose `@Clinician A · clinician`; `Add comment` | Staff revision and root comment with mention metadata | `04-staff-mention.mp4` |
| 5 | 02:25-03:05 | Staff A then Clinician A | `Resolve` → `Unresolve`; `Pin` → `Unpin`; Clinician `History` → `Compare` → `Revert`; optional `Accept` | Collaboration toggle, feedback toggle, Before/After, new revert version, retained history | `05-review-history.mp4` |
| 6 | 03:05-03:32 | Clinician A / internal | Show Hot/Warm/derived cold; click `View original record` | Scrolls to April 2025 canonical Patient summary; no false exact-span claim | `06-longitudinal-context.mp4` |
| 7 | 03:32-04:00 | Sarah Patient / sequential session | Show `Internal Glance View is hidden`; show patient timeline and patient Voice sample | Internal controls and clinical sample absent; patient-safe fixture only | `07-patient-privacy.mp4` |
| 8 | 04:00-04:20 | Clinician or Staff / English | End on synthetic disclosure and HTTPS app | Honest boundary: PostgreSQL, fixture providers, optional redacted adapter, no live call | `08-honest-close.mp4` |

## Captured evidence versus narration

The browser rehearsal directly verified shots 1-7's core visible states, including the Voice and
patient flows. Render Deploys showed the existing service `Live` at `e766fe9`; the Render Logs
surface was inspected without reproducing raw log lines. The recording should not show the
dashboard unless the presenter wants a short security boundary cut.

## Do not capture

Do not capture password entry, API keys, database URLs, environment values, browser storage,
provider consoles, raw Render log output, microphone permissions, file upload dialogs, live
DeepSeek calls, or any real patient information. Do not add shots for a new-note composer, manual
highlight selection, second-browser SSE, live 409 conflict, task completion, or Whisper/diarization
claims; those steps were removed or replaced after rehearsal.
