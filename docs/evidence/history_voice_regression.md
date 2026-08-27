# Local History and Voice regression evidence

Date: 2026-08-27
Baseline: local `64d0f0b`
Scope: History current-row alignment and local authenticated Voice playback only

## History

The regression was the last current-version row in `HistoryPanel`. Older rows rendered an action
group while the current row rendered no corresponding content, so a flex row with
`justify-between` redistributed the free space. The date column therefore moved horizontally.

The fix gives every row the same responsive three-column grid:

1. version and role;
2. date and time;
3. Compare/Revert actions or a muted `Current`/`当前` label.

On narrow screens the grid becomes a vertical stack. The panel-level current-version pill was
removed because the current row now carries the local status label.

After screenshots:

- [English desktop History after three versions](../../artifacts/gate-b/desktop-1440-history-open-after-revert.png)
- [Chinese desktop History after multiple versions](../../artifacts/gate-b/desktop-1440-history-chinese.png)
- [Chinese mobile History](../../artifacts/gate-b/mobile-390-history-chinese.png)
- [English mobile History](../../artifacts/gate-b/mobile-390-history-open-after-revert.png)

## Voice playback

The local browser served the UI from port 5173 while the authenticated Voice API served the WAV
from port 8000. The previous `<audio>` element used the backend's relative `audio_url`, which made
the browser resolve it against the Vite origin. The UI now constructs the authorized route from
`patientId` and `sampleId`, fetches it with `credentials: include`, validates `audio/wav`, creates
a Blob object URL, and revokes that URL on sample switch or unmount.

The loader also aborts stale requests, rejects unexpected path segments, exposes only a normal
product error, and keeps the backend authorization route unchanged. Transcript seeking runs only
after audio metadata is ready.

Browser evidence:

- local response: `200`, `audio/wav`, API port `8000`;
- media element: Blob URL, metadata ready, positive duration;
- native play: `currentTime` advanced above zero;
- transcript segment starting at 8 seconds: playback position moved to at least 8 seconds;
- clinical and patient samples both passed; patient still received no source button;
- post-login console/media error checks passed.

Screenshots:

- [Clinical Voice ready](../../artifacts/gate-b/desktop-1440-voice-clinical.png)
- [Patient Voice](../../artifacts/gate-b/desktop-1440-voice-patient.png)
- [Mobile Clinical Voice ready](../../artifacts/gate-b/mobile-390-voice-clinical.png)
- [Mobile Patient Voice](../../artifacts/gate-b/mobile-390-voice-patient.png)

## Verification

- Vitest/API and App suites: `36 passed`.
- Core Gate B Playwright suite: `14 passed` across desktop and mobile.
- Voice Playwright suite: `4 passed` across desktop and mobile, including actual WAV response and
  playback progression.
- Frontend lint, Prettier, type-check, and production build: passed.
- Backend regression suite and quality checks: passed; no backend or database behavior changed.
- `requirements.txt` hash remains
  `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5`.
- Render, GitHub, PDF, ZIP, MANIFEST, providers, RBAC, and privacy configuration were not changed
  by this fix.
