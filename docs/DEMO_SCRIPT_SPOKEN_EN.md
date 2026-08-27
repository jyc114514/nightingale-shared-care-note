# Nightingale final spoken English demo script

Target runtime: **4:20**. Target speaking rate: **105-120 words per minute**.
Target UI: English. Target data: synthetic only.
This is a recording script based on the deployed rehearsal on 2026-08-27. It is not a claim of
independent UX-01 evidence, clinical validation, live ASR, or a final recorded video.

Password entry, role switching, loading waits, and any error recovery are off-camera cuts. Never
show a credential, key, environment screen, database URL, browser storage, or provider console.

## Shot 1 — Opening workspace

- **Time:** 00:00-00:30
- **Browser / profile / role:** Existing Chrome user tab; Clinician A; Sarah Tan selected.
- **Starting state:** Deployed root is open; English is selected; page has reached `Live updates:
  Connected`.
- **Exact action:** Confirm `English`; confirm `Select patient` is `Sarah Tan`; scroll to the
  workspace header.
- **Visible result expected and verified:** `Shared Care Note`, `Clinician view`, patient name,
  and the synthetic-only trust boundary are visible.
- **Maximum wait:** 6 seconds for the authenticated workspace. If the header says reconnecting,
  wait once for `Connected`; if it remains stale, refresh once before recording.
- **Mutation / reset note:** Read-only. No note or Voice mutation.
- **Requirements:** `requirements.txt:3-5, 8, 33-40`.
- **Say exactly:**

  > Nightingale is a shared care note for synthetic data. It is a trust system, not an autonomous
  > medical system. I use one patient workspace and keep the interface in English. The page
  > separates human notes, system suggestions, patient context, and review metadata.

## Shot 2 — Glance and exact provenance

- **Time:** 00:30-01:08
- **Browser / profile / role:** Same Chrome tab; Clinician A; internal view.
- **Starting state:** The `Top Card` region is visible with six or fewer items.
- **Exact action:** Read `What needs attention now`; point to a card's action/status/risk/source;
  click `Open source` on `Unresolved cardiology referral`; wait for the timeline target.
- **Visible result expected and verified:** The card shows `Action: Review referral · Open`,
  `P100`, `Suggested` or the current review state, and `Why ranked? Ranking priority, not a
  medical risk score.` The source panel shows `Immutable source`, `v1`, Python code-point offsets,
  and the timeline `<mark>` contains `Unresolved cardiology referral`.
- **Maximum wait:** 2 seconds for the source panel. If the card has already been reviewed, use
  another visible AI-scribed card with `Open source`; do not claim a missing review button.
- **Mutation / reset note:** Opening and closing source is view-only. `Close source` removes the
  source span and `highlight` query while retaining `patient`.
- **Requirements:** `requirements.txt:8-13, 25-26, 41-44, 87-89`.
- **Say exactly:**

  > The Top Card is designed for a fast glance. It has no more than six source-linked items. Each
  > card shows content, an action, a status, an item kind, and a risk label. The ranking note is
  > important: ranking priority is not a medical risk score. This nurse entry is an AI-scribed
  > suggestion. Open source takes me to the exact timeline entry. The source panel names immutable
  > version one, the source reference, and Python code-point offsets. The highlight is the stored
  > quote, not a rewritten sentence.

## Shot 3 — Level-C Voice fixture

- **Time:** 01:08-01:45
- **Browser / profile / role:** Same Chrome tab; Clinician A; internal Voice panel.
- **Starting state:** `Ambient Voice Prototype` is visible with `Synthetic nurse follow-up ·
  clinical` selected and no existing Voice result, or the result is prepared before recording.
- **Exact action:** Click the native audio play control; click `Process sample` once; wait for
  `Voice session status: completed`; click transcript segment `8.0s - 16.0s`; click `Open
  generated source` if the result is not already on screen.
- **Visible result expected and verified:** The player advances for several seconds; the panel
  shows `Mock transcript fixture`, three fixture timestamp ranges, `ASR confidence unavailable
  for fixture`, a system suggestion requiring review, and an immutable source with an exact mark.
  No microphone or upload control is visible.
- **Maximum wait:** 3 seconds for playback evidence; 10 seconds for processing; 2 seconds for
  segment seeking/source. If processing fails, show the explicit safe failure and remove the shot
  from the final video rather than calling it a success.
- **Mutation / reset note:** Processing one synthetic sample creates one recorded Voice session
  and source entry. Do not click `Process sample` twice.
- **Requirements:** `requirements.txt:21-26, 45-48, 53`.
- **Say exactly:**

  > This is a Level-C architecture and demo path. The audio is prerecorded synthetic signal data,
  > and the timestamps are fixture timestamps. The transcript is a mock fixture because local ASR
  > was unavailable in this environment, so confidence is unavailable. This optional prototype uses
  > prerecorded synthetic audio and a mock timestamped transcript. It demonstrates audio-to-summary
  > provenance, but it does not claim live ASR or diarization. The suggestion remains system-authored
  > and requires clinician review.

## Shot 4 — Staff collaboration and mention

- **Time:** 01:45-02:25
- **Browser / profile / role:** Same Chrome tab after an off-camera cut; Staff A; Sarah Tan.
- **Starting state:** Staff page shows `Staff view`, `Timeline`, and the existing `Staff note`.
- **Exact action:** Click `Edit`; replace the text with the synthetic rehearsal sentence; click
  `Save revision`; click `Comments`; type a comment ending in `@clinician`; choose
  `@Clinician A · clinician`; click `Add comment`.
- **Visible result expected and verified:** The Staff note shows a new version. The drawer shows
  the root comment and `Mentions: @Clinician A`. There is no new-note composer in the deployed UI.
- **Maximum wait:** 4 seconds for save; 2 seconds for the drawer; 3 seconds for the comment. If
  the drawer does not appear, refresh once and repeat the semantic `Comments` action. If the
  mention menu does not appear, leave the step out; do not type a hidden collaborator ID.
- **Mutation / reset note:** This creates a synthetic Staff revision and one internal comment.
  The brief's “add a new note” step is replaced by this existing-note edit because no create
  control was visible.
- **Requirements:** `requirements.txt:14-19, 37-40, 90-93`.
- **Say exactly:**

  > Now I switch to Staff. This deployed UI does not expose a new-note composer, so I use the
  > reproducible existing Staff note edit. The new revision is saved. I add an internal comment,
  > choose Clinician A from the mention menu, and submit it. The mention is stored as metadata, and
  > the discussion remains inside the clinic-scoped workspace.

## Shot 5 — Review, history, and feedback

- **Time:** 02:25-03:05
- **Browser / profile / role:** Staff A for the first cut; then Clinician A after an off-camera
  cut; same patient.
- **Starting state:** Staff comment drawer contains the synthetic root comment; Clinician page has
  the Clinician section and a suggested AI card.
- **Exact action:** In Comments click `Resolve`, then `Unresolve`. On the Glance card click `Pin`,
  then `Unpin`. In Clinician view click `Edit` on `Clinician section`, click `Save revision`,
  click `History`, click `Compare` for v1, then click `Revert` for v1. If a suggested card is
  available, click `Accept` once.
- **Visible result expected and verified:** Resolve state toggles and returns to unresolved. Pin
  state toggles. History shows `Diff v1 → v2` with Before/After; Revert creates v3, restores the
  original plan, and keeps v1 and v2. Accept removes the review buttons from the accepted item.
- **Maximum wait:** 3 seconds for each collaboration action; 4 seconds for save/revert. If the
  current rehearsal state already has the nurse suggestion accepted, use another visible
  Suggested/Conflict review card or omit the Accept cut.
- **Mutation / reset note:** These actions create synthetic audit/revision/review metadata. Do not
  reset versions by editing raw database state. The recording log must retain the observed version
  numbers.
- **Requirements:** `requirements.txt:15-19, 27-31, 41-44, 90-93`.
- **Say exactly:**

  > Resolve and Unresolve are explicit collaboration states. Pin and Unpin provide feedback to the
  > importance logic, but one click is not proof of learning. Clinician authority is limited to the
  > Clinician section. History keeps full snapshots. Compare shows the before and after. Revert
  > creates a new version and restores the prior content. It never erases history. A review action
  > accepts a suggestion without rewriting its source.

## Shot 6 — Longitudinal context

- **Time:** 03:05-03:32
- **Browser / profile / role:** Clinician A; same Chrome tab.
- **Starting state:** `Historical context` is visible with current and older entries.
- **Exact action:** Point to `Hot context`, `Warm index`, and `Derived summary · not the original
  record`; click the first `View original record`.
- **Visible result expected and verified:** The page scrolls to the April 2025 canonical Patient
  summary in the Timeline. The source panel does not open for this context pointer, so the video
  calls it original-record navigation rather than an exact-span provenance panel.
- **Maximum wait:** 2 seconds for the scroll. If the target is not visible, use the browser's
  normal scroll position after the click; do not invent a source panel.
- **Mutation / reset note:** View-only. No context refresh or data-decay mutation.
- **Requirements:** `requirements.txt:10-13, 32, 41-44, 94-97`.
- **Say exactly:**

  > Longitudinal context combines current entries with older history. The panel distinguishes Hot
  > context, the Warm index, and a derived cold summary. The summary is labeled not the original
  > record. View original record scrolls to the canonical Patient summary in the timeline. This is
  > source navigation, but it is not an exact-span panel.

## Shot 7 — Patient privacy projection

- **Time:** 03:32-04:00
- **Browser / profile / role:** Sarah Patient after an off-camera logout/login cut; same patient.
- **Starting state:** Patient page is in English and shows `Patient view`.
- **Exact action:** Point to `Internal Glance View is hidden`; show the two patient-facing timeline
  entries; open `Ambient Voice Prototype` and show only `Synthetic patient follow-up · patient`.
- **Visible result expected and verified:** No `Top Card`, internal Comments, Assign task, History,
  clinical Voice sample, or generated-source control is present. Patient Voice displays mock
  transcript/timestamps and the patient-safe result.
- **Maximum wait:** 6 seconds for the patient workspace; 3 seconds for Voice processing if the
  patient sample is recorded live. If the patient session is unavailable, remove this shot and do
  not claim patient privacy from an internal session.
- **Mutation / reset note:** Processing the patient fixture once creates one synthetic patient-safe
  Voice session. Do not process it twice.
- **Requirements:** `requirements.txt:34-40, 45-48, 51-53`.
- **Say exactly:**

  > Finally, the patient session is a different server-side projection. The internal Glance View,
  > comments, tasks, and history controls are absent. Only patient-facing records and the patient
  > Voice fixture appear. The transcript is mock data, timestamps are fixture timestamps, and no
  > generated-source control is exposed. This is privacy by server-side projection, not by hiding a
  > button in the browser.

## Shot 8 — Honest close

- **Time:** 04:00-04:20
- **Browser / profile / role:** English Clinician or Staff workspace; no credential/configuration
  screen.
- **Starting state:** Return to the cleanest English workspace view; stop before any password or
  environment screen.
- **Exact action:** Point to the synthetic-only disclosure and end the recording.
- **Visible result expected and verified:** The deployed app remains on HTTPS; the repository and
  deployment evidence document PostgreSQL, redaction, fixture providers, and clean logs. No live
  DeepSeek call is shown.
- **Maximum wait:** 1 second. No fallback action.
- **Mutation / reset note:** Read-only ending. Sign out after recording if the browser is shared.
- **Requirements:** `requirements.txt:50-54, 74-85, 99-104`.
- **Say exactly:**

  > The deployed service uses HTTPS and PostgreSQL, and this demo remains synthetic. The fixture is
  > the default. DeepSeek is only an optional redacted adapter; no live call is shown. This prototype
  > is designed for a ten-second glance, not independently proven. It does not claim clinical
  > validation, live ASR, production PHI capture, or a final recorded video.

## Removed or replaced claims

The final recording must not include a successful click for a new-note composer, manual phrase
highlight creation, a second-browser SSE update, a live 409 conflict panel, task completion, live
DeepSeek, microphone capture, upload, Whisper inference, or diarization. These were either absent
from the deployed rehearsal or deliberately outside the Level-C boundary. The local tests and
technical evidence remain the correct place to discuss them.
