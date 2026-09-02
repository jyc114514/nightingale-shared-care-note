# Round 1 iteration decision

Baseline: 573f897a69864707f64b1846b2802a2674f69597

Round: 1 of 10

Decision: implement one closed, source-anchored allergy safety vertical slice in the backend.

## Why Scenario 13 plus Scenario 15

Scenario 13 is the clearest semantic trust gap: the current system preserves both notes but
cannot distinguish present from absent allergy assertions or show the contradiction as one
reviewable object. Scenario 15 explains why a safety item cannot be treated like an ordinary
preference: an interaction-driven ranking signal is subject to exposure selection and fatigue.

Together they justify a small invariant:

    A detected allergy contradiction is a clinician-review item with immutable dual sources.
    Ordinary preference feedback may be recorded as evidence, but it cannot train that item
    below a deterministic safety floor.

This is an attention and provenance control, not diagnosis, confidence calibration, or
treatment advice.

## Why one vertical slice

The released application already has immutable EntryVersion records, exact code-point
provenance, clinic authorization, materialized Glance rows, bounded feedback, and metadata-only
audit/events. A narrow allergy slice can reuse these primitives and be independently tested
without pretending that generic clinical NLP is solved.

Adding a small number of well-defined fields and two services is more falsifiable than
adding a broad classifier whose behavior cannot be audited. The new tables preserve source
records and can be rebuilt from immutable versions.

## Why allergy-only

Round 1 supports only penicillin and only explicit patterns:

- penicillin allergy
- allergic to penicillin
- allergy to penicillin
- not allergic to penicillin
- denies penicillin allergy
- no known allergies
- no known drug allergies

The output is a present/absent assertion with an exact source span. Drug names outside this
vocabulary, uncertain language, family history, cannot-rule-out language, double negation,
malformed Unicode, and unresolved multi-interpretation text abstain safely.

This closed vocabulary gives the test suite a complete semantic contract. It is intentionally
not medication normalization, entity linking, temporal reasoning, or a general medical NLP
engine.

## Why not general clinical NLP

General clinical NLP would require a terminology source, negation and temporality evaluation,
section/context handling, multilingual support, calibration, error review, and a much larger
false-positive/false-negative test set. A regex that appears to pass a demo is not evidence
of safe clinical interpretation. Round 1 therefore uses deterministic extraction plus explicit
abstention, and documents unsupported language rather than guessing.

## Why not trilingual ASR, WhatsApp, or streaming

The current Voice feature is a bounded prerecorded synthetic fixture with prepared transcript
segments. It does not establish ASR inference, speaker diarization, code-switching, Hokkien,
Malay, noisy capture, or real PHI-audio redaction. WhatsApp/SMS delivery and streaming safety
monitoring would add identity, retention, delivery, and real-time correctness boundaries.
They are independent projects and remain deferred.

## What “safety floor” means

The safety floor is a deterministic lower bound on display priority for an internally marked
allergy safety item. The calculation is:

    pre_floor =
        base + recency + explicit risk + unresolved action
        + clinician confirmation + adaptive feedback

    final = clamp(max(pre_floor, safety_floor), 0, 100)

For ordinary highlights, safety_floor is absent and the previous ranking behavior remains.
The ranking explanation records every contribution, pre_floor, safety_floor, whether the
floor was applied, and final.

Round 1 uses 95.0 for an open allergy conflict. This number is an attention policy for the
prototype, not a medical risk probability.

## What the safety floor does not mean

- It is not a diagnosis, severity score, confidence score, or treatment recommendation.
- It does not decide whether the nurse or patient is clinically correct.
- It does not turn an AI/provider response into a trusted source.
- It does not delete, rewrite, or supersede canonical notes by itself.
- It does not prevent a clinician from adjudicating the conflict.
- It does not replace PostgreSQL RLS, application authorization, logging controls, or human review.

The LLM/provider cannot set safety_class or safety_floor. Only the deterministic internal
conflict service and clinician adjudication path may set these fields.

## Phase 2 scope

The backend-only implementation adds:

1. ClinicalAssertion with clinic/patient scope, polarity, closed concept, immutable source
   version, exact code-point offsets, quote hash, verification status, and lifecycle status.
2. ClinicalConflict with deterministic positive/negative pair ordering, versioned clinician
   adjudication, dual provenance, and preserved resolution history.
3. Protected conflict-review Highlight and materialized Glance fields.
4. Ranking pre-floor/floor explanation and protected feedback suppression.
5. Typed internal list/detail/adjudication APIs with server-side patient and clinic checks.
6. Real application tests for extraction, abstention, persistence, conflict lifecycle,
   authorization, stale adjudication, provenance, ranking, and protected feedback.
7. A new 0011 Alembic migration. Older migrations remain unchanged.

Assertion derivation runs after a successful immutable entry version write and outside the
Glance read path. If derivation fails, the human-authored entry remains committed and only a
safe metadata audit status is retained.

## Deferred work

- phone/OTP or magic-link patient onboarding
- PostgreSQL RLS and full tenant-defense-in-depth
- application-wide log sanitization and hosted retention review
- clinic admin onboarding
- multilingual ASR, streaming capture, WhatsApp/SMS delivery
- dosage/medication normalization and patient publication/recall
- impression/exposure logging and learning calibration
- general clinical NLP, embeddings, LLM classification
- frontend UI, Render deployment, Voice changes, DeepSeek calls, and demo work

## Demo narrative

The backend evidence narrative is deliberately modest:

1. Two immutable synthetic records contain different penicillin allergy assertions.
2. The system extracts both exact source spans and opens one protected conflict.
3. Glance keeps the conflict visible with a documented display floor; negative feedback is
   recorded but does not lower the floor or change the clinic preference profile.
4. A clinician sees both immutable sources and adjudicates with expected_version.
5. A stale adjudication returns 409; the attempted resolution code is retained as safe
   metadata, and all original sources remain available.

This does not claim an automated diagnosis or real-clinic safety certification.

## Rollback strategy

The implementation is additive:

- older Alembic revisions are not edited;
- new tables/nullable columns can be removed by the 0011 downgrade in an isolated database;
- canonical entries, EntryVersion records, highlights, and audit rows are not deleted by the
  runtime conflict service;
- the iteration branch can be abandoned without changing local main or the 72h-submission tag;
- no remote push or production database operation is part of this round.

If migration compatibility or source-preservation tests fail, stop at the current checkpoint,
retain the failing evidence, and do not trade away the existing Gate A-C behavior.

## Explicit boundary

Inspired by FHIR semantics for allergy/intolerance and detected-issue style review, but not
FHIR-compliant. This is a closed synthetic vertical slice with no clinical production claim.

# Round 2/10 iteration decision

Baseline: `3ed7be5249c677fdfc4c78d1ad7d6a46b4cfd545`

Round: 2 of 10

Decision: Turn the Round 1 allergy safety slice into an observable, reviewable product path,
without broadening the clinical vocabulary or claiming an unbiased learning system.

## Selected work

1. Add only the new `0012_glance_impressions` migration. Previous migrations, the requirements
   brief, dependency lockfiles, and the 72-hour submission tag remain unchanged.
2. Centralize the Glance candidate snapshot and six-item selection so the read path and exposure
   telemetry share deterministic ordering without writes, provider calls, or ranking recompute.
3. Add an internal, idempotent exposure API that stores candidate rank/surface metadata, safety
   floor metadata, and feature signatures without quote, content, patient name, or risk text.
4. Add an assertion-source endpoint that revalidates exact immutable version, span, quote hash,
   clinic, and patient before returning source data.
5. Make generic highlight Accept/Reject reject protected clinical conflicts; give clinicians a
   separate versioned four-option adjudication path and give Staff equal-weight read-only source
   views.
6. Add the protected Glance card and contextual conflict drawer, then verify desktop/mobile
   source navigation, stale CAS handling, and Patient privacy in a real browser.

## What this round can claim

The local synthetic app now measures which bounded candidates were eligible and surfaced, while
keeping protected safety feedback out of preference learning. It proves exposure data capture and
source/decision integrity for the penicillin slice. It does not claim inverse-propensity scoring,
counterfactual debiasing, calibrated confidence, general clinical NLP, or production compliance.

## Evidence and stop boundary

The local run at application/test checkpoint `803733d` reports 101 backend tests with 89%
coverage, 43 frontend Vitest tests, 16 core Playwright checks across 1440x900 and 390x844, and a
real-TCP SQLite warm-path P95 of 83.045 ms with zero errors. The run also passes Ruff, format,
mypy, pip check, Alembic check, fresh
migration/seed idempotency, frontend lint/format/type-check/build, and source/UI screenshot
review. Round 2 stops before deployment, GitHub push, DeepSeek, Voice changes, patient
publication, video/PDF/ZIP regeneration, RLS, and broad clinical NLP.

# Round 3/10 iteration decision

Baseline: `0530d645b19c6c822e7d90e11dc2cbf7b1a6c96b`

Round: 3 of 10

Decision: Make failure and observability behavior safe, bounded, persistent, and visible while
preserving the existing clinical workspace. The optional external adapter remains opt-in; the
fixture remains the deterministic default.

## Selected work

1. Add only sequential migration `0013_ai_provider_resilience`; keep `0001`-`0012`, dependency
   manifests, requirements brief, and Voice behavior unchanged.
2. Add an allowlisted structured logger, second-layer sanitizer, generic exception boundary, and an
   explicit local log audit script. Logs contain opaque IDs and bounded operational metadata only.
3. Bound the optional provider to 8 seconds per attempt, 12 seconds total, and at most two attempts.
   Retry only transport timeout/connection/transient 5xx; do not silently use the fixture on failure.
4. Persist one circuit per clinic/provider. Three counted failures open it for 60 seconds; one
   CAS-reserved half-open probe either closes it on success or reopens it on failure.
5. Expose an internal provider-status projection and a bilingual degraded-mode panel that keeps
   existing records and navigation usable while new suggestions are unavailable.
6. Verify Scenario E in real browser contexts at desktop/mobile sizes and measure both warm Glance
   and circuit-open fail-fast paths.

## What this round can claim

The local synthetic application now proves redaction-before-provider event ordering, safe local log
handling, bounded provider calls, persistent clinic-scoped circuit transitions, no silent fallback,
and a visible degraded UI. The existing materialized Glance read path is independent of provider
health. The round does not claim a durable job queue, automatic replay, third-party retention
policy, production incident response, or clinical SLA.

## Evidence and stop boundary

The final local run at runtime checkpoint `481db06` and Scenario E test checkpoint `cc99b1c` reports 131 backend tests with 88% coverage, 44
frontend Vitest tests, 18 core Playwright checks across 1440x900 and 390x844, 4 Voice regression
checks, a warm Glance P95 of 70.639 ms with zero errors, and 100 circuit-open submissions with
P95 17.911 ms and zero measured provider calls. Round 3 stops before push, deployment, live
provider calls, Voice changes, patient publication, video/PDF/ZIP work, RLS, and broad clinical
NLP.

# Round 4/10 iteration decision

Baseline: `4faff3448bb6bb5d3825a27d421741a36d8c3044`

Round: 4 of 10

Decision: Implement the patient publication gate for the critical wrong-dosage scenario while
keeping the portal boundary explicit. The product must distinguish an internally accepted AI
suggestion, a patient-facing draft, clinician approval, and a separate portal publish action.

## Selected work

1. Add only sequential migration `0014_patient_publications`; leave migrations `0001`–`0013`,
   `requirements.txt`, dependency lockfiles, Voice, deployment, and existing Entry visibility
   semantics unchanged.
2. Add append-only publication content versions and deterministic source evidence anchored to
   immutable EntryVersion codepoint spans. The supported dosage grammar is deliberately limited
   to synthetic English metformin integer-mg once/twice-daily examples.
3. Enforce server-side Staff/Clinician/Admin/Patient permissions and workflow-version CAS for
   draft edit, approval, publish, recall, correction, and supersession. Store metadata-only
   audit/events; do not add external delivery.
4. Use a typed patient projection instead of flipping internal Entry visibility. Patient output
   contains only current published content or safe withdrawal/correction notices.
5. Add the bilingual internal publication drawer, dosage mismatch warning, explicit publish
   confirmation, correction path, and desktop/mobile Scenario F browser checks.

## What this round can claim

The local synthetic prototype now proves that `Accept is not Publish`, blocks the demonstrated
wrong dosage, requires a clinician to approve and explicitly publish the corrected content, and
preserves source/publication history through recall and correction. The published-care endpoint
met the local real-TCP P95 target with zero errors. The round does not claim external message
delivery, receipt/recall semantics, general medication NLP, FHIR conformance, hosted PostgreSQL
performance, or clinical production safety.

## Evidence and stop boundary

The Round 4 implementation checkpoints are `00f0e927` (backend workflow), `d71946c` (UI and
browser path), and `85f5ff0` (dosage-context hardening). The final local evidence records 175 backend tests with 86% coverage, 45 frontend
Vitest tests, 18 existing Gate B Playwright checks, 4 Voice checks, and 2 Scenario F checks
across 1440x900 and 390x844. A separate 1,000-request published-care benchmark at concurrency
10 measured P95 46.797 ms with zero errors on local SQLite/Uvicorn. The audit status remains
PARTIAL because the dosage grammar is bounded and external delivery is intentionally absent.
Round 4 stops before push, deployment, live LLM calls, Voice changes, video/PDF/ZIP regeneration,
RLS, and broad clinical NLP.

# Round 5/10 iteration decision

Baseline: `2200a891ab82555a78cdef926975c75ff8108ce3`

Round: 5 of 10

Decision: Freeze the Round 1–4 clinical scope and integrate the local implementation into a
reproducible release candidate. This round adds no clinical product feature and does not perform
push, external CI, Render deployment, live provider calls, Voice changes, video, PDF, or ZIP work.

## Selected work

1. Add narrow ignore rules for genuine Round test temp directories, preserving ACL-protected
   directories without taking ownership or performing broad cleanup.
2. Audit the Round 1–4 diff, route/RBAC/data-flow boundaries, patient projection, semantic state
   distinctions, and local-versus-hosted performance claims.
3. Verify fresh/legacy/downgrade disposable SQLite paths through `0014_patient_publications` and
   targeted PostgreSQL offline SQL. Record the pre-existing fresh offline reflection limitation.
4. Replace the stale PostgreSQL workflow that stopped at `0010` with a Python 3.12/PostgreSQL 18
   workflow that covers the current head, publication tables, seed idempotency, tests and static
   quality gates without production credentials.
5. Rehearse the candidate from tracked files in a clean clone and record actual results before
   creating the local `real-clinic-rc1` tag.

## Evidence and stop boundary

The integration audit is [`ROUND5_INTEGRATION_AUDIT.md`](ROUND5_INTEGRATION_AUDIT.md), the route
matrix is [`evidence/round5_route_privacy_audit.md`](evidence/round5_route_privacy_audit.md), and
the scenario/runbook and iteration brief are separate documents. The final primary run records
175 backend tests with 85% coverage, 45 frontend tests, 24 browser checks across both viewports,
Glance P95 113.998 ms, circuit-open P95 27.571 ms, and published-care P95 82.264 ms, all with
zero measured errors. No external PostgreSQL CI run is claimed until Round 6. Existing
real-clinic statuses remain honest: #3, #8, #9, #12, #13, #14, and #15 are PARTIAL; #16 remains
SURVIVES. The round stops before push/deploy and final video/PDF/ZIP regeneration.
