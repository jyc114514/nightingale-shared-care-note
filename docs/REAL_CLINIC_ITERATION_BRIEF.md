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

The candidate has 175 backend tests with 85% coverage, 45 frontend Vitest tests, 18 existing Gate
B browser checks, 4 Voice checks, and 2 Scenario F checks across desktop/mobile viewports. Fresh
and four legacy SQLite paths reach `0014`; disposable downgrade/re-upgrade and targeted
PostgreSQL offline SQL pass. The published-care local real-TCP benchmark is 1,000 requests at
concurrency 10 with zero errors and P95 82.264 ms in the Round 5 comparable run. These are local synthetic measurements, not
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

## Round 9 production recovery addendum — 2026-09-03

Round 9 addressed a production logging regression before the existing Render service was updated.
The old sanitizer consumed the parameterized `LogRecord.args` tuple that Uvicorn's
`AccessFormatter` needs, which caused formatter failures for ordinary access lines. A real
formatter regression test was committed red at `f72593c`; the narrow repair was committed at
`43714a5` and preserves formatter-compatible access arguments while redacting query values and
failing closed on sanitizer errors.

The exact repair source `c6e9851288c745ceb66dad32078d1385ffbe3424` passed PostgreSQL 18 CI run
`33650978171`, including the full migration/seed/schema checks, the pinned bridge probe, backend
tests, and static gates. Main was fast-forwarded and the existing Render service deployed that
same commit once: deploy `dep-dac4dgek1f9s73e4qu30`. HTTPS, anonymous auth boundaries, Staff/
Clinician/Patient canaries, and a 15/15 sustained asset watch passed. Auto-Deploy remains disabled
for controlled release.

The current evidence is deliberately partial. The hosted authenticated read-path benchmark was
not run because no safe browser request surface was available without extracting cookies or
tokens. The production Glance top-six was also affected by accumulated synthetic rehearsal state,
so protected allergy/publication controls were not claimed as live-canary passes. No production
cleanup was used to manufacture them. See [`round9_render_live.md`](evidence/round9_render_live.md)
and [`round9_hosted_performance.md`](evidence/round9_hosted_performance.md).

The local iteration demo is a separate, disposable synthetic artifact at
`deliverables/iteration/Nightingale_Real_Clinic_Iteration_Demo.webm` and is intentionally kept out
of GitHub; its browser-based QA and the unavailability of `ffprobe`/`ffmpeg` are recorded in
[`round9_demo_qa.md`](evidence/round9_demo_qa.md). The original user-supplied MP4 was not opened,
transformed, moved, renamed, or uploaded.
