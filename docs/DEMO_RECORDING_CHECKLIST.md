# Nightingale demo recording checklist

## Before recording

- [ ] Use the deployed HTTPS URL and select `English`.
- [ ] Use synthetic roles only: Clinician A, Staff A, and Sarah Patient.
- [ ] Select Sarah Tan and confirm the expected role label.
- [ ] Confirm `Live updates: Connected` for internal sessions.
- [ ] Prepare the browser window at a readable desktop size; do not show browser password
      managers, developer tools, environment pages, or address-bar credentials.
- [ ] Decide whether to record from the current rehearsal database or an isolated seeded copy.
      If using the current deployment, note that revisions and Voice entries already exist.
- [ ] Test microphone and system-audio settings without opening the application's microphone or
      upload controls. The product demo uses a prerecorded WAV only.

## During recording

- [ ] Keep the UI in English and narration in English.
- [ ] Do not type or show a password, API key, database URL, or real patient data.
- [ ] Start with the Top Card and show content, action, status, item kind, risk, and ranking
      disclaimer.
- [ ] For provenance, show `Open source`, the immutable version, code-point offsets, exact mark,
      and `Close source` query cleanup.
- [ ] For Voice, process each fixture at most once; show the mock transcript disclosure,
      timestamps, confidence unavailable, and no microphone/upload claim.
- [ ] For Staff, say that the existing-note edit replaces the unavailable new-note composer.
- [ ] For comments, show the mention suggestion and metadata; show Resolve and Unresolve.
- [ ] For Clinician history, show Compare Before/After and Revert as a new version.
- [ ] For historical context, call `View original record` timeline navigation, not an exact-span
      provenance panel.
- [ ] For Patient, show the server-side projection and absence of internal controls and clinical
      Voice sample.
- [ ] Use pauses and cuts for waits; never narrate a failure as success.

## After recording

- [ ] End on the English synthetic workspace, not a credential or configuration screen.
- [ ] Sign out if the browser is shared.
- [ ] Confirm the final file duration is no more than five minutes and narration is approximately
      105-120 words per minute.
- [ ] Watch the complete file once for unreadable text, clipped captions, cursor obstruction,
      accidental secrets, and unsupported claims.
- [ ] Check that the spoken disclaimer says the Voice path is prerecorded synthetic audio with a
      mock timestamped transcript and does not claim live ASR or diarization.
- [ ] Keep UX-01 marked pending until an unfamiliar participant completes an independent test.
- [ ] Re-run a secret/package scan before any final packaging. This task does not regenerate a
      PDF, ZIP, or manifest.
