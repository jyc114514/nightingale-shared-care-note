# Nightingale deployed demo session setup

## Target

Use the existing Render deployment:

- URL: `https://nightingale-shared-care-note.onrender.com`
- UI: English
- Database: the existing synthetic Render PostgreSQL service
- Voice mode: Level-C fixture only
- LLM mode: deterministic fixture only

The recording must not show credentials, environment variables, provider keys, database URLs,
browser storage, or configuration screens.

## Browser and role plan

The rehearsal used one existing Chrome user tab with sequential sessions. A separate browser
context was not available without risking the active cookie, so each role was ended with the
visible `Sign out` button before the next role was entered. Password entry was manual and off
camera.

| Session | Role | Patient | Planned use |
| --- | --- | --- | --- |
| 1 | Clinician A | Sarah Tan | Top Card, source, Voice clinical path, plan review, diff/revert, accept |
| 2 | Staff A | Sarah Tan | Staff note edit, internal comment, `@Clinician`, resolve/unresolve, pin feedback |
| 3 | Clinician A | Sarah Tan | Clinician plan edit, History, Compare, Revert; optional source review |
| 4 | Sarah Patient | Sarah Tan | Patient Voice fixture and privacy projection |

For a short recording, sessions can be prepared before recording and joined with cuts. Never show
the password field while it contains input. If a role is not available, remove that role's shot;
do not narrate an unverified result.

## Start checklist

1. Open the deployed root and select `English`.
2. Sign in to the intended synthetic role off camera.
3. Select `Sarah Tan` in `Select patient` if it is not already selected.
4. For Staff/Clinician, wait for `Live updates: Connected` and `Top Card` / `What needs
   attention now`.
5. For Patient, verify `Patient view` and `Internal Glance View is hidden`.
6. Use only the visible synthetic records and built-in WAV fixtures.
7. Do not click `Process sample` more than once per sample during one rehearsal.

## Controls used in the rehearsal

| Area | Exact visible control | Maximum wait | Expected visible result |
| --- | --- | ---: | --- |
| Top Card | `Open source` | 2 s | `Immutable source` panel and exact timeline mark |
| Source | `Close source` | 1 s | Panel/span removed; `patient` remains in URL |
| Comments | `Comments` | 2 s | Contextual drawer and `Comment body` |
| Comments | `Add comment` | 3 s | Root comment and mention metadata |
| Comments | `Resolve` / `Unresolve` | 3 s each | Action label toggles |
| Timeline | `Edit` → `Save revision` | 4 s | New version and saved text |
| History | `History` → `Compare` | 3 s | `Diff v1 → v2` Before/After |
| History | `Revert` | 4 s | New version restores prior content; history remains |
| Voice | `Process sample` | 10 s | `Voice session status: completed` |
| Voice | Transcript segment | 2 s | Audio current time seeks to the segment start |

## Rehearsal-state warning

The authenticated rehearsal intentionally used synthetic mutations and therefore changed the
existing evaluation database. It created Voice-derived entries, changed the Staff note to a new
revision, created one internal mention comment, created a Clinician plan revision and revert,
accepted one AI suggestion, and toggled one pin. The current database is not a pristine seed.

For a clean-looking final recording, use an isolated seeded copy or a documented reset procedure
outside this task. Do not claim that the live database is pristine, and do not reset production
data speculatively. If recording from the current deployment, narrate version numbers as observed
and keep the mutation/reset note in the video log.

## Safe Voice boundary

Show only:

- `Prerecorded synthetic audio only`;
- `Mock transcript fixture`;
- fixture timestamps;
- `ASR confidence unavailable for fixture`;
- the generated source link for the clinical role.

Do not show or claim microphone capture, upload, live ASR, Whisper inference, diarization, speaker
separation, live DeepSeek, or production PHI audio.
