# Round 9 local iteration demo QA

Date: 2026-09-03

Status: **local synthetic recording generated and browser-validated.**

## Reproducible path

- Recording script: [`record_round9_demo.mjs`](../../scripts/record_round9_demo.mjs)
- Environment: disposable migrated SQLite at Alembic head, local Uvicorn and Vite only
- Provider mode: deterministic fixture; no live DeepSeek call
- Rehearsal: `REHEARSAL PASSED - local synthetic selectors verified`
- Recording output (local-only): `deliverables/iteration/Nightingale_Real_Clinic_Iteration_Demo.webm`

The recording path used only local synthetic accounts and opened the Glance, immutable source,
conflict review, patient publication review, explicit provider-failure, prerecorded Voice, and
Patient privacy states. It did not write to Render or use the original user-supplied MP4.

## Media checks

| Check | Result |
| --- | --- |
| File size | 4,770,193 bytes |
| SHA-256 | `20F581728DA5BD94A58E93F6EFDEF29FB571BA81D2222362542235ADD8F2F021` |
| Container metadata | Chromium `loadedmetadata` succeeded; duration 54.76 s, 1280×720, `readyState=4` |
| Decode/seek | Chromium seeked successfully at 6, 10, 17, 25, 30, 39, 43, and 53.26 seconds |
| Visual samples | Each sampled frame was rendered and inspected: Glance, conflict, publication, provider failure, Voice transcript/source, and Patient projection are visible |
| `ffprobe` / `ffmpeg` | Not installed in this Windows environment; no ffprobe/full-decode claim is made |

The new WebM is local-only and ignored by Git so it cannot be uploaded accidentally. The original
MP4 remained outside Git and was not opened, transformed, renamed, moved, or uploaded during this
round. This QA makes no claim about audio quality; the recording uses visible English captions.
