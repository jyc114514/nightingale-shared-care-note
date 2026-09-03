# Nightingale Real Clinic Demo Video QA

**Status before recording: NOT RECORDED - QA PENDING**
**Recording SSOT:** [`REAL_CLINIC_DEMO_RECORDING_MASTER_ZH_EN.md`](REAL_CLINIC_DEMO_RECORDING_MASTER_ZH_EN.md)
**Subtitle SSOT:** [`REAL_CLINIC_DEMO_SUBTITLES_EN.srt`](REAL_CLINIC_DEMO_SUBTITLES_EN.srt)

This checklist is completed only after the final human-recorded video is watched from beginning
to end. The existing 54.76-second WebM is supplementary technical evidence, not this final video.
The original user MP4 is not inspected or transformed in this preparation round.

## Pre-recording material validation (2026-09-03)

- Master cue ledger: **44 cues**, **706 English words**, final target time `00:07:22,000`.
- SRT: **44 cues**, exact normalized text match with the Master, continuous numbering, monotonic
  non-overlapping timestamps, English-only text.
- Master structure: **18 detailed beats**, each containing Chinese operation, wait condition,
  required/forbidden screen state, narration reference, mapping, evidence type, exit condition,
  fallback, and editing advice.
- Traceability: all **16 scenarios** plus the overall capability checklist are present.
- Forbidden-claim review: all detected terms are explicitly negated or bounded; no unqualified
  production, clinical-validation, general-ASR, medical-risk, or unbiased-learning claim is used.
- Video itself: **not yet recorded and therefore not passed**.

## File and structure

- [ ] Final human recording exists at the operator's chosen path.
- [ ] Original recording is preserved byte-for-byte; no trim, transcode, compression, or rename.
- [ ] Duration is between 6:00 and 8:00; target is approximately 7:22.
- [ ] Staff -> Clinician -> Patient order is clear; role changes happen off camera.
- [ ] English UI and English narration are used.
- [ ] Chinese operator instructions are not visible in the recording.
- [ ] Login pages, password fields, autofill, notifications, DevTools, terminals, and dashboards are absent.

## Subtitle and narration

- [ ] `REAL_CLINIC_DEMO_SUBTITLES_EN.srt` is imported without manual retyping.
- [ ] 44 cues are present, numbered continuously, strictly increasing, and non-overlapping.
- [ ] Last cue ends at `00:07:22,000` unless the final recording is intentionally re-timed.
- [ ] Subtitle text is English only and matches the Master cue ledger exactly.
- [ ] No subtitle cue contains Chinese operator instructions.
- [ ] Narration is approximately 706 English words and 95-110 WPM.
- [ ] Every cue is readable; no important UI text is covered by the subtitle bar.

## Direct UI demonstrations

- [ ] Staff opening shows `Staff A`, `Staff view`, `Sarah Tan`, and `Up to date`.
- [ ] Glance shows no more than six items.
- [ ] `Conflicting allergy information` is visibly first and its protected-first explanation is readable.
- [ ] Priority is explicitly distinguished from medical risk.
- [ ] `Review conflict` opens both source assertions without a Staff clinical decision.
- [ ] `Original source`/timeline shows the immutable source version and exact highlighted span, when the source result is stable.
- [ ] Comments entry point is shown only if it is clean; no rehearsal-labelled test task is shown.
- [ ] Clinician History/Compare/Before/After is shown only after current manual re-login verification.
- [ ] Publication shows `Patient publication review`, `Draft`, immutable evidence, and separate Approve/Publish semantics.
- [ ] Patient projection is shown only after current manual privacy recheck.

## Voice and failure boundaries

- [ ] Voice is described as prerecorded synthetic audio with a prepared timestamped transcript.
- [ ] No microphone, upload, live ASR, diarization, or provider key is shown or claimed.
- [ ] If Voice has no current result, the video does not click `Create care-note suggestion` to manufacture one.
- [ ] Provider/redaction behavior is presented as test/evidence-backed explanation, not live outage injection.
- [ ] Existing records remain visibly available when that claim is made.

## Privacy and overclaiming

- [ ] Patient view contains no Glance, internal conflict/source, comments, tasks, history, raw AI, or staff/clinician controls.
- [ ] Clinical note source text is not automatically translated or rewritten.
- [ ] No claim says the prototype is production-ready, clinically validated, generally multilingual, or free of hallucinations.
- [ ] No claim says priority is a medical risk score or calibrated confidence.
- [ ] No claim says the system performs real-time collaborative editing, external delivery, or live ASR.
- [ ] Benchmark pending is presented as a disclosed supplementary gap, not as passed latency evidence.

## Scenario coverage review

- [ ] Direct UI scenes: protected Glance, dual provenance, publication gate, role projections, and available Voice boundary.
- [ ] Evidence scenes: RBAC, safe logs/redaction, timeout/provider failure, CAS/409, and revision preservation.
- [ ] Explicit limitations: phone-only onboarding, trilingual ASR, streaming detection, external delivery receipt, broad medication NLP, and clinical validation.
- [ ] Each claim is traceable to [`REAL_CLINIC_DEMO_REQUIREMENT_TRACEABILITY.md`](REAL_CLINIC_DEMO_REQUIREMENT_TRACEABILITY.md).

## Human final review

- [ ] Watch the complete video once without pausing.
- [ ] Watch again with subtitles and verify cue timing against the spoken audio.
- [ ] Confirm no accidental write, duplicate task, stale state, or wrong role appears.
- [ ] Confirm the final frame stops on a stable workspace, not a login/configuration screen.
- [ ] Record reviewer initials/date and any cut list below.

Reviewer: ____________________  Date: ____________________
Result: `PENDING` / `PASS WITH CUTS` / `READY FOR FINAL PACKAGING`
Notes: ______________________________________________________________________
