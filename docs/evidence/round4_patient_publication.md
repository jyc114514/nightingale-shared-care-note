# Round 4 patient publication evidence

Result: **PASS WITH DISCLOSED PROTOTYPE BOUNDARY** for the bounded local portal gate.

Round 3 was completed before this round. Round 4 then implemented an explicit patient
publication workflow without editing the old migrations or changing `requirements.txt`.
The selected typed projection keeps internal Entry visibility unchanged.

## Implementation checkpoints

| Area | Checkpoint/evidence |
| --- | --- |
| Design and threat model | [`ROUND4_PATIENT_PUBLICATION_DESIGN.md`](../ROUND4_PATIENT_PUBLICATION_DESIGN.md) |
| Migration/model/service/API | local commit `00f0e927` — `feat: add versioned patient publication workflow` |
| UI, Patient projection, browser flow | local commit `d71946c` — `feat: add clinician publication and patient recall UI` |
| Boundary tests and migration assertions | local commit `c960310` — `test: verify patient publication safety gate` |
| Current migration head | `0014_patient_publications` |
| Requirements hash | `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5` (unchanged) |

## Safety behavior verified

- Staff can prepare a draft but cannot approve or publish.
- A wrong synthetic dosage (`500 mg` immutable source versus `1000 mg` draft) is shown as
  `mismatch`; approval is rejected server-side and the Patient projection remains empty.
- A corrected matching draft requires Clinician approval and a separate explicit publish.
- The Patient projection returns the published content without source/workflow/internal IDs.
- Source change after approval returns a safe `409` and does not publish stale content.
- Recall returns the exact safe withdrawal notice and hides the withdrawn content.
- Correction creates a linked new publication; only its newly published content becomes
  current and the old publication becomes `superseded`.
- Two approval requests with the same workflow version produce one success and one `409`
  with the refreshed latest workflow version.
- Audit records retain actor/action/version metadata; publication content is kept in immutable
  publication-version rows instead of audit fields.
- No external delivery endpoint or provider call was added.

## Automated verification

The local checks were run after implementation:

| Check | Result |
| --- | --- |
| Backend Round 4 publication API tests | 32 passed |
| Backend full regression | 163 passed; 86% coverage |
| Ruff check/format and mypy `app tests` | passed |
| Frontend Vitest | 45 passed |
| Frontend ESLint/Prettier/type-check | passed |
| Existing Gate B Playwright | 18 passed at 1440×900 and 390×844 |
| Existing Voice Playwright | 4 passed at 1440×900 and 390×844 |
| Scenario F publication Playwright | 2 passed at 1440×900 and 390×844 |
| Published-care warm path | 50 warm-up + 1,000 real-TCP requests, concurrency 10, 0 errors |
| Published-care P95 | 47.665 ms (local SQLite/Uvicorn approximation) |

Machine-readable benchmark data is in
[`round4_patient_publication_p95.json`](round4_patient_publication_p95.json). It is not
hosted PostgreSQL performance evidence.

## Boundary and limitations

The Round 4 audit status remains **PARTIAL**: this proves an explicit portal gate for a
small synthetic metformin dosage grammar, not external delivery, delivery receipts,
external recall, general medication NLP, FHIR conformance, production retention, or a
clinical safety certification. PDF/ZIP/video artifacts were intentionally not regenerated
in this round.
