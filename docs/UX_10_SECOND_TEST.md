# UX-01 human 10-second test

Status: **pending human sign-off**. Automated browser checks establish rendering and interaction,
not human comprehension speed.

## Protocol

1. Use the seeded synthetic patient and a fresh browser viewport at 1440×900, then repeat at
   390×844.
2. Give the participant this instruction: “You have ten seconds. Tell me what needs attention,
   what action is available, whether any item is an explicit risk, and where its source came from.”
3. Start the timer when the workspace becomes visible. Do not explain the labels or point at a
   control during the ten seconds.
4. Record whether the participant identifies: (a) the highest-priority item, (b) its action/state,
   (c) explicit risk vs ranking priority, and (d) the source-navigation affordance.
5. After the timer, ask the participant to open the source and explain what “derived summary · not
   canonical source” means.

## Pass rule

Pass only if the participant identifies all four items within ten seconds at both viewports and can
open the source without coaching. Record participant count, viewport, completion time, errors,
and any confusion. A screenshot or Playwright pass is not a substitute for this check.

## Current evidence boundary

The Top Card visibly includes content, open action, explicit risk, status, source, and a collapsed
ranking explanation. Playwright covers desktop/mobile rendering and source navigation. The product
team still needs a real human observation before marking UX-01 fully passed.
