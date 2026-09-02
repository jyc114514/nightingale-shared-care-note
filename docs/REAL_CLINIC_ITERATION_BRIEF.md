# Real-clinic iteration brief — Round 1–5 release candidate

## 1. Baseline first break

The original synthetic prototype had useful immutable Entry snapshots and role-scoped patient
projection, but the adversarial real-clinic scenarios exposed a gap between technical review
controls and clinical trust: free-text allergy contradictions were not semantic assertions,
Glance exposure was not measurable, provider failure could look like an ordinary error, and an
accepted suggestion had no separate patient publication/correction boundary.

## 2. Scope decision

Rounds 1–4 selected narrow vertical slices instead of broad clinical NLP: penicillin assertion
conflict, protected attention/exposure metadata, safe provider failure, and a metformin dosage
publication gate. Round 5 adds no clinical feature. It integrates these slices, verifies migration
compatibility, prepares PostgreSQL CI, and rehearses the candidate from tracked files.

## 3. Architecture changes

- Immutable `entry_versions` remain the source-of-truth graph.
- Clinical assertions and conflicts are derived, source-anchored, and separately adjudicated.
- Glance reads materialized candidates; impressions store metadata, not note text.
- Provider calls are redaction-first, bounded, circuit-protected, and opt-in; fixture remains the
  stable default.
- Patient publication uses `patient_publications`, append-only publication content versions, and
  deterministic source evidence. It is a typed portal projection, not an Entry visibility flip.
- Patient projection excludes internal comments, raw AI, workflow/source IDs, evidence/history,
  and provider status.

## 4. Evidence

The candidate has 175 backend tests with 86% coverage, 45 frontend Vitest tests, 18 existing Gate
B browser checks, 4 Voice checks, and 2 Scenario F checks across desktop/mobile viewports. Fresh
and four legacy SQLite paths reach `0014`; disposable downgrade/re-upgrade and targeted
PostgreSQL offline SQL pass. The published-care local real-TCP benchmark is 1,000 requests at
concurrency 10 with zero errors and P95 46.797 ms. These are local synthetic measurements, not
hosted PostgreSQL performance or clinical validation.

## 5. Failure and abstention

The candidate blocks source-version drift, stale workflow updates, wrong dosage, ambiguous or
unsupported dosage grammar, cross-clinic access, forbidden roles, and raw patient projection
leakage. It does not guess dose conversions, interpret general medication language, or silently
fallback from a failed external provider to a fixture result.

## 6. Remaining DOES NOT/PARTIAL/SURVIVES

- #3 PHI beyond model redaction: PARTIAL; local logging is hardened, external retention is unknown.
- #8 model hangs: PARTIAL; request/provider bounds exist, no durable queue.
- #9 provider outage: PARTIAL; persistent circuit/degraded UI exists, no durable replay.
- #12 wrong dosage: PARTIAL; bounded synthetic metformin portal gate, no external delivery/receipt.
- #13 allergy contradiction: PARTIAL; bounded penicillin slice, not general semantic NLP.
- #14 risk/confidence/importance: PARTIAL; explicit risk/priority/safety floor are not clinical
  probabilities.
- #15 exposure bias/fatigue: PARTIAL; impression metadata exists, no debiasing or fatigue study.
- #16 edited source provenance: SURVIVES under the immutable version/span contract.

## 7. Deployment status

The existing Render deployment evidence remains historical and was not changed by Round 5. No
Render resource, production database, GitHub remote, or external CI run was touched. The prepared
`.github/workflows/real-clinic-postgres.yml` requires Round 6 external authorization to execute.

## 8. Explicit non-claims

This is not a clinical production system, FHIR-conformant implementation, medication NLP service,
ASR/diarization system, external communication service, or hosted PostgreSQL performance report.
The brief is an iteration/release-candidate record, not a replacement for the earlier Technical
Brief.
