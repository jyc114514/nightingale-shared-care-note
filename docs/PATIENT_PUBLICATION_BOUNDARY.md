# Patient publication boundary

Nightingale treats an accepted suggestion and a patient publication as different safety
decisions:

```text
internal AI/manual source
        ↓ prepare draft
      DRAFT  -- edit → new immutable content version
        ↓ clinician approval
CLINICIAN_APPROVED
        ↓ explicit clinician publish
     PUBLISHED → patient portal projection
        ↓ recall                 ↓ corrected publication published
     RECALLED                  SUPERSEDED
```

## What the prototype guarantees locally

- AI entries remain internal suggestions. Generic highlight `Accept` does not create a
  patient publication.
- Staff can prepare and edit a draft. Staff cannot approve, publish, recall, or correct.
- A Clinician must approve the exact draft content version and then perform a separate
  explicit publish action.
- Approval and publish are blocked when the selected immutable source has changed or when
  the bounded medication dosage evidence is mismatch, ambiguous, unsupported, or missing
  for a dosage-bearing source.
- Draft edits append immutable publication content versions and invalidate approval.
- Recall removes patient content and leaves only the safe withdrawal notice. Correction is
  a linked new draft, not a silent edit; it must pass the same approval and publish gates.
- Patient responses contain only current published content or safe notices. They do not
  contain internal source text, comments, raw AI notes, evidence, workflow states, or
  internal identifiers. Legacy patient-facing summaries/instructions remain available.
- Audit rows and collaboration events contain actor/state metadata only; publication
  content is not copied into audit metadata.

## Bounded dosage evidence

The deterministic slice recognizes only synthetic English `metformin`, an integer `mg`
quantity, and `once daily` or `twice daily`, with exact Unicode-codepoint source offsets.
For example, `Continue metformin 500 mg twice daily.` can support a matching draft. A
draft containing `metformin 1000 mg twice daily` is a visible mismatch and cannot advance.
Ranges, PRN/taper/route changes, multiple doses or medications, decimal/unit conversion,
insulin units, multilingual text, and fuzzy drug names abstain.

## API surface

Internal workflow endpoints are:

- `POST /entries/{source_entry_id}/patient-publications`
- `GET /patients/{patient_id}/patient-publications`
- `GET /patient-publications/{publication_id}`
- `PATCH /patient-publications/{publication_id}`
- `POST /patient-publications/{publication_id}/approve`
- `POST /patient-publications/{publication_id}/publish`
- `POST /patient-publications/{publication_id}/recall`
- `POST /patient-publications/{publication_id}/corrections`

The patient-safe projection is:

- `GET /patients/{patient_id}/published-care`

All role, clinic, source, state, and workflow-version checks are server-side. The database
schema is added only in migration `0014_patient_publications`; migrations `0001`–`0013`
are unchanged.

## Deliberate non-goals

This is a synthetic, portal-only prototype. It does not implement email/SMS/WhatsApp/push
delivery, delivery receipts, external recall, medication-normalization coverage, general
clinical NLP, FHIR conformance, production retention policy, or a clinical production claim.
