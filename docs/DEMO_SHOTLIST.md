# Nightingale demo shot list

| Shot | View / action | Evidence to capture | Suggested file |
| --- | --- | --- | --- |
| 1 | Clinician Top Card | Six-or-fewer cards, action/risk/status/source | `scenario-a-desktop.png` |
| 2 | “Why ranked?” expanded | Contribution breakdown and ranking disclaimer | `scenario-a-ranking.png` |
| 3 | Immutable source panel | Source entry/version, exact quote and span | `scenario-a-source.png` |
| 4 | Timeline after source click | Highlighted immutable source version in context | `scenario-a-timeline.png` |
| 5 | Staff revision history | Version list, diff, revert-as-new-version | `scenario-b-desktop.png` |
| 6 | Nested comments | Root, reply, resolve/unresolve state | `scenario-b-comments.png` |
| 7 | Conflict panel | Winner vs preserved stale submission, `409` | `scenario-c-conflict.png` |
| 8 | Historical context | Hot/warm/cold and derived-summary disclosure | `scenario-c-context.png` |
| 9 | Mobile workspace | No horizontal overflow at 390×844 | `mobile-scenario-a.png` |
| 10 | Patient projection | Patient-facing entries only | `patient-privacy.png` |

The current Playwright runner emits the Scenario A/B screenshots under ignored
`artifacts/gate-b/`. Delivery copies are synthetic and should be selected from those outputs after
visual review; no raw database or password file belongs in the package.
