# Round 1 backend safety evidence

Date: 2026-09-01

Baseline: 573f897a69864707f64b1846b2802a2674f69597

Branch: codex/real-clinic-safety

Baseline tag: 72h-submission

Migration: 0011_real_clinic_safety, additive child of 0010_postgres_compat

## Implemented scope

This checkpoint implements one closed synthetic safety vertical slice:

    immutable EntryVersion
      -> deterministic penicillin assertion extraction
      -> exact source-anchored ClinicalAssertion
      -> active same-patient assertion comparison
      -> ClinicalConflict with dual provenance
      -> protected Glance highlight
      -> deterministic display safety floor
      -> clinician versioned adjudication

Assertion derivation runs after a successful EntryVersion write and is not part of the
Glance read path. If derivation raises an infrastructure error, the canonical entry remains
committed and only a metadata-only failure audit row is written.

## Closed vocabulary and abstention

Accepted explicit phrases are:

- penicillin allergy
- allergic to penicillin
- allergy to penicillin
- not allergic to penicillin
- denies penicillin allergy
- no known allergies
- no known drug allergies

The extractor returns Python Unicode-codepoint offsets, the exact quote, offset unit, and
SHA-256 quote hash. Repeated occurrences retain their occurrence-specific offsets.

The extractor safely abstains with an enumerated reason for:

- possible, suspected, or cannot-rule-out language
- family/past/previous/remote history language
- double negation or multiple polarity interpretations
- unsupported substances
- malformed Unicode or invalid spans

No raw text is written to assertion/conflict audit rows.

## Conflict rules and lifecycle

Only active allergy assertions for the same clinic and patient are compared. Round 1 opens
one deterministic pair for:

- present(penicillin) versus absent(penicillin)
- present(penicillin) versus absent(all_drug_allergies)

The positive assertion is the primary Glance span. The ClinicalConflict response contains
both assertion records, each with its own immutable source entry/version, exact quote,
offsets, role and verification status. Pair ordering is positive first and negative second.
Existing pairs are idempotent; no duplicate conflict is opened.

New entry versions supersede derived assertions from the previous version without deleting
the old assertion, source version, entry, or provenance. An inactive conflict is marked
superseded, never silently adjudicated.

Clinicians use:

- GET /patients/{patient_id}/clinical-conflicts
- GET /clinical-conflicts/{conflict_id}
- PATCH /clinical-conflicts/{conflict_id}/adjudicate

Staff can read internal conflict details but cannot adjudicate. Patients are denied. Foreign
clinic access resolves as not found. Adjudication uses expected_version and returns 409 for
a stale open conflict; the attempted resolution is retained only as a safe audit action
and response metadata.

Resolution behavior:

- confirmed_present confirms the positive assertion, refutes the negative, and keeps a
  protected confirmed-allergy Glance item.
- confirmed_absent confirms the negative, refutes the positive, and supersedes the
  conflict Glance item.
- needs_more_information keeps the conflict open and the floor protected.
- entered_in_error updates both assertion verification states and supersedes the conflict
  Glance item; canonical sources remain.

## Safety floor and feedback

For every highlight:

    pre_floor =
        base + recency + explicit risk + unresolved action
        + clinician confirmation + adaptive feedback

    final = clamp(max(pre_floor, safety_floor), 0, 100)

Ordinary highlights have no safety floor and retain the previous bounded adaptive behavior.
Open allergy conflicts use safety_class=allergy_conflict and safety_floor=95.0. A clinician
confirmed allergy item uses safety_class=confirmed_allergy and the same documented floor.
The floor is an attention policy, not a medical risk probability, diagnosis, confidence
score, or treatment recommendation. Provider/API payloads cannot set it.

Feedback against a protected safety highlight is still appended and audited, but records
applied_to_profile=false and suppression_reason=protected_safety_class. It does not create
or change an importance profile and cannot lower the projected final priority below the
floor. Ordinary feedback remains clinic-scoped, idempotent, and bounded to plus/minus 12.

## Verification

Backend environment: existing ai_env, Python 3.10.20. No dependency manifest was changed.

- Targeted assertion/conflict tests: 20 passed.
- Full backend suite: 101 passed.
- Coverage: 89% total with pytest --cov=app.
- Ruff check: passed for app, tests, and migrations.
- Ruff format check: passed for app, tests, and migrations.
- mypy app tests: passed with no issues in 108 source files.
- pip check: passed with no broken requirements.
- Fresh Alembic SQLite upgrade through 0011: passed.
- Alembic current: 0011_real_clinic_safety (head).
- Alembic check: no new upgrade operations detected.
- Migration downgrade/re-upgrade and legacy index repair tests: passed.
- Synthetic seed twice-run smoke: stable counts of 2 clinics, 5 users, 2 patients, 7
  entries, 2 comments, 5 highlights, 5 Glance items, 1 archival summary, and 2 archival
  sources.
- Existing frontend lint, type-check, and production build: passed; frontend was not
  modified.
- requirements.txt SHA-256 unchanged:
  4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5
- High-confidence working-tree secret scan: 0 hits.
- MP4: expected original recording remains untracked and unstaged.
- No listener remained on ports 8000, 8010, or 5173 at the final check.

The pytest command used the repository-local isolated basetemp because the managed Windows
host denied access to its default user pytest directory. This changed only test-artifact
location, not test behavior.

## Failures encountered and repairs

The first SQLite migration smoke failed while removing the temporary Boolean server default
with ALTER COLUMN DROP DEFAULT, which SQLite does not support. The migration now removes
that default only on PostgreSQL; SQLite retains the harmless migration-time default. The
fresh upgrade, downgrade/re-upgrade, legacy repair, and Alembic check then passed.

The initial pytest invocation was blocked before fixture setup by system temporary-directory
permissions. Re-running with a dedicated repository-local basetemp allowed the actual suite
to execute and pass.

## Known limitations

- This round did not connect to a PostgreSQL service or the production Render database.
  The migration is tested on SQLite and uses portable additive operations; PostgreSQL
  deployment verification remains a separate gate.
- The assertion vocabulary is intentionally penicillin-only and English phrase-only. It is
  not general clinical NLP, medication normalization, multilingual reasoning, or a diagnosis
  engine.
- There is no application-wide logging sanitizer, impression/exposure denominator, or
  learning calibration in this round.
- PostgreSQL RLS, patient identity onboarding, notification delivery, dosage publication/
  recall, streaming ASR, Voice, DeepSeek, frontend UI, and deployment are unchanged and
  deferred.
- The protected floor does not determine clinical truth; a clinician must adjudicate.

## Next Round 2 recommendation

After this local checkpoint is reviewed, the smallest next priority is a backend/API and UI
surface for dual-source conflict interaction plus explicit impression logging. Keep the
allergy vocabulary closed until a labeled evaluation set and a broader terminology policy
exist. Do not expand to streaming ASR or generic clinical NLP before the tenant, logging,
and publication boundaries are separately evidenced.
