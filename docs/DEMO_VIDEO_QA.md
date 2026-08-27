# Nightingale demo video QA checklist

Use this checklist on the actual exported video. No video was recorded in this phase.

## Structural QA

- [ ] Runtime is between 4:00 and 5:00, with a target of 4:20.
- [ ] Spoken narration is approximately 105-120 words per minute and uses short, speakable
      sentences.
- [ ] Captions use `docs/DEMO_SUBTITLES_EN.srt`, start at 00:00:00, and end at 00:04:20 or are
      adjusted to the final edit without overlapping entries.
- [ ] Every shot has a visible beginning and end, and the action is synchronized with narration.
- [ ] No cut skips from a failed action to a success claim without an explanation.

## Product evidence QA

- [ ] Shot 1 shows English UI, Sarah Tan, internal role, and a connected realtime status.
- [ ] Shot 2 shows the six-or-fewer Top Card with action/status/risk/ranking and an AI source.
- [ ] Shot 3 shows the Level-C Voice disclosure, prerecorded audio, mock timestamps, segment seek,
      confidence unavailable, and exact source linkage.
- [ ] Shot 4 shows the Staff existing-note edit and the `@Clinician A` mention metadata.
- [ ] Shot 5 shows Resolve/Unresolve, Pin/Unpin, Compare Before/After, and Revert as a new
      version with history retained.
- [ ] Shot 6 distinguishes Hot, Warm, derived cold, and original-record navigation.
- [ ] Shot 7 shows the patient projection with internal controls and clinical sample absent.
- [ ] Shot 8 states the deployment and scope boundary without opening configuration screens.

## Trust and privacy QA

- [ ] The video never calls a fixture transcript an ASR transcript.
- [ ] The video never claims microphone capture, upload, Whisper inference, diarization, speaker
      labels, live DeepSeek, or production PHI audio.
- [ ] The exact Voice disclaimer is spoken or captioned:
      “This optional prototype uses prerecorded synthetic audio and a mock timestamped transcript.
      It demonstrates audio-to-summary provenance, but it does not claim live ASR or diarization.”
- [ ] No password, API key, database URL, cookie, browser storage, environment value, or raw log
      line appears in any frame or subtitle.
- [ ] Synthetic names and synthetic note text are the only record content shown.
- [ ] UX-01 is described as designed for a ten-second glance, not independently proven.

## Final review decision

Mark the video **ready for user review** only after all boxes pass. This QA sheet does not replace
the independent human UX-01 test, deployment security evidence, or the final submission checklist.
