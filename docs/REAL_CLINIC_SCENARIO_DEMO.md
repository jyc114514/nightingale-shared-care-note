# Real-clinic scenario demo draft

This is a local synthetic rehearsal path for the Round 2 safety slice. It is intended to make the
trust boundary visible to a reviewer; it is not a clinical protocol and is not the final recording
script.

## Data prepared by the seed

Clinic A / Sarah Tan contains two independent records:

1. Staff note: `Patient reports a penicillin allergy.` The extracted source span is `penicillin
   allergy`.
2. Patient-session summary: `I have no known drug allergies.` The extracted source span is `no
   known drug allergies`.

The two exact immutable sources form one open allergy conflict. Clinic B has no corresponding
conflict. The Glance view remains capped at six items.

## Reviewer path

### Staff — inspect, do not adjudicate

1. Log in as the synthetic Staff persona and open Sarah Tan.
2. Find the card labelled `Conflicting allergy information`.
3. Open `Why is this here?` and show `Minimum display priority` and `Minimum applied`.
4. Click `Pin`; explain that unresolved protected feedback is retained but does not train ordinary
   preference ranking.
5. Click `Review conflict`.
6. Read both equally weighted sides: `Allergy reported` and `Allergy denied`.
7. Click `View source` on each side. Confirm that the selected source and exact highlighted span
   change to the corresponding immutable timeline record.
8. Point out that Staff has no `Record clinical decision` control.

### Clinician — record through a versioned decision

1. Log in as the synthetic Clinician persona and reopen the same conflict.
2. Choose `Need more information` and record the decision. Explain that this keeps the conflict
   protected because the two sources have not been silently rewritten.
3. In a second Clinician browser, submit the same displayed conflict version once more.
4. Show that exactly one write succeeds and the other remains in the drawer with a stale `409`
   message and refreshed latest version. Do not replay the stale decision automatically.

### Patient — privacy projection

1. Log in as the synthetic Patient persona.
2. Show the patient-facing summary and instruction only.
3. Confirm that conflict labels, assertion text, internal Glance data, and impression data are not
   in the UI. Direct protected endpoints return `403`.

## Claims allowed in a demo

- The prototype detects one explicit, closed-vocabulary penicillin contradiction in synthetic data.
- Both sides remain linked to immutable source versions and exact spans.
- Staff can review but cannot adjudicate; Clinician decisions use optimistic concurrency.
- Glance exposure is recorded as metadata to support future evaluation.
- The safety floor is an attention policy, not a diagnosis, risk probability, or unbiased-learning
  solution.

## Claims intentionally excluded

Do not describe this slice as general clinical NLP, allergy diagnosis, calibrated confidence,
inverse-propensity correction, production compliance, ASR/Voice inference, live DeepSeek output,
or hosted PostgreSQL evidence. Do not expose the patient-session internal source to the Patient
persona.

## Scenario 12 — Wrong patient-facing dosage

Round 4 adds a separate portal publication gate for this bounded synthetic case. The source is
the internal note `Continue metformin 500 mg twice daily.` Staff can prepare the patient-facing
draft, but the intentionally wrong `Take metformin 1000 mg twice daily.` is visibly marked
`mismatch`; the API rejects approval and the Patient sees nothing.

The safe demonstration path is:

1. Staff opens the source and prepares the update. Show the immutable source version and dosage
   evidence; do not describe this as accepting or publishing an AI suggestion.
2. Clinician edits the draft to `Take metformin 500 mg twice daily.`, saves the new immutable
   draft version, and clicks `Approve for portal`.
3. Clinician performs the separate `Publish to patient portal` confirmation. The Patient sees
   the exact published content, while the internal source remains unchanged.
4. Clinician can withdraw it with a safe reason code. The Patient then sees only the safe
   withdrawal notice; the old content remains internal history.
5. Clinician creates a linked correction draft, approves it, and explicitly publishes it. The
   old publication becomes superseded and the Patient sees only the corrected current update.

The workflow uses the typed publication projection rather than flipping an internal Entry's
visibility. It is portal-only: no email, SMS, WhatsApp, push delivery, delivery receipt,
external recall, general medication NLP, or FHIR conformance is claimed. See
[`PATIENT_PUBLICATION_BOUNDARY.md`](PATIENT_PUBLICATION_BOUNDARY.md) for the exact role and
state boundary.
