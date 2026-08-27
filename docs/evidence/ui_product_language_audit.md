# UI product-language audit

Date: 2026-08-27
Scope: local product-language release candidate
Repository: `D:\NTU学习\Nightingale_project`

This audit checks that contestant-facing surfaces describe user value first while retaining the
technical facts needed for trust, debugging, and review. It does not delete provenance data, change
RBAC, change the database model, or describe the prepared Voice transcript as ASR output.

The product-language changes are local at this point. The last observed Render rehearsal commit was
`e766fe9`; its screenshots and online observations remain historical until an explicitly authorized
release push. The after screenshots below were generated from the local Alembic-migrated, seeded
Playwright environment.

## Before / after mapping

| Surface | Before language or presentation | After product language | Technical fact retained |
| --- | --- | --- | --- |
| Session header | `{{role}} · cookie session`; `Live updates: Connected` | `Staff`, `Clinician`, or `Patient`; `Record status: Up to date` | Session remains cookie-authenticated; reconnecting has a clear user-facing state |
| Glance View | `Top Card`, `P96`, `No explicit risk tag`, `No action label` | `Glance View`, `Priority 96`, `No risk flag`, `No action required` | Priority, risk, action state, and status remain separate fields |
| Source panel | `Immutable source` as the primary title; Python code-point offsets and SHA-256 in the main panel | `Original source`; type, date, version, and highlighted excerpt are primary; `Technical details` is collapsed | Exact offsets, source reference, and hash remain available in the closed details section |
| Timeline source | Developer-oriented immutable/source wording | `Original source excerpt` and a clear saved-version explanation | The excerpt still resolves to the originating immutable version and exact span |
| Historical context | `Hot context`, `Warm index`, `Derived historical context`, and `canonical` in summary text | `Recent context`, `Earlier context`, `Historical summary`, and `View original record` | Summary/source pointers and source-of-truth relationship remain intact |
| AI Scribe | Provider/model badge and implementation-oriented status | `AI-assisted note`, `Ready for review`, and a safe failure message | Provider identity and configuration are restricted to technical details/API evidence; suggestions remain reviewable |
| Voice | `Ambient Voice Prototype`, fixture/mock/provider terminology and unavailable-confidence wording | `Voice note`, `Review a pre-recorded care conversation`, `Ready for review`, and `About this example` | The disclosure says this is a pre-recorded synthetic conversation with a prepared timestamped transcript; no ASR claim is added |
| Collaboration | Raw request/error details could reach an error surface; collaborator roles were raw values | `Team discussion`, `Mentioned teammates`, localized role labels, and a generic safe action error | Threading, mentions, resolve/unresolve, assignment, and server-side authorization remain unchanged |
| History/conflict | Implementation-oriented expected/actual wording | `This record changed while you were editing`; review both versions | Current version and both preserved texts remain visible for safe review |
| Patient view | `Internal Glance View is hidden` and projection-oriented wording | `Your care summary`; `Only information shared with you appears here` | Patient-facing projection and API authorization are unchanged and separately tested |
| Generated suggestion text | `Fixture suggestion:` and `Synthetic fixture output requires clinician review.` | `Care note suggestion:` and `This suggestion is ready for clinician review.` | Redacted text, exact quote, source span, and review state are unchanged |

## What remains technical by design

The following remain available to reviewers without occupying the primary workflow:

- Source `Technical details` contains the text-position unit, source reference, exact span, and
  SHA-256 statement.
- AI `Technical details` contains the synthetic-data and suggestion-boundary explanation; provider
  configuration is not rendered in the normal workflow.
- Voice `About this example` contains the precise pre-recorded synthetic-audio disclosure.
- Backend APIs and evidence retain provider names, model names, safe error codes, hashes, IDs, and
  migration/test metadata for engineering verification.

## Screenshot evidence

The existing release-candidate screenshots from 2026-08-26 are retained as before references:

- [Before: desktop Scenario A](../../deliverables/screenshots/scenario-a-desktop.png)
- [Before: mobile Scenario A](../../deliverables/screenshots/scenario-a-mobile.png)
- [Before: desktop Scenario B](../../deliverables/screenshots/scenario-b-desktop.png)
- [Before: mobile Scenario B](../../deliverables/screenshots/scenario-b-mobile.png)
- [Before: desktop context](../../deliverables/screenshots/scenario-c-context-desktop.png)
- [Before: mobile context](../../deliverables/screenshots/scenario-c-context-mobile.png)

The following after references were generated on 2026-08-27 by local Playwright E2E runs. The
`artifacts/gate-b` directory is intentionally ignored by Git as local evidence, so these files are
workspace evidence rather than submission-package contents.

| Surface | Desktop after | Mobile after |
| --- | --- | --- |
| Staff workspace / Glance | [Scenario A](../../artifacts/gate-b/desktop-1440-scenario-a.png) | [Scenario A](../../artifacts/gate-b/mobile-390-scenario-a.png) |
| Original source open | [Source](../../artifacts/gate-b/desktop-1440-source-open.png) | [Source](../../artifacts/gate-b/mobile-390-source-open.png) |
| Voice note | [Clinical Voice](../../artifacts/gate-b/desktop-1440-voice-clinical.png) | [Clinical Voice](../../artifacts/gate-b/mobile-390-voice-clinical.png) |
| Patient Voice | [Patient Voice](../../artifacts/gate-b/desktop-1440-voice-patient.png) | [Patient Voice](../../artifacts/gate-b/mobile-390-voice-patient.png) |
| Comments drawer | [Comments](../../artifacts/gate-b/desktop-1440-comments-open.png) | [Comments](../../artifacts/gate-b/mobile-390-comments-open.png) |
| Task drawer | [Task](../../artifacts/gate-b/desktop-1440-task-open.png) | [Task](../../artifacts/gate-b/mobile-390-task-open.png) |
| History/conflict/context | [Scenario C](../../artifacts/gate-b/desktop-1440-scenario-c.png) | [Scenario C](../../artifacts/gate-b/mobile-390-scenario-c.png) |
| Guide | [Guide](../../artifacts/gate-b/desktop-1440-guide-open.png) | [Guide](../../artifacts/gate-b/mobile-390-guide-open.png) |
| Demo preview | [Preview](../../artifacts/gate-b/desktop-1440-preview-mobile.png) | [Preview](../../artifacts/gate-b/mobile-390-preview-mobile.png) |
| Patient privacy | [Patient](../../artifacts/gate-b/desktop-1440-patient-privacy.png) | [Patient](../../artifacts/gate-b/mobile-390-patient-privacy.png) |

Loading/error/empty states are covered by Vitest assertions and were not captured as separate visual
artifacts because they require transient or data-manipulation setup. No screenshot includes a
password, API key, database URL, environment value, cookie, or raw log.

## Automated checks

- Frontend product-language/unit suite: `28 passed`.
- Frontend lint, Prettier, TypeScript build/type-check: passed.
- Gate B browser suite: `14 passed` across desktop `1440×900` and mobile `390×844`.
- Voice browser suite: `4 passed` across desktop and mobile.
- Backend suite: `85` collected tests passed; coverage run reported `88%`.
- Backend Ruff (`--no-cache`), mypy, and `pip check`: passed.
- Required `requirements.txt` SHA-256 was checked after the change and remains unchanged.

## Acceptance notes

- Patient privacy remains server-side and was exercised by both browser and backend checks.
- Unicode/repeated-quote exact-span and integrity-warning tests remain green.
- Deep-linked source, persistent source visibility, replacement by a second source, and query
  cleanup remain green.
- UX-01 is passed only on the previously recorded independent Simplified Chinese participant
  evidence; the local product-language screenshots are not additional UX-01 participants.
- The final video, final PDF refresh, final ZIP/MANIFEST, and external release are intentionally not
  claimed by this audit.
