# Round 2/10 conflict UI and Glance exposure evidence

Date: 2026-09-01

Application/test checkpoint: `803733d`

Result: **PASS for the bounded local synthetic iteration**.

This evidence covers the Round 2 source-anchored allergy conflict path and metadata-only Glance
exposure capture. It is not a claim of general clinical NLP, unbiased learning, hosted PostgreSQL,
or production clinical safety.

## Scope delivered

- Alembic `0012_glance_impressions` adds append-only batch/item metadata tables. Migrations `0001`
  through `0011` were not edited.
- `build_glance_candidates()` is the shared provider-free read snapshot used by both `GET
  /patients/{patient_id}/glance` and impression capture. It keeps the six-item product cap and
  stores at most 500 candidates per impression.
- `POST /patients/{patient_id}/glance-impressions` is clinic/internal scoped, idempotent, and
  validates the requested limit, duplicate surfaced resources, candidate membership, and payload
  reuse. `GET /patients/{patient_id}/glance-impressions/summary` returns feature and safety
  aggregates without quote, content, risk text, or patient name.
- `GET /clinical-assertions/{assertion_id}/source` revalidates the assertion's clinic/patient,
  immutable entry version, exact Unicode-codepoint span, quote hash, and offset unit. Corrupt
  provenance returns one generic verification error; it never returns the forged quote.
- Protected allergy conflicts have a separate dual-source drawer. Staff can inspect both sides but
  cannot record a decision. Clinicians have four resolution choices with a versioned database CAS;
  a stale submission stays open, refreshes the latest detail, and is not replayed automatically.
- Protected cards show the product labels `Conflicting allergy information`, `Needs clinician
  review`, and `Protected attention`. Generic Accept/Reject controls are absent. Ranking details
  distinguish pre-floor, minimum display priority, whether the minimum was applied, and final
  display priority; the UI says this is not a medical risk score.
- The post-render frontend impression effect is one opaque snapshot per unchanged candidate
  signature. It is non-blocking, does not run on the GET endpoint, and does not retry a failed
  telemetry write in a loop.

## Verification

| Check | Observed result |
| --- | --- |
| Backend application suite | 101 passed, 89% coverage |
| Ruff | `ruff check --no-cache app tests` passed |
| Ruff format | 115 files already formatted |
| mypy | `mypy app tests` passed with no issues |
| Dependencies | `pip check` reported no broken requirements |
| Alembic | `alembic check` reported no new upgrade operations |
| Fresh migration/seed | `0001` -> `0012`, seed twice: stable 9 entries, 6 highlights, 6 Glance items |
| Frontend unit | 43 Vitest tests passed |
| Frontend static/build | Prettier, TypeScript, ESLint, and Vite build passed |
| Browser workflows | 16 Playwright checks passed: 8 at 1440x900 and 8 at 390x844 |
| Warm path | 50 warm-up + 1,000 real-TCP requests at concurrency 10, zero errors; P50 64.165 ms, P95 83.045 ms, P99 99.848 ms, max 137.349 ms |

The browser Scenario D specifically verified both source-side buttons, exact quotes `penicillin
allergy` and `no known drug allergies`, source replacement, Staff read-only behavior, protected
feedback notice, two-clinician same-version competition with one visible `409`, refreshed latest
conflict state, and Patient UI/API denial. The screenshots are local generated evidence:

- [Desktop conflict drawer](../../artifacts/gate-b/desktop-1440-scenario-d-conflict-drawer.png)
- [Desktop 409 state](../../artifacts/gate-b/desktop-1440-scenario-d-conflict-409.png)
- [Desktop Patient privacy](../../artifacts/gate-b/desktop-1440-scenario-d-patient-privacy.png)
- [Mobile conflict drawer](../../artifacts/gate-b/mobile-390-scenario-d-conflict-drawer.png)
- [Mobile 409 state](../../artifacts/gate-b/mobile-390-scenario-d-conflict-409.png)
- [Mobile Patient privacy](../../artifacts/gate-b/mobile-390-scenario-d-patient-privacy.png)

## Data boundary and limitations

The seed uses only synthetic Clinic A records: a staff note containing `penicillin allergy` and a
system-authored patient-session summary containing `no known drug allergies`. Clinic B has no
matching conflict. The assertion vocabulary is deliberately limited to explicit penicillin
patterns and safe abstention. It does not infer general medications, diagnosis, temporality,
multilingual meaning, or clinical truth.

Impressions measure the eligible/surfaced denominator and preserve protected safety metadata, but
they do not implement inverse-propensity scoring, counterfactual correction, exposure duration,
calibration, or unbiased self-learning. `safety_floor=95.0` is an attention policy, not a medical
risk probability.

Patient-facing APIs remain unchanged: the patient projection excludes internal conflict/assertion/
impression records, and direct protected endpoints are denied. No external provider, DeepSeek call,
Voice change, deployment, GitHub push, video/PDF/ZIP regeneration, or PostgreSQL claim is part of
this evidence.
