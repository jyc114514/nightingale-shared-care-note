# Nightingale demo shot list

| Shot | View / action | Evidence to capture | Suggested file |
| --- | --- | --- | --- |
| 1 | English and Chinese chrome | Language toggle, translated heading, original clinical text | `scenario-a-language.png` |
| 2 | Clinician Top Card | Six-or-fewer cards, action/risk/status/source | `scenario-a-desktop.png` |
| 3 | Why ranked? | Contribution breakdown and ranking disclaimer | `scenario-a-ranking.png` |
| 4 | Immutable source | Source entry/version, exact quote/span after focus fades | `scenario-a-source.png` |
| 5 | Timeline deep link and close | Refresh persistence, Close source, query cleanup | `scenario-a-timeline.png` |
| 6 | Staff revision history | Version list, diff, revert-as-new-version | `scenario-b-desktop.png` |
| 7 | Mention autocomplete | Keyboard `@` suggestion and selected collaborator metadata | `scenario-b-mentions.png` |
| 8 | Assignment/task | Source comment, assignee, status transition, Glance action | `scenario-b-tasks.png` |
| 9 | Two-browser SSE | Clinician receives comment/task invalidation without page reload | `scenario-b-realtime.png` |
| 10 | Conflict panel | Winner vs preserved stale submission, `409` | `scenario-c-conflict.png` |
| 11 | Historical context | Hot/warm/cold and derived-summary disclosure | `scenario-c-context.png` |
| 12 | Patient projection | Patient-facing entries only; internal tasks/comments absent | `patient-privacy.png` |
| 13 | Mobile workspace | Chinese chrome, source/task controls, no horizontal overflow at 390x844 | `mobile-scenario-a.png` |
| 14 | Contextual drawers | Comments loading/error focus path and task source context at desktop/mobile | `comments-open.png`, `task-open.png` |
| 15 | Demo viewport preview | Same-origin interactive Desktop 1440x900 and Mobile 390x844 frames without recursive toolbar | `preview-desktop.png`, `preview-mobile.png` |

The Playwright runner emits synthetic Scenario A/B/C screenshots under ignored `artifacts/gate-b/`.
Delivery copies should be selected after visual review; no database, password file, runtime log, or
real patient data belongs in the package.
