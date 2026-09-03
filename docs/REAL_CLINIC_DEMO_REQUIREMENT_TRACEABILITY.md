# Real Clinic Demo Requirement Traceability

This file maps the final recording to **Scenarios 1-16 plus the overall capability checklist**.
It separates direct UI demonstration, automated-test evidence, explanation-only material, and
current limitations. It does not invent a Scenario 17.

## Video map

| Evidence mode | Scenes |
| --- | --- |
| Direct UI demonstration | 1-5, 7, and 9 where the current role/session is manually reverified |
| Test/evidence-backed explanation | 4, 6, 8, and 9 |
| Explicit partial / does not | 6 and 8, with limitations shown in the Brief |
| Current UI canary | Staff protected Glance, dual source, Staff boundary, Draft publication, History, Comments, Tasks, Voice fixture |

## Scenario 1 - Patient without email

- Status: **DOES NOT**.
- Where: `backend/app/api/routes/auth.py` and the email/password login UI; no phone-only or
  WhatsApp identity/onboarding route exists.
- What breaks first: a patient who exists only in a phone/WhatsApp thread cannot enter through the
  current identity flow.
- Video scene/cue: Scene 7 / Cue 32-35 explains the existing Patient projection; it does not claim
  phone onboarding.
- Evidence: automated RBAC and Patient projection tests; absence of a phone onboarding endpoint.
- Build better: add an audited phone-based enrollment and identity-linking flow with consent and
  clinic scope before presenting this as supported.
- Allowed claim: `Phone-only onboarding is not implemented in this prototype.`

## Scenario 2 - Clinic isolation

- Status: **SURVIVES** in the tested application boundary.
- Where: `backend/app/services/authorization.py` clinic-scoped access helpers and route dependencies.
- What breaks first: a future missing scope check could expose another clinic's patient/derived
  records; database RLS is not claimed.
- Video scene/cue: Scene 9 / Cue 40 references the required RBAC tests; no cross-clinic demo is
  fabricated.
- Evidence: `backend/tests/test_rbac_scope.py`, including cross-clinic denial and role-derived
  writes.
- Build better: add database-level RLS and a separate multi-clinic provisioning audit.
- Allowed claim: `The server-side clinic scope is covered by application tests; RLS is not claimed.`

## Scenario 3 - PHI beyond model redaction

- Status: **PARTIAL**.
- Where: `backend/app/ai/redaction.py`, `backend/app/observability/safe_logging.py`, and
  `backend/app/middleware/safe_exceptions.py`.
- What breaks first: an external provider or retained third-party dashboard could retain data
  beyond the local redaction/logging boundary.
- Video scene/cue: Scene 6 / Cue 30-31 explains redaction and safe failure without opening logs.
- Evidence: `backend/tests/test_redaction.py`, `test_ai_processing.py`, and
  `test_uvicorn_access_logging.py`; external retention is not observable here.
- Build better: add provider retention contracts, structured log review, and operational access
  review.
- Allowed claim: `Local redaction and logging are tested; external retention remains unknown.`

## Scenario 4 - Redaction before provider invocation

- Status: **SURVIVES** at the local provider boundary.
- Where: `backend/app/services/ai_processing.py` constructs a typed redacted payload before
  `app.ai.provider` is invoked.
- What breaks first: a future new provider call path could bypass the shared redaction boundary.
- Video scene/cue: Scene 6 / Cue 30-31, explanation-only.
- Evidence: `backend/tests/test_ai_provider_boundary.py` and `test_ai_processing.py`, including
  redaction failure with zero provider calls.
- Build better: enforce one provider adapter interface and a contract test for every adapter.
- Allowed claim: `The tested processing path redacts before provider invocation.`

## Scenario 5 - Clinic B onboarding

- Status: **PARTIAL**.
- Where: `Clinic`, `Membership`, and authorization models exist; no complete admin onboarding UI
  or audited provisioning workflow exists.
- What breaks first: a second clinic requires controlled user/clinic provisioning rather than a
  simple configuration toggle.
- Video scene/cue: Scene 8 / Cue 36-39 states this as a limitation.
- Evidence: clinic-scope tests cover isolation, not full onboarding.
- Build better: add admin provisioning, invite/consent, clinic configuration, and RLS migration.
- Allowed claim: `The data model is clinic-scoped; full Clinic B onboarding is deferred.`

## Scenario 6 - Trilingual consult and code-switching

- Status: **DOES NOT**.
- Where: `backend/app/voice/fixtures.py` and `backend/app/voice/providers.py` support the
  prerecorded fixture boundary; there is no production multilingual ASR pipeline.
- What breaks first: a Malay/English/Hokkien sentence is not converted into a validated transcript
  with downstream clinical semantics.
- Video scene/cue: Scene 6 / Cue 28-29 explicitly limits Voice to prerecorded synthetic audio and
  prepared transcript.
- Evidence: `backend/tests/test_voice.py`; no ASR/diarization quality result is claimed.
- Build better: collect consented multilingual evaluation data, add ASR/diarization, terminology
  checks, and human review before clinical use.
- Allowed claim: `Real trilingual ASR and code-switching are not implemented.`

## Scenario 7 - Allergy detected during a consult

- Status: **PARTIAL**.
- Where: `backend/app/services/clinical_assertions.py` and `clinical_conflicts.py` run bounded
  post-processing; they do not stream detection during a live consult.
- What breaks first: an allergy mentioned mid-consult is surfaced after the supported processing
  request, not as a live minute-two alert.
- Video scene/cue: Scene 2-3 / Cue 07-13 shows the post-process conflict and its sources.
- Evidence: `backend/tests/test_clinical_conflicts.py`.
- Build better: design a streaming, latency-bounded, human-confirmed detection path separately.
- Allowed claim: `This build demonstrates a bounded post-consult conflict slice.`

## Scenario 8 - Model hang

- Status: **PARTIAL**.
- Where: `backend/app/services/provider_resilience.py`, AI processing route, and configured
  request/provider bounds.
- What breaks first: a durable asynchronous job/queue is absent, so a long-running request still
  needs an explicit timeout/degraded response.
- Video scene/cue: Scene 6 / Cue 30-31 uses test/evidence explanation, not live injection.
- Evidence: `backend/tests/test_provider_resilience.py` and `test_ai_processing.py`.
- Build better: add durable jobs, cancellation, progress state, and replay-safe recovery.
- Allowed claim: `The bounded failure path is tested; no durable queue is claimed.`

## Scenario 9 - Provider 503 for an hour

- Status: **PARTIAL**.
- Where: `backend/app/services/provider_resilience.py` and the provider-status UI.
- What breaks first: new generation can fail or enter degraded state; durable replay and a long-term
  stale-content policy are not implemented.
- Video scene/cue: Scene 6 / Cue 30-31 explains explicit failure and existing-record availability.
- Evidence: `backend/tests/test_ai_provider_boundary.py`, `test_ai_processing.py`, and
  `test_provider_resilience.py`.
- Build better: add durable retry/replay, operator visibility, and expiry rules for stale output.
- Allowed claim: `Provider failure is explicit in the tested path; no silent fixture fallback is claimed.`

## Scenario 10 - Concurrent editing

- Status: **SURVIVES** for the tested optimistic-concurrency contract.
- Where: `backend/app/services/entries.py` performs conditional version updates and stores stale
  submissions as conflicts.
- What breaks first: a client that ignores the 409 response could confuse users, but last-write-wins
  is not silently used by the tested path.
- Video scene/cue: Scene 4 / Cue 18-22 explains the result; no live failure injection is required.
- Evidence: `backend/tests/test_concurrent_edits.py` and `test_revision_history.py`.
- Build better: add clearer conflict recovery UX, notifications, and broader multi-client testing.
- Allowed claim: `Same-section stale writes return deterministic 409 and preserve both submissions.`

## Scenario 11 - Appointment link delivery

- Status: **DOES NOT**.
- Where: no external appointment/message delivery, receipt, retry, or acknowledgement route exists.
- What breaks first: a generated internal draft cannot prove that a patient received an external
  message.
- Video scene/cue: Scene 5 / Cue 27 explicitly says external message delivery is not claimed.
- Evidence: absence of a delivery adapter; publication tests stop at the portal workflow.
- Build better: add consented delivery adapters, receipts, retry, recall semantics, and audit.
- Allowed claim: `The prototype has a portal-only publication gate, not delivery confirmation.`

## Scenario 12 - Wrong patient-facing dosage

- Status: **PARTIAL**.
- Where: `backend/app/services/publication_evidence.py`, `patient_publications.py`, and
  `frontend/src/App.tsx` publication review.
- What breaks first: unsupported or mismatched dosage is blocked by the bounded gate; external
  delivery and receipt are outside the build.
- Video scene/cue: Scene 5 / Cue 23-29 directly demonstrates Draft, immutable evidence, dosage
  check, and separate Approve/Publish semantics.
- Evidence: `backend/tests/test_patient_publications.py` and `frontend/tests/e2e/publication.spec.ts`.
- Build better: broaden medication terminology validation only with authoritative references and
  human confirmation.
- Allowed claim: `Accept is not Publish; the tested dosage slice fails closed.`

## Scenario 13 - Contradictory allergy assertions

- Status: **PARTIAL** bounded semantic slice.
- Where: `backend/app/services/clinical_conflicts.py`, `clinical_assertions.py`, and protected
  Glance selection.
- What breaks first: unsupported vocabulary or broader clinical semantics are not generalized;
  supported penicillin assertions remain separately reviewable.
- Video scene/cue: Scene 2-3 / Cue 07-13 directly shows protected ranking, two sources, and Staff
  read-only boundary.
- Evidence: `backend/tests/test_clinical_conflicts.py`; current Staff canary observed the same UI
  path without adjudication.
- Build better: expand the vocabulary only with a reviewed evaluation set and clinician adjudication.
- Allowed claim: `The demo shows a bounded penicillin contradiction slice, not general semantic NLP.`

## Scenario 14 - Risk, confidence, and importance meaning

- Status: **PARTIAL**.
- Where: `backend/app/services/glance_read.py` and `importance.py` keep display priority,
  explicit risk, safety class, and review state separate.
- What breaks first: users may misread a workflow priority as a medical risk or calibrated confidence.
- Video scene/cue: Scene 2 / Cue 08-09 directly shows the explanation and protected-first policy.
- Evidence: `backend/tests/test_clinical_conflicts.py`, `test_impressions.py`, and Glance UI text.
- Build better: add calibration studies and separate confidence semantics before clinical decisions.
- Allowed claim: `Priority is workflow ordering, not a medical risk score or calibrated probability.`

## Scenario 15 - Exposure bias, fatigue, and self-learning

- Status: **PARTIAL**.
- Where: `backend/app/services/impressions.py`, `importance.py`, and protected feedback handling.
- What breaks first: surfaced-only interaction data cannot estimate what the ranking failed to show;
  the prototype has no IPS/counterfactual correction or fatigue study.
- Video scene/cue: Scene 2 / Cue 09 and Scene 8 / Cue 36-39 explain the boundary; no claim of
  unbiased learning is made.
- Evidence: `backend/tests/test_impressions.py`, `test_self_learning_importance.py`, and
  `test_clinical_conflicts.py`; protected feedback is excluded from ordinary preference learning.
- Build better: add exposure-aware evaluation, fatigue monitoring, protected classes, and a human
  release gate for ranking changes.
- Allowed claim: `Protected safety items are not learned away; unbiased learning is not claimed.`

## Scenario 16 - Edited-source provenance

- Status: **SURVIVES** under the tested immutable-version/span contract.
- Where: `backend/app/services/highlights.py`, `backend/app/api/routes/gate_b.py`, and the
  `ImmutableTimelineSource` UI path.
- What breaks first: a future derived record that stores only an entry ID or approximate text would
  lose exact historical addressability; the current contract stores source version, offsets, quote,
  and hash.
- Video scene/cue: Scene 3 / Cue 10-13 directly shows source navigation and exact span; Scene 4 /
  Cue 20-22 explains old/current version separation.
- Evidence: `backend/tests/test_highlight_provenance.py`, including Unicode, repeated occurrence,
  old-version preservation, and integrity failure; Playwright provenance checks.
- Build better: require the same tuple for every derived assertion and expose stale dependent output
  explicitly where applicable.
- Allowed claim: `The tested highlight resolves to its immutable source version and exact span.`

## Overall capability checklist

| Capability | Status | Video/evidence treatment |
| --- | --- | --- |
| Streaming consult audio and noisy-environment ASR | DOES NOT | Not demonstrated; stated as a limitation. |
| Speaker attribution and diarization | DOES NOT | Voice fixture is explicitly not diarization. |
| Within-statement code-switching | DOES NOT | No trilingual ASR claim. |
| Multilingual downstream processing | DOES NOT | No broad multilingual clinical pipeline. |
| Medical terminology/dosage confirmation | PARTIAL | Bounded synthetic dosage gate plus clinician gate; no general terminology validation. |
| Immutable, version-bound provenance | SURVIVES | Scene 3 direct UI and provenance tests. |
| Negation, correction, and conflicting-source extraction | PARTIAL | Bounded penicillin assertions; not general NLP. |
| Real-time collaborative editing without lost updates | PARTIAL | CAS/409 is tested; no CRDT/OT claim. |
| AI regeneration preserving human-confirmed state | PARTIAL | Suggestions remain reviewable; broader regeneration policy is bounded. |
| Contradictory human/patient/AI assertions | PARTIAL | Protected allergy conflict and clinician boundary. |
| Distinct clinician/staff/patient outputs | SURVIVES in tested projection | Scenes 4 and 7, with Patient manual recheck required before recording. |
| Self-learning bounded and auditable | PARTIAL | Metadata and protected-feedback suppression; no debiasing claim. |

## Final claim rule

The final video may say what the current UI shows, what the named tests prove, and what the Brief
classifies as `SURVIVES`, `PARTIAL`, or `DOES NOT`. It must not turn an explanation-only item into
a claimed live failure injection, and it must not translate clinical note source text.
