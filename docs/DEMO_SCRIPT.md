# Nightingale demo script

Target length: 3–4 minutes. Use synthetic seed data only. The demo password is supplied through
the local `DEMO_SEED_PASSWORD` environment variable and must never be written in the recording,
repository, or logs.

## Opening (15 seconds)

“Nightingale is a shared-care note, not an autonomous medical system. The Top Card ranks what
needs attention, while every suggestion remains traceable to an immutable source and a human
review state.”

## Scenario A — trace and trust (75 seconds)

1. Sign in as `clinician.a@clinic-a.test` and select the seeded synthetic patient.
2. Point out that the Top Card has no more than six items and separately displays item kind,
   action state, explicit risk, status, and source label.
3. Open **Why ranked?**. Read the base, recency, action, confirmation, adaptive, and final
   contributions. Say: “This is ranking priority, not a medical risk score.”
4. Click **Pin**, then **Unpin**. Explain that feedback is clinic-scoped and idempotent and does
   not mutate risk or provenance.
5. Open an AI-scribed doctor-consult source. Show the exact quote in the immutable source panel,
   then the matching highlighted span in the timeline. Refresh the URL/deep link if time allows.
6. Accept or reject a suggestion and show that the status changes while the source remains
   resolvable.

## Scenario B — collaborate without erasure (75 seconds)

1. Sign in as `staff.a@clinic-a.test`.
2. Open the staff note, edit it, and save a new revision.
3. Open history, compare the prior version, and revert it. Say: “Revert creates a new snapshot;
   it does not delete history.”
4. Add a root internal comment, reply to it, resolve it, and unresolve it. The reply is nested
   under its parent rather than flattened into a separate list.

## Scenario C — surface conflict and history (60 seconds)

1. Keep the staff session and obtain the current version from the history panel.
2. Submit one current write and one stale write with the same `expected_version`.
3. Show the `409` conflict panel with current content and preserved attempted content side by
   side. Say: “There is no silent last-write-wins.”
4. Open **Historical context**. Point out Hot, Warm index, and the derived cold period.
5. Read the disclosure “Derived summary · not canonical source” and open a canonical source
   pointer back in the timeline.

## Privacy close (20 seconds)

Sign in as `sarah.patient@clinic-a.test`. Show that patient-facing summary/instruction entries
remain visible while internal Glance, comments, raw AI notes, conflict details, and internal source
pointers are absent. Mention that this is a server-side projection, not a hidden UI control.

## If a live action fails

Use the already seeded state and the static screenshots in `deliverables/screenshots/`. Do not
invent a successful provider call, hosted database, TLS guarantee, or UX result. The deterministic
local provider and recorded test evidence are the fallback boundary.
