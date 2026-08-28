# Nightingale judge access

## Links

- Live application: https://nightingale-shared-care-note.onrender.com
- GitHub repository: https://github.com/jyc114514/nightingale-shared-care-note

## Demo accounts

All accounts below are synthetic seed personas in the Clinic A/Clinic B demo boundary.

| Email | Role | Persona / scope |
| --- | --- | --- |
| `staff.a@clinic-a.test` | Staff | Staff A · Clinic A |
| `clinician.a@clinic-a.test` | Clinician | Clinician A · Clinic A |
| `sarah.patient@clinic-a.test` | Patient | Sarah Patient · linked to Sarah Tan |
| `admin.a@clinic-a.test` | Admin | Admin A · Clinic A, read-only product path |
| `staff.b@clinic-b.test` | Staff | Staff B · separate Clinic B scope |

Demo password: provided separately in the submission email.

## Recommended review order

1. Sign in as `staff.a@clinic-a.test` and select **Sarah Tan**.
2. Review Glance View, source/provenance, Voice fixture, Comments, mentions, and task entry points.
3. Sign out outside the recording and sign in as `clinician.a@clinic-a.test`.
4. Review task lifecycle, AI suggestion review, History, Compare, Revert, and historical context.
5. Sign out outside the recording and sign in as `sarah.patient@clinic-a.test`.
6. Confirm that the Patient view contains only patient-facing records and Voice content.

The application defaults to English; the application chrome can also be switched to Simplified
Chinese. Sarah Tan and Jordan Lim are synthetic demo patients. The first request to the Render Free
instance may take time while the service wakes.

## Feature map

- **Glance View:** bounded attention cards with content, action/state, risk, ranking priority, and
  source actions.
- **Open source / View original record:** navigate to the immutable source version or the labelled
  original historical record.
- **Voice:** prerecorded synthetic audio with a prepared timestamped transcript; it is not live ASR,
  microphone capture, or diarization.
- **Comments:** threaded internal discussion, mentions, resolve/unresolve, and assignment entry.
- **Tasks:** assignment and the `Open` → `In progress` → `Done` lifecycle; patients cannot access it.
- **AI suggestions:** Clinicians can `Accept` or `Reject` a suggestion; this state is independent of
  task status and never rewrites the original source.
- **Patient privacy:** server-side projection excludes internal comments, tasks, raw AI notes, and
  revision controls from Patient responses.

The repository and application use synthetic data only. The demo password is not stored in this
file, Git, the submission ZIP, or the Technical Brief.
