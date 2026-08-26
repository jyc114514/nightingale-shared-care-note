# UX-01 human 10-second test

Status: **pending human sign-off**. Automated browser checks establish rendering and interaction,
not human comprehension speed.

## Internal PM rehearsal (not independent UX-01 evidence)

- Locale: Chinese
- Viewport: Desktop
- Completion time: 5 seconds
- Result: 4/4 — highest-priority item, action/state, risk versus ranking, and source/version/exact span were identified correctly.
- Coaching: none
- Limitation: the participant had already read the Guide and knew the product controls, so this rehearsal does not close UX-01.

## Protocol

1. Use the seeded synthetic patient, close the Learning Guide, select English or 简体中文, and use
   a fresh browser viewport at 1440x900, then repeat at 390x844.
2. Give the participant this instruction: “You have ten seconds. Tell me what needs attention,
   what action is available, whether any item is an explicit risk, and where its source came from.”
3. Start the timer when the workspace becomes visible. Do not explain labels or point at a control.
4. Record whether the participant identifies: (a) the highest-priority item, (b) its action/state,
   (c) explicit risk versus ranking priority, and (d) the source-navigation affordance.
5. After the timer, ask the participant to open the source, explain “derived summary · not the original
   record,” and say whether the selected source remains visible after the focus ring fades.

## Pass rule

Pass only if the participant identifies all four items within ten seconds at both viewports and can
open the source without coaching. Record participant count, viewport, completion time, errors, and
confusion. A screenshot or Playwright pass is not a substitute for this check.

## Current evidence boundary

The Top Card includes content, open action, explicit risk, status, source, and a collapsed ranking
explanation. Playwright covers desktop/mobile rendering, bilingual chrome, source navigation,
keyboard mentions, tasks, and SSE invalidation. The product team still needs a real human
observation before marking UX-01 fully passed.
