# Real-clinic adversarial audit — Round 1

Audit baseline: 573f897a69864707f64b1846b2802a2674f69597

Audit scope: the released synthetic prototype was inspected before the Round 1 backend
changes. This document distinguishes an implemented protection from a product capability
that does not yet exist. A passing test is cited only for the behavior it actually exercises.

## Summary matrix

| # | Scenario | Status | Severity | Effort | First break | Round 1 decision |
|---:|---|---|---|---|---|---|
| 1 | Patient has no email | DOES NOT | High | M | A patient without an email cannot use the email/password login route | Deferred; design identity onboarding |
| 2 | Clinic isolation single failure | PARTIAL | Critical | M | A missed scope check could expose the entire patient/derived-record surface for a clinic | Improve the canonical scope path; defer database RLS |
| 3 | PHI beyond model redaction | PARTIAL | Critical | L | A raw value can escape through an exception, request log, provider/host retention, or future event payload | Local application logging hardened; external retention remains unknown |
| 4 | Redaction ordering | SURVIVES | High | M | A future caller bypassing the typed boundary could reintroduce an unsafe provider call | Strengthened with ordered safe events and no-provider-on-redaction-failure tests |
| 5 | Clinic B onboarding | PARTIAL | Medium | M | A new clinic cannot be provisioned through an audited admin workflow | Deferred |
| 6 | Trilingual consult | DOES NOT | High | XL | The current fixture has a prepared English transcript, not multilingual capture or ASR | Deferred; do not call fixture Voice multilingual |
| 7 | Allergy at minute 2 | DOES NOT | Critical | L | A contradiction is stored as unrelated text and no clinician flag is created | Implement the bounded allergy vertical slice |
| 8 | Model hangs 45 seconds | PARTIAL | High | M | A synchronous processing request holds the clinician request open through timeout/retry | Bounded total wait added; durable asynchronous queue remains deferred |
| 9 | Provider 503 for an hour | PARTIAL | High | M | New suggestions fail safely, but the UI has no explicit stale/provider-outage state or retry policy | Fail-fast circuit and degraded UI added; durable queue remains deferred |
| 10 | Concurrent editing | SURVIVES | High | M | A same-section stale write is rejected and preserved as a write conflict | Existing strength; keep separate from clinical conflicts |
| 11 | Appointment link never delivered | DOES NOT | Medium | L | There is no link-generation, delivery, receipt, retry, or acknowledgement path | Deferred |
| 12 | Wrong patient-facing dosage | PARTIAL | Critical | L | Bounded portal publication gate blocks mismatched synthetic dosage and separates draft, clinician approval, publish, recall, and correction; external delivery is absent | Round 4 partial gate; do not equate Accept with Publish |
| 13 | Nurse allergy vs patient no allergies | DOES NOT | Critical | M | No normalized assertion or semantic comparison can create a reviewable contradiction | Implemented now in Phase 2 |
| 14 | Meaningful risk/confidence/importance | PARTIAL | High | M | Display priority can be mistaken for medical risk and has no protected safety floor | Improved now through a deterministic safety floor |
| 15 | Exposure bias and fatigue | PARTIAL | High | L | Only surfaced interactions create feedback; there is no impression denominator and ordinary adaptive feedback has no safety floor | Partially implemented now through protected feedback suppression; impression logging deferred |
| 16 | Edited source provenance | SURVIVES | High | M | A source remains resolvable if every new derived record preserves the immutable version/span contract | Existing strength; reuse the same contract for assertions |

## Scenario 1 — Patient has no email

Status: PARTIAL

Severity: High

Effort: M

Where:

- backend/app/models/user.py:12-19 — User requires a unique email and stores a password hash.
- backend/app/api/routes/auth.py:54-81 — login lowercases and looks up only User.email, then verifies a password.
- backend/app/schemas/auth.py:8-12 — LoginRequest requires email and password.
- backend/app/models/patient.py:22-29 — PatientUserLink binds a user to a patient, but is not an alternate identity.

Current call/data path:

The patient link is resolved only after the caller has authenticated. There is no phone,
OTP, magic-link, WhatsApp identity, invitation token, or patient portal enrollment flow.
The synthetic patient account therefore works only because the seed creates an email identity.

What breaks first:

A real patient record without an email has no supported login credential. The care team can
still use the internal staff/clinician path, but the patient cannot enter the patient-facing
projection through the current auth route.

Blast radius:

This blocks patient onboarding for every non-email identity. It is an identity product gap,
not evidence that the existing clinic scope is unsafe.

What already mitigates it:

PatientUserLink gives an explicit server-side binding once a user exists. Patient-facing
responses are separately projected and do not depend on a client role selector.

Build it better:

Add an invitation-bound phone/OTP or magic-link enrollment flow, verified identity binding,
expiry/revocation, rate limits, and an audited recovery path. Do not infer identity from
the patient name or from a comment body.

Evidence/tests:

The role and patient projection tests exercise the seeded email identity and patient link;
there is no no-email onboarding test because the capability is absent.

Round 1 decision: Deferred; not part of the bounded allergy safety slice.

## Scenario 2 — Clinic isolation single failure

Status: PARTIAL

Severity: Critical

Effort: M

Where:

- backend/app/services/authorization.py:45-81 — get_patient_context is the canonical patient scope resolver.
- backend/app/services/authorization.py:83-93 — get_entry_context reuses patient scope for entries.
- backend/app/api/dependencies.py:35-55 — the session resolves only an active authenticated User.
- backend/app/models/entry.py:12-19 and backend/app/models/patient.py:11-29 — records carry clinic foreign keys and patient links.
- backend/app/api/routes/gate_b.py:92-126 and 128-243 — timeline/Glance add explicit patient and clinic predicates.

Current call/data path:

Protected routes first resolve a Patient and then accept a matching ClinicMembership or
PatientUserLink. Internal resources generally repeat the clinic predicate, and foreign
patients become 404. The database has tenant foreign keys, but there is no PostgreSQL Row
Level Security policy. Some route-level list queries rely on the patient ID returned by the
canonical context and would be dangerous if a future caller bypassed that resolver.

What breaks first:

A single route that queries by resource ID without checking clinic and patient scope could
turn an ID leak or guessed ID into cross-clinic disclosure. The blast radius includes
timeline, comments, tasks, highlights, assertions, and derived projections unless each
resource path remains scoped.

Blast radius:

Critical: this is a tenant boundary. Application authorization is strong evidence for the
tested routes, but it is a single enforcement layer rather than defense in depth.

What already mitigates it:

get_patient_context returns 404 for foreign scope; get_entry_context checks the entry clinic;
role checks are server-side; RBAC tests cover Clinic A versus Clinic B, patient denial, and
admin read-only behavior.

Build it better:

Keep get_patient_context as the only scope entry point, add resource-specific scope helpers
for new assertion/conflict routes, add composite clinic/patient consistency constraints where
the target database supports them, and evaluate PostgreSQL RLS with migrations and service
role boundaries. RLS is deferred here because the local test and deployment contract is not
yet an RLS deployment.

Evidence/tests:

backend/tests/test_rbac_scope.py and provenance/collaboration tests catch known cross-clinic
paths. They cannot prove that a newly added production route will never skip the helper, and
there is no PostgreSQL RLS test in this baseline.

Round 1 decision: Partial; improve the new allergy routes with the same canonical helper and
add cross-clinic assertion/conflict tests.

## Scenario 3 — PHI beyond model redaction

Status: PARTIAL

Severity: Critical

Effort: L

Where:

- backend/app/ai/redaction.py:48-84 — name, Singapore ID, and phone detectors plus fail-closed scan.
- backend/app/services/ai_processing.py:61-73 and 149-220 — safe job errors and redaction/provider path.
- backend/app/ai/deepseek.py:102-145 — provider failures map to enumerable error codes without raw response logging.
- backend/app/api/routes/events.py:29-87 — SSE payload contains resource type/id and event kind only.
- backend/app/services/entries.py:42-70 — audit rows contain identifiers, actions, and versions but no content field.
- backend/alembic.ini:1-31 — only standard Alembic/SQLAlchemy console logging is configured.

Current call/data path:

The tested AI path stores a redacted payload and uses safe error codes. Audit and SSE
structures are metadata-only. There is no application-wide log sanitizer, structured
request/response logging policy, exception middleware audit, or independent retention
evidence for Render/provider logs. Test output and third-party retention are environmental
unknowns.

What breaks first:

A future exception or debug log that includes a raw request, provider response, or source
text could leak data after the model redaction boundary has already succeeded. A provider
or hosted log retention policy could also exceed this repository's evidence.

Blast radius:

Any raw value in process logs, job failures, traces, or external retention can affect more
than one patient or clinic. The local synthetic-only dataset limits current exposure but does
not prove production privacy.

What already mitigates it:

redact_text runs before RedactedPayload validation; the DeepSeek adapter rechecks the payload;
safe provider error codes, metadata-only audit rows, and metadata-only SSE are covered by
tests. No real PHI is permitted.

Build it better:

Introduce a central safe logging adapter, correlation IDs with allowlisted fields, exception
sanitization, negative log-leak tests for every route family, and a documented provider/host
retention review. Keep raw note text out of audit by schema, not by convention.

Evidence/tests:

test_redaction.py, test_ai_processing.py, test_deepseek_provider.py, and test_events.py
cover the local boundary. They do not verify Render or provider retention and do not replace
an application-wide sanitizer.

Round 1 decision: Deferred; record as a Round 2 hardening candidate.

Round 3 update (2026-09-02): Application logs now use a closed-vocabulary, metadata-only
`safe_event` boundary with a defensive sanitizer and generic unexpected-exception middleware. A
local audit script checks explicitly supplied logs for synthetic names, Singapore IDs, phones,
authorization material, keys, credentialed database URLs, and cookies without printing matches.
The redaction/provider event-order tests prove that provider start occurs only after redaction and
that redaction failure makes zero provider calls. Local application logging is hardened, but
Render/Uvicorn host retention and third-party provider retention remain Unknown; the status stays
PARTIAL.

## Scenario 4 — Redaction ordering

Status: SURVIVES

Severity: High

Effort: M

Where:

- backend/app/services/ai_processing.py:149-164 — known-name lookup, redact_text, source-reference redaction, then typed payload construction.
- backend/app/services/ai_processing.py:205-218 — provider receives RedactedPayload and output is schema validated.
- backend/app/ai/redaction.py:62-84 — replacements are followed by a secondary detector.
- backend/app/ai/deepseek.py:94-100 — the optional adapter rejects a non-redacted typed payload before network I/O.

Current call/data path:

raw text -> _known_names -> redact_text -> secondary_detector -> RedactedPayload ->
provider.process. Source references are separately redacted. The fixture path is the
default, and the optional provider cannot receive an arbitrary dict through its typed method.

What breaks first:

The boundary would regress if a new caller invokes a provider directly, adds a new sensitive
token type without updating the detector, or logs the raw input before redaction.

Blast radius:

The provider boundary is high impact, but the current supported path is narrow and tested.

What already mitigates it:

Fail-closed redaction, known synthetic names, ID/phone patterns, a second detector, typed
Pydantic payloads, and provider-spy tests provide a real local control.

Build it better:

Keep providers dependent on RedactedPayload, add a boundary-level audit hook containing only
hashes/counts, extend detectors through explicit fixtures, and keep live-provider calls opt-in.

Evidence/tests:

test_redaction.py, test_ai_provider_boundary.py, test_ai_processing.py, and
test_deepseek_provider.py cover ordering, fail-closed behavior, and no-provider-on-failure.

Round 1 decision: Existing strength; preserve while adding the allergy write-path derivation.

Round 3 update (2026-09-02): The optional provider path records ordered metadata events for job
creation, redaction completion, provider call start/completion or safe failure, and provenance
completion. The provider performs a second redaction check, and the total budget prevents an
unbounded retry loop. Existing fixture behavior remains the default. The source ordering status
remains SURVIVES for the tested local application path, without implying external retention
certification.

## Scenario 5 — Clinic B onboarding

Status: PARTIAL

Severity: Medium

Effort: M

Where:

- backend/app/scripts/seed_demo.py:305-350 — synthetic Clinic A/Clinic B creation and memberships.
- backend/app/models/clinic.py:9-17 and membership.py:11-22 — clinic and membership persistence.
- backend/app/config.py:18-57 — one process DATABASE_URL and global runtime settings.
- backend/app/api/routes/auth.py:22-51 — membership listing, without an admin onboarding command.

Current call/data path:

Clinic B exists as a seed fixture to prove isolation. A new clinic requires direct database
or script-level provisioning; there is no scoped admin workflow for creating a clinic,
inviting staff, assigning roles, linking patients, rotating settings, or documenting an
operational handoff.

What breaks first:

An operator cannot safely onboard Clinic B through the product. Manual provisioning can omit
a membership or accidentally reuse a patient/link, and there is no onboarding audit trail.

Blast radius:

Operational error can create either denial of care-team access or a tenant-boundary risk.

What already mitigates it:

ClinicMembership is unique per clinic/user; Patient and all canonical records carry clinic
foreign keys; the seed produces a deterministic separate patient and staff identity.

Build it better:

Add an authenticated admin-only onboarding workflow with invitation states, membership
auditing, clinic-scoped settings, and migration/rollback evidence. Keep provisioning separate
from patient-facing login.

Evidence/tests:

RBAC tests prove the seeded two-clinic topology. No onboarding workflow or production
provisioning test exists.

Round 1 decision: Deferred.

## Scenario 6 — Trilingual consult

Status: DOES NOT

Severity: High

Effort: XL

Where:

- backend/app/voice/fixtures.py:1-75 — prerecorded synthetic fixture text.
- backend/app/voice/providers.py:1-180 — optional local ASR adapter boundary, not a production transcript.
- backend/app/services/voice.py:91-134 and 231-363 — fixture/local provider selection and post-capture processing.
- backend/app/static/voice-fixtures/expected_transcripts.json — prepared English synthetic transcript.

Current call/data path:

The achieved Voice path uses prerecorded WAV files and prepared timestamped transcript
segments. The optional faster-whisper adapter is lazy and was not a successful ASR run.
There is no evidence for code-switching, Hokkien, Malay, multilingual medical vocabulary,
diarization, overlap handling, or noisy-environment capture. The current AI summary path is
post-consult and fixture-first.

What breaks first:

A trilingual consult would be represented by the prepared fixture rather than transcribed
from speech. A downstream summary could silently lose language-specific terms if this were
presented as real ASR.

Blast radius:

Incorrect multilingual transcription can affect every derived summary and provenance link.
Calling the fixture multilingual would overclaim capability.

What already mitigates it:

The UI and documentation explicitly label prerecorded synthetic audio, prepared transcript,
no ASR inference, no microphone, and no diarization.

Build it better:

Treat multilingual ASR, terminology evaluation, speaker labeling, overlap/noise handling,
redaction of audio/transcripts, and human correction as a separate evidence-gated project.

Evidence/tests:

test_voice.py proves fixture scope, safe errors, timestamps, and role/patient projection. It
does not prove multilingual ASR quality.

Round 1 decision: Deferred; no Voice changes in this round.

## Scenario 7 — Allergy at minute 2

Status: DOES NOT

Severity: Critical

Effort: L

Where:

- backend/app/services/ai_processing.py:122-288 — creates a suggestion/highlight but has no clinical assertion normalization.
- backend/app/models/entry.py:12-29 and entry_version.py:11-21 — store free-text immutable entries.
- backend/app/services/importance.py:119-167 — ranking factors are display features, not semantic allergy comparison.
- backend/app/api/routes/gate_b.py:328-377 — review changes highlight status only.

Current call/data path:

A nurse note saying an allergy is present and a patient/AI note saying no allergies are
currently just separate entries or highlights. CAS detects stale writes to one entry; it
does not compare clinical meaning across entries. The existing conflict table is an
optimistic-write conflict, not a clinical contradiction.

What breaks first:

The clinician sees text but no deterministic, source-anchored allergy conflict and no
protected action that cannot be buried by ordinary importance feedback.

Blast radius:

This is a safety-critical semantic gap. It can affect review ordering and clinician trust,
although the prototype does not make a diagnosis or treatment decision.

What already mitigates it:

Entries and versions are immutable, provenance can resolve exact spans, and clinician review
is explicit. These preserve evidence but do not detect contradiction.

Build it better:

Implement only a closed penicillin vocabulary first: extract exact present/absent assertions
with safe abstention, compare active same-patient assertions, create a dual-provenance
clinical conflict, and protect its Glance item with a deterministic safety floor. Let a
clinician adjudicate; do not infer truth from role or LLM output.

Evidence/tests:

Existing provenance and concurrency tests prove the source and write-conflict primitives.
There is no clinical_assertions model, extractor, clinical_conflicts model, or semantic
conflict test at this baseline.

Round 1 decision: Implemented now in Phase 2, strictly limited to the closed synthetic slice.

Baseline status: DOES NOT — no clinical assertion or semantic conflict path existed.

Round 1 improvement: The backend now extracts closed-vocabulary penicillin assertions,
preserves exact immutable provenance, opens dual-source conflicts, protects the Glance item,
and exposes clinician CAS adjudication.

Remaining limitation: This is not general allergy/medication NLP, multilingual reasoning,
temporality resolution, or a clinical truth engine; unsupported and ambiguous text abstains.

## Scenario 8 — Model hangs 45 seconds

Status: PARTIAL

Severity: High

Effort: M

Where:

- backend/app/config.py:34-35, 57-59 — DeepSeek timeout is configurable up to 120 seconds.
- backend/app/ai/deepseek.py:55-80 — HTTP client uses a total timeout and a 5-second connect cap.
- backend/app/ai/deepseek.py:102-118 — one retry is made for timeout/request/5xx failures.
- backend/app/api/routes/ai_processing.py:32-67 — processing is called synchronously inside the request.

Current call/data path:

The optional path can spend up to approximately two configured timeout windows, plus
connection/transport overhead, because the endpoint waits for provider.process. At the
default 20-second total timeout and one retry, the practical upper bound is roughly 40
seconds before safe failure, not a guaranteed 45-second bound. No background queue or
client-visible retry-after state exists.

What breaks first:

The clinician's HTTP request remains open while the provider is unavailable. The final state
is a safe failed_provider job/error code, but the UI cannot continue the rest of the review
flow from an asynchronous job handle in this route.

Blast radius:

One slow provider can consume request workers and delay concurrent staff actions. The
fixture path avoids this in the normal demo.

What already mitigates it:

The provider has a bounded timeout, one retry, safe enumerable errors, and no silent fixture
fallback. Glance reads are not on this provider path.

Build it better:

Move provider work to a bounded worker/outbox, return a job immediately, add retry budget and
circuit state, and keep the last materialized projection available. Add tests using a fake
clock/transport rather than waiting 40 seconds.

Evidence/tests:

DeepSeek provider tests cover timeout and retry mapping. They do not measure request-worker
exhaustion or prove an asynchronous production queue.

Round 1 decision: Deferred; do not expand this round beyond allergy safety.

Round 3 update (2026-09-02): DeepSeek attempts now use an 8-second per-attempt timeout, 12-second
monotonic total budget, and at most two attempts. A synchronous route still waits for the bounded
work, so this improves the 45-second hang but does not provide an asynchronous queue or worker
isolation. The status remains PARTIAL.

## Scenario 9 — Provider 503 for an hour

Status: PARTIAL

Severity: High

Effort: M

Where:

- backend/app/ai/deepseek.py:115-126 — transient 5xx/retry and safe provider error mapping.
- backend/app/services/ai_processing.py:205-220 — failed jobs persist a safe status/error code.
- backend/app/services/glance.py:21-53 — Glance projection is maintained independently of provider reads.
- backend/app/api/routes/gate_b.py:128-243 — Glance reads materialized rows without calling a provider.

Current call/data path:

An unavailable provider produces a failed job and no new source/highlight. Existing
patient_glance_items remain readable. There is no provider-health/stale timestamp in the
Glance response, no circuit breaker, no scheduled retry, and no rule-derived fallback.
The system does not silently pretend that fixture output came from the failed provider.

What breaks first:

The clinician can see last-known materialized items but cannot tell from the Glance payload
that a new suggestion attempt has been unavailable for an hour unless they inspect the job
state separately.

Blast radius:

Review freshness and trust suffer; existing source integrity remains intact. A fake fallback
would be worse because it would misrepresent provider provenance.

What already mitigates it:

Fixture is default and network-free; provider failures are explicit; materialized reads are
provider-free; failed job metadata is safe.

Build it better:

Add explicit provider health/staleness metadata, bounded retry/circuit policy, operator
visibility, and a clearly labeled rule-based fallback only if its provenance and semantics
are distinct from AI output.

Evidence/tests:

Provider failure and materialized-read tests cover the local behavior. No hour-long outage
or stale-label production test exists.

Round 1 decision: Deferred reliability work; preserve current safe failure.

Round 3 update (2026-09-02): External provider state is persisted per clinic/provider with a
three-failure threshold, 60-second cooldown, database-CAS half-open probe, safe provider-status
API, and bilingual degraded-mode UI. When the circuit is open, no provider call is made and the
job records `provider_circuit_open`; existing Glance/timeline/tasks/comments/source paths remain
usable and there is no fixture fallback. There is no durable queue, scheduled retry, or automatic
replay, so the status remains PARTIAL.

## Scenario 10 — Concurrent editing

Status: SURVIVES

Severity: High

Effort: M

Where:

- backend/app/services/entries.py:143-181 — conditional update on Entry.current_version and preserved Conflict row.
- backend/app/api/routes/entries.py:105-132 — stale write maps to HTTP 409.
- backend/tests/test_concurrent_edits.py:17-68 — independent sections and same-section stale write.

Current call/data path:

The client supplies expected_version. The database conditional update accepts exactly one
same-section writer; a stale writer gets a deterministic 409 and its attempted content is
preserved in the optimistic Conflict table. Different entries have independent CAS keys.

What breaks first:

This path detects write races, not semantic contradictions. A successful CAS write can still
contain a clinically conflicting statement, which is why the allergy conflict path must be a
different model and API.

Blast radius:

The current write safety applies to entry revisions covered by the role authorization rules.
It does not automatically protect newly added clinical records unless they receive their own
version/CAS semantics.

What already mitigates it:

Immutable EntryVersion snapshots, audit metadata, conflict preservation, and independent
entry IDs are tested through the real API.

Build it better:

Keep CAS and clinical adjudication separate. For clinical conflicts, add a version field and
return 409 on stale adjudication while preserving only safe resolution metadata.

Evidence/tests:

test_concurrent_edits.py and test_revision_history.py pass for the existing entry path.

Round 1 decision: Existing strength; reuse the discipline for conflict adjudication.

## Scenario 11 — Appointment link never delivered

Status: DOES NOT

Severity: Medium

Effort: L

Where:

- No appointment, delivery, receipt, SMS, email, WhatsApp, or acknowledgement model/route
  exists in backend/app/models or backend/app/api/routes.
- backend/app/models/entry.py:12-29 stores source references, not delivery state.

Current call/data path:

An appointment instruction can be written as a patient-facing entry, but the system has no
link generation, destination binding, delivery provider, retry, receipt, or patient
acknowledgement path.

What breaks first:

The team cannot distinguish “instruction was authored” from “the patient received and
acknowledged a safe, identity-bound appointment link.”

Blast radius:

Missed follow-up and ambiguous identity can affect care coordination. This is outside the
current synthetic note scope.

What already mitigates it:

Patient-facing entries are server-projected and clinic scoped; no false delivery claim is
made.

Build it better:

Design a separate notification subsystem with signed expiring links, verified destination
identity, provider receipts, retries, bounce handling, and explicit correction/revocation.

Evidence/tests:

There are no delivery tests; repository search found no implementation.

Round 1 decision: Deferred.

## Scenario 12 — Wrong patient-facing dosage

Status: PARTIAL

Severity: Critical

Effort: L

Where:

- backend/app/services/authorization.py:136-145 — patient reads are limited to two entry types and patient-facing visibility.
- backend/app/api/routes/patients.py:75-140 — patient projection omits internal entries and metadata.
- backend/app/services/ai_processing.py:232-268 — provider output creates an internal system suggestion.
- backend/app/services/highlights.py:139-167 — review changes suggestion state and audit metadata only.

Current call/data path:

AI output is an internal suggestion; Accept/Reject changes a highlight state and does not
publish a patient entry. Round 4 adds a separate typed patient-publication projection. A
Staff or Clinician can prepare an internal draft, but only a Clinician can approve and then
explicitly publish the exact draft content. The portal projection includes only current
published content and safe withdrawal/correction notices; it does not expose raw AI entries,
comments, conflicts, source IDs, or publication history to a Patient.

What breaks first:

The bounded workflow blocks the demonstrated wrong dosage (`500 mg` source versus `1000 mg`
draft), but it intentionally abstains from unsupported medication grammar. Source-version
changes after approval, stale workflow writes, ambiguous/multiple doses, and unsupported forms
remain blocked rather than guessed.

Blast radius:

Patient-facing medication errors can be high impact. The prototype avoids the specific
silent-publish failure by keeping AI entries internal, but it does not solve the product
workflow.

What already mitigates it:

Server-side patient projection, role-owned writes, immutable source and publication-content
versions, deterministic dosage evidence, explicit clinician approval/publication, workflow CAS,
metadata-only audit rows, and safe recall/correction states prevent the current Accept action
from rewriting or exposing raw AI text.

Build it better:

Extend the bounded gate only with a separately reviewed medication vocabulary and a production
retention/notification policy. If external delivery is added, give it its own provider boundary,
delivery receipt, retry, and recall semantics; do not imply those properties from this portal-only
prototype.

Evidence/tests:

Round 4 adds `test_patient_publications.py`, the `0014_patient_publications` migration, and
desktop/mobile Scenario F browser coverage for mismatch blocking, explicit approval/publication,
patient projection, recall, correction, and stale workflow CAS. The local published-care
benchmark is recorded separately. There is deliberately no external delivery test.

Round 1 decision: Deferred.

Round 4 update (2026-09-02): **PARTIAL — explicit portal gate implemented for a bounded
synthetic dosage slice; no external delivery, provider receipt, or general medication NLP.**
The detailed state machine, role matrix, source/version binding, and limitations are in
[`ROUND4_PATIENT_PUBLICATION_DESIGN.md`](ROUND4_PATIENT_PUBLICATION_DESIGN.md) and the
verification record is in [`evidence/round4_patient_publication.md`](evidence/round4_patient_publication.md).

## Scenario 13 — Nurse allergy vs patient no allergies

Status: DOES NOT

Severity: Critical

Effort: M

Where:

- backend/app/models/entry.py:12-29 and entry_version.py:11-21 — free-text source storage only.
- backend/app/services/highlights.py:67-74 — validates literal source spans, not clinical meaning.
- backend/app/services/entries.py:143-181 — CAS conflicts are version races, not semantic conflicts.
- No clinical assertion or allergy conflict symbol exists at this baseline.

Current call/data path:

The timeline can retain both statements, but there is no concept key, polarity, negation,
temporality, source assertion record, conflict pair, clinician adjudication, or protected
Glance item. “Nurse says penicillin allergy” and “patient says no known allergies” therefore
remain unrelated strings.

What breaks first:

The first clinician-facing failure is absence of a deterministic conflict flag with both
immutable sources. The clinician must manually notice and reconcile the contradiction.

Blast radius:

This is the narrow safety vertical selected for Round 1. It affects attention ordering and
semantic trust, not a claim that the system currently prescribes or diagnoses.

What already mitigates it:

All source text and revisions remain immutable and exact-span provenance can preserve the
evidence needed for later review.

Build it better:

Round 1 implements only penicillin present/absent extraction, safe abstention for ambiguous
phrases, same-clinic/patient conflict detection, dual provenance, clinician CAS
adjudication, and a protected safety floor.

Evidence/tests:

New tests must cover exact code-point spans, repeated phrases, idempotency, unsupported and
ambiguous abstention, Clinic B isolation, patient denial, dual provenance, stale
adjudication, all four resolution codes, and source preservation.

Round 1 decision: Implemented now in Phase 2.

Round 2 update (2026-09-01): The bounded penicillin slice is now a reviewable product path.
`ClinicalAssertion` records preserve exact immutable source versions and code-point spans;
`ClinicalConflict` pairs the present and absent assertions; and the protected Glance card opens
a dual-source drawer. Staff is read-only, while a clinician records one of four decisions with a
database compare-and-swap version check. Scenario D exercises both source links, the drawer, a
real stale `409`, and patient denial.

Remaining limitation: this is still only an explicit synthetic penicillin vocabulary. It is not
general allergy/medication NLP, diagnosis, clinical truth calibration, multilingual extraction, or
production safety certification. The status therefore remains PARTIAL rather than a claim that
the full real-clinic scenario is solved.

## Scenario 14 — Meaningful risk/confidence/importance

Status: PARTIAL

Severity: High

Effort: M

Where:

- backend/app/services/importance.py:78-98 — structured feature signature.
- backend/app/services/importance.py:101-167 — recency/risk/action/confirmation/adaptive score.
- backend/app/models/patient_glance_item.py:31-52 — persisted ranking contributions and explanation.
- backend/app/schemas/gate_b.py:63-99 — API exposes explicit risk and display-ranking fields separately.

Current call/data path:

The score combines base priority, recency, explicit risk presence, open action state,
clinician confirmation, and a bounded clinic-scoped feedback weight. It is a display
priority, not a calibrated risk probability or confidence. Before Round 1 there is no
safety-class field and a sufficiently negative adaptive history can lower an ordinary
item without a protected floor.

What breaks first:

A reviewer may read a high display priority as medical risk, or repeated negative feedback
may bury a safety-critical semantic conflict. The existing UI disclosure helps the first
problem but cannot solve the second.

Blast radius:

Ranking errors change attention allocation across a clinic. They must never mutate source
provenance or explicit risk fields.

What already mitigates it:

The formula is explainable, feedback is bounded to ±12, profiles are clinic scoped, and
risk/provenance are separate fields. Tests assert ordinary feedback does not mutate source
risk.

Build it better:

Add a deterministic safety class/floor that is independent of LLM output and adaptive
feedback. Persist pre-floor and floor-applied explanation fields; keep ordinary behavior
unchanged.

Evidence/tests:

test_self_learning_importance.py covers before/after ordinary feedback and the ±12 bound.
It does not cover a protected safety floor at this baseline.

Round 1 decision: Improved now through the Phase 2 safety floor.

Baseline status: PARTIAL — display priority was explainable and bounded, but it was not a
medical risk score and had no protected floor.

Round 1 improvement: Ranking explanations now expose pre-floor, safety floor, floor-applied,
and final values; an internally assigned allergy safety class keeps the item at or above 95.0.

Remaining limitation: The floor is an attention policy, not a calibrated risk/confidence
measure; ordinary ranking still requires future evaluation and clinician review.

Round 2 update (2026-09-01): Protected cards now expose product labels for the conflict, minimum
display priority, pre-floor value, floor value, and whether the floor was applied. Generic
Accept/Reject controls are withheld for protected conflicts, and protected Pin/Unpin feedback is
retained without changing the preference profile. The floor remains an attention policy, not a
calibrated medical risk or confidence score.

## Scenario 15 — Exposure bias and fatigue

Status: PARTIAL

Severity: High

Effort: L

Where:

- backend/app/services/importance.py:208-228 — only materialized rows matching a feedback feature are refreshed.
- backend/app/services/importance.py:230-301 — interaction events update a clinic/feature profile.
- backend/app/models/highlight_feedback_event.py:11-28 — append-only events have no applied/suppressed outcome or impression fields.
- backend/app/api/routes/gate_b.py:397-428 — feedback is accepted only when a caller submits an event.

Current call/data path:

Only surfaced highlights can receive feedback, so the system has no denominator for unseen
items, no impression log, no exposure duration, and no dismissal reason. Repeated negative
events can move ordinary feature weights to -12. There is no critical/safety floor.

What breaks first:

The system can learn from an interaction selection effect rather than a true preference and
can reward fatigue-driven dismissal. A critical item with no separate protection could be
demoted by adaptive feedback.

Blast radius:

Clinic-wide feature weights affect all matching patients in that clinic. Cross-clinic
isolation exists, but the feedback denominator and safety semantics are incomplete.

What already mitigates it:

Feature signatures exclude patient identity and raw text; feedback is clinic scoped,
idempotent, bounded, and separate from risk/provenance. This is not enough for exposure
unbiasing.

Build it better:

First protect the selected allergy safety class and suppress its feedback from preference
learning while retaining the event/audit. Later add impression/exposure events, negative
context, calibration, and offline evaluation before changing the learning policy broadly.

Evidence/tests:

The self-learning tests cover clinic isolation, idempotency, ordinary positive/negative
updates, and the bound. No impression denominator or protected feedback test exists at the
baseline.

Round 1 decision: Partially implemented now through protected-feedback suppression; impression
logging deferred.

Baseline status: PARTIAL — only surfaced items generated feedback, with no impression
denominator or safety protection.

Round 1 improvement: Feedback events for protected safety highlights are retained and audited
but have applied_to_profile=false and suppression_reason=protected_safety_class; their floor
and source fields remain unchanged.

Remaining limitation: Impression/exposure logging, calibration, fatigue signals, and offline
evaluation remain deferred; only the selected safety class is protected in this round.

Round 2 update (2026-09-01): Impression batches now record the bounded eligible candidate set,
rank, surfaced flag, feature signature, display priority, and safety metadata through an
idempotent internal API. Candidate storage is capped at 500 and reports truncation; the frontend
posts one opaque snapshot after a successful rendered Glance load and treats telemetry failure as
non-blocking. The summary provides a denominator for future analysis, but no IPS, counterfactual
correction, exposure-duration signal, calibration, or claim of unbiased self-learning is made.

## Scenario 16 — Edited source provenance

Status: SURVIVES

Severity: High

Effort: M

Where:

- backend/app/services/highlights.py:33-74 — source-version lookup, exact code-point span, and quote hash validation.
- backend/app/services/highlights.py:76-137 — new highlights are bound to an immutable version and projected.
- backend/app/api/routes/gate_b.py:245-272 — source response returns immutable version content and offsets.
- backend/tests/test_highlight_provenance.py:118-245 — Unicode, repeated occurrence, and old-version preservation.

Current call/data path:

A highlight stores source_entry_id, source_version_id, start/end offsets, quote, quote hash,
and offset unit. Editing an entry creates a new EntryVersion; the old source remains
resolvable. The frontend uses the source response to render an exact span.

What breaks first:

Any new derived record that stores only an entry ID or an approximate substring would lose
the original source after an edit. This is the specific failure Round 1 avoids for allergy
assertions.

Blast radius:

Broken provenance damages clinician trust and makes derived safety flags unauditable. It
does not inherently imply a tenant leak if authorization remains intact.

What already mitigates it:

Exact Python Unicode-codepoint validation, SHA-256 quote integrity, immutable versions,
cross-source checks, and patient/internal authorization are already tested.

Build it better:

Make the same source-version/span/hash tuple mandatory for every assertion and conflict
side, and provide a dual-provenance detail response without replacing the canonical note.

Evidence/tests:

test_highlight_provenance.py covers the existing contract, including non-BMP Unicode and
repeated phrases. New assertion tests must reuse the same validation discipline.

Round 1 decision: Existing strength; extend the contract to assertions.
