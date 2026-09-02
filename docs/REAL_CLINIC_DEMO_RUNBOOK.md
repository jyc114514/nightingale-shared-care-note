# Real-clinic iteration demo runbook

Target length: 3–5 minutes. Use only the existing synthetic seed. This runbook is for a local or
already prepared evaluation environment; it does not reset a production database and does not
record a new video.

## Setup and safety

1. Start the existing demo launcher with a local-only password, or use an already prepared local
   database at Alembic head `0014_patient_publications`.
2. Confirm the page shows the synthetic Sarah Tan patient and the role label. Keep the browser at
   a real desktop or mobile viewport; the Preview control is only for layout self-checking.
3. Do not enter real patient data, use live DeepSeek, reprocess Voice, or click write controls
   during the primary Scenario 13/15 path unless you intentionally want a disposable state change.

## Primary path — Scenario 13/15: safety cannot be learned away

### Staff view

1. Sign in as `staff.a@clinic-a.test` and select Sarah Tan.
2. In Glance View, find the card labelled **Conflicting allergy information**.
3. Open **Why is this here?** and point to **Minimum display priority** and **Minimum applied**.
4. Click **Pin** once. Explain that protected feedback is recorded but does not train ordinary
   preference ranking while the conflict is unresolved.
5. Click **Review conflict**. Read the two sides: reported penicillin allergy and no known drug
   allergies.
6. Click **View source** on both sides. Show that the selected timeline source, immutable version,
   and exact span change together.
7. Point out that Staff has no clinical adjudication button.

### Clinician view

1. Sign out and sign in as `clinician.a@clinic-a.test`.
2. Open the same conflict, select **Need more information**, and record the decision.
3. Explain that the derived conflict state changes, while both original sources remain intact.
4. If demonstrating concurrency, use a second Clinician browser and submit the same displayed
   conflict version once. Show one success and one stale `409`; do not replay the stale request.

## Secondary optional path — Scenario 12: Accept is not Publish

1. From an internal source, choose **Prepare patient update**.
2. Show the immutable source `Continue metformin 500 mg twice daily.`.
3. In the draft, enter `Take metformin 1000 mg twice daily.` and save. Show **Mismatch** and the
   disabled/blocked approval state. Explain that an accepted AI highlight is still not a publish.
4. As Clinician, correct the draft to `Take metformin 500 mg twice daily.`, save, click
   **Approve for portal**, then click **Publish to patient portal** and confirm.
5. Switch to Patient. Show only the exact published update; do not claim that it was emailed or
   read.
6. As Clinician, withdraw it with a safe reason. Patient should see only the safe withdrawal notice.
7. Create a correction draft, approve and explicitly publish it. Explain that the old publication
   becomes superseded and the corrected update is current.

## Talking points and forbidden claims

- Say: “This is a synthetic, portal-only prototype with explicit source and human approval.”
- Say: “The ranking is an attention policy, not a medical risk score; protected safety attention
  is separate.”
- Say: “The Voice path is prerecorded synthetic audio with a prepared transcript, not ASR.”
- Do not say that the system diagnoses allergy, learns fairness, delivers messages, provides
  receipts, recalls an external message, is FHIR compliant, or is clinically production ready.
- Do not claim PostgreSQL passed until Round 6 external CI actually runs.

## Reset/rollback

For a local demo, stop the launcher and use a new disposable SQLite database or the documented
seed path. Do not run downgrade against a user or hosted database. A publication downgrade drops
publication tables and is only a disposable migration test. Do not delete source history to make
the demo look pristine.
