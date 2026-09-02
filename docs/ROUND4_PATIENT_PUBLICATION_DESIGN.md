# Round 4 patient publication gate design

Status: local implementation design for Round 4/10. This document defines a bounded,
synthetic portal publication workflow. It is not a claim of FHIR compliance, clinical
production readiness, general medication NLP, or external notification delivery.

## Decision and safety thesis

Accept is not Publish.

An AI highlight may be accepted as an internal review decision. That decision never
creates a patient-facing record. A separate patient-publication draft must be prepared,
checked against an immutable source version, approved by a clinician, and explicitly
published to the portal. The portal projection is typed and state-filtered; it does not
flip an internal Entry's visibility and does not expose raw AI history, draft history,
source IDs, or validation internals to a patient.

The implementation is intentionally portal-only. Email, SMS, WhatsApp, push delivery,
delivery receipts, external recall, and communication-provider integrations are not
implemented in this round.

## Threat model

The gate is designed against these concrete failure modes:

- an accepted AI suggestion is mistaken for permission to publish;
- a staff-authored or AI-authored internal note is exposed by changing Entry visibility;
- a medication dosage is silently copied, normalized, translated, or converted;
- a draft is approved against one source version and published after that source changes;
- a stale approval or publish request overwrites a newer workflow transition;
- a recall or correction silently edits history or leaves old content active;
- a patient response contains internal comments, raw AI text, workflow state, evidence,
  or internal identifiers;
- audit records or logs contain the patient's free text or credential material.

The controls are server-side authorization, immutable source/version references, immutable
publication content snapshots, deterministic dosage evidence, workflow-version CAS,
metadata-only audit events, and a patient projection that selects only the current
published state.

## State machine

```text
DRAFT --clinician approve--> CLINICIAN_APPROVED --explicit publish--> PUBLISHED
  |                                  |                                  |
  | edit                             | source changed                  | recall
  v                                  v                                  v
DRAFT                         blocked/review required              RECALLED

PUBLISHED --corrected publication published--> SUPERSEDED
any unpublished state --entered in error--> ENTERED_IN_ERROR
```

- `DRAFT` is internal, editable through new immutable content versions, and never
  patient-visible.
- `CLINICIAN_APPROVED` binds the exact current draft content version and source version.
  Editing the draft returns it to `DRAFT`; a source-version change blocks publication.
- `PUBLISHED` is an explicit clinician action. The portal exposes the exact approved
  content version only. No external message is sent.
- `RECALLED` withdraws portal content immediately while retaining internal history and
  a safe withdrawal notice. There is no external delivery to recall.
- `SUPERSEDED` is the historical state of an older publication after a linked corrected
  publication is explicitly published.
- `ENTERED_IN_ERROR` is internal audit state. If the item had been published, the portal
  shows only the safe withdrawal notice; otherwise the patient sees nothing.

## Data and provenance

`patient_publications` is the workflow/state record. It stores clinic and patient scope,
the source Entry and immutable EntryVersion, state, severity, content/workflow versions,
actor metadata, timestamps, and correction links. `published_entry_id` remains nullable
because this round uses the typed publication projection rather than generating or
mutating a normal Entry.

`patient_publication_versions` is append-only. Every draft edit creates a new content
snapshot with SHA-256; old snapshots are never updated or deleted.

`patient_publication_evidence` stores deterministic source evidence only: exact immutable
source version, Unicode-codepoint offsets, quote and hash, dosage concept/value/unit/
frequency, and validation status. No LLM creates or adjudicates dosage evidence.

The bounded dosage slice supports only the synthetic English form `metformin`, integer
`mg`, and `once daily` or `twice daily`, for example:

```text
Continue metformin 500 mg twice daily.
```

Ranges, PRN, tapers, route changes, multiple medications/doses, decimal conversion,
micrograms, insulin units, multilingual or fuzzy names, and ambiguous grammar abstain.
The wrong draft `Take metformin 1000 mg twice daily.` is `mismatch` and cannot be
approved or published. The corrected draft `Take metformin 500 mg twice daily.` is
`matched` and still requires clinician approval and explicit publication.

This design follows the general trust/provenance ideas represented by selected FHIR
Provenance, DocumentReference status, and Communication concepts, but the application
is not FHIR-compliant and does not claim a FHIR resource mapping.

## Roles and permissions

| Actor | Internal draft/read | Edit draft | Approve | Publish | Recall/correct | Patient projection |
|---|---:|---:|---:|---:|---:|---:|
| Staff | yes | yes | no | no | no | scoped internal only |
| Clinician | yes | yes | yes | yes | yes | scoped internal and portal review |
| Admin | read-only oversight | no | no | no | no | scoped read-only |
| Patient | no | no | no | no | no | own current published projection only |

All checks are enforced by the API. UI controls are explanatory affordances, not the
authorization boundary.

## Approval, publication, recall, and correction

Approval requires the expected workflow version, a draft state, valid current evidence,
and an unchanged source current version. Publication repeats the source/version and exact
approved-content checks, then changes state in one transaction. A stale request returns
`409` and never replays the transition.

Recall accepts a closed reason code (`dosage_error`, `clinical_correction`,
`entered_in_error`, or `other_safe_code`) and never stores a free-text PHI reason. The
patient projection contains exactly the safe withdrawal notice, not the withdrawn text.

A correction is a linked new draft. It follows the same evidence, approval, and explicit
publish gates. Only after corrected publication succeeds is the old publication marked
`SUPERSEDED`; the patient projection then contains the corrected current update and a
safe correction notice. No silent edit or destructive history operation occurs.

## Failure and retention boundaries

Source changes, dosage mismatch/ambiguity, missing evidence for a dosage source, invalid
workflow versions, cross-clinic access, and forbidden roles fail closed. Publication
history, source references, content hashes, and audit metadata are retained locally for
review; this prototype does not define a production retention schedule, legal hold,
patient-notification policy, or external delivery guarantee.

## Explicit limitations

- Synthetic data only; no clinical production claim.
- Portal publication only; no external delivery or delivery receipt.
- Bounded deterministic metformin dosage slice; no general medication NLP.
- Selected FHIR semantics are conceptual references, not a conformance statement.
- Patient projection is a typed application response and is not a complete FHIR export.
- Round 4 does not change old migrations, product requirements, Voice, live LLM calls,
  deployment, video, PDF, or ZIP artifacts.
