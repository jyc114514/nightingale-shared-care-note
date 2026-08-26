# Nightingale demo script

Target length: 3-4 minutes. Use synthetic seed data only. The password is supplied locally to the
launcher or `DEMO_SEED_PASSWORD`; never record, print, commit, or log it.

## Opening (15 seconds)

“Nightingale is a shared-care note, not an autonomous medical system. The Top Card ranks what
needs attention, while every suggestion remains traceable to an immutable source and a human
review state.”

## Scenario A - trace, trust, and bilingual chrome (70 seconds)

1. Double-click `Start Nightingale Demo.cmd`, or use the manual setup. Sign in as
   `clinician.a@clinic-a.test` and select the synthetic patient.
2. Switch between English and 简体中文. Explain that only application chrome changes; clinical
   note content and quotes remain in the original language.
3. Point out that the Top Card has no more than six items and separately displays item kind,
   action state, explicit risk, status, ranking priority, and source label.
4. Open **Why ranked?**. Say: “This is ranking priority, not a medical risk score.”
5. Open an AI-scribed doctor-consult source. Show the exact quote in the immutable source panel
   and the matching source span in the timeline. Wait beyond the focus animation: the source stays.
6. Refresh the deep link, then close the source. The panel/span disappears while `patient` stays
   in the URL and `highlight` is removed.

## Scenario B - collaborate without erasure (85 seconds)

1. Sign in as `staff.a@clinic-a.test`.
2. Open the staff note, edit it, compare history, and revert it. Say: “Revert creates a new
   snapshot; it does not delete history.”
3. Open Comments; the contextual drawer appears immediately. Type `@`, use the keyboard
   suggestion, and choose a clinic collaborator.
4. Add a root comment and reply. Click **Assign task**; the task drawer states the selected
   entry/comment context and focuses the title. Create a task linked to the comment,
   choose an assignee, move it to **In progress**, then **Done**. The open task appears as a
   Glance action and leaves the active action list after completion.
5. Keep a second clinician browser open on the same patient. The second browser receives the
   comment/task metadata event and refetches the canonical API without a page refresh.
6. Resolve and unresolve the comment thread.

## Scenario C - conflict and history (55 seconds)

1. Submit one current write and one stale write with the same `expected_version`.
2. Show the `409` conflict panel with current and preserved attempted content. Say: “There is no
   silent last-write-wins.”
3. Open Historical context. Point out Hot, Warm index, and the derived cold period, then choose
   one of the labelled **View original record** rows. Explain that the derived summary is not the
   original record; the immutable source remains the source of truth.

## Privacy close (20 seconds)

Sign in as `sarah.patient@clinic-a.test`. Show patient-facing entries only. Internal Glance,
comments, raw AI notes, tasks, conflict details, and internal source pointers remain unavailable
through server-side projection and authorization.

## Help and UX boundary

The bilingual Learning Guide is closed by default and may be opened for learning before the
formal UX-01 test. Close it before the ten-second test. The Guide explicitly lists actions that
modify demo state: Accept, Reject, Edit, Revert, Comment, and Task creation/update.

## If a live action fails

Use the seeded state and reviewed synthetic screenshots. Do not invent a successful provider call,
hosted database, TLS guarantee, SSE completion, or human UX result.
