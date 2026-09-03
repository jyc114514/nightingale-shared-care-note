# Round 9 closure evidence

Date: 2026-09-03

Status: **ROUND 9 PARTIAL - PROTECTED-FIRST LIVE; AUTHENTICATED HOSTED BENCHMARK PENDING**

Submission decision: **SUBMISSION READY WITH DISCLOSED SUPPLEMENTARY BENCHMARK GAP**. The pending
benchmark is retained as honest engineering evidence; it is not a requested deliverable and does
not block final Demo Video preparation or submission.

This is the closure record for the existing Nightingale service. It does not create a new
Render resource, reset production data, alter the requirements brief, or inspect the original
user-supplied MP4.

## Release identity

- Repository: `jyc114514/nightingale-shared-care-note`
- Main and origin/main at closure: `4f4fc84c3451152e63135bd7fdd7b851bb43a1ea`
- Release tag: `real-clinic-rc6`, peeled commit `4f4fc84c3451152e63135bd7fdd7b851bb43a1ea`
- PostgreSQL 18 gate: [run 33702459026](https://github.com/jyc114514/nightingale-shared-care-note/actions/runs/33702459026)
- Deploy-candidate gate: [run 33702720681](https://github.com/jyc114514/nightingale-shared-care-note/actions/runs/33702720681)
- Existing Render service: `nightingale-shared-care-note`
- Render deploy: `dep-dacd2lgn74is73co3t2g`, source commit `4f4fc84`
- URL: `https://nightingale-shared-care-note.onrender.com`
- Auto-Deploy: disabled
- Database target: existing managed Render PostgreSQL 18
- Alembic head: `0015_feedback_backward_compat`
- Requirements SHA-256: `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5`

## Protected-item starvation repair

The production issue was not only rehearsal-state pollution. The former Glance selection path
ordered candidates by `display_priority`, so six ordinary 100-priority candidates could bury an
active allergy conflict with a deterministic 95 safety floor. The fix keeps the score meaning
unchanged and makes selection semantics explicit:

1. active protected candidates enter a protected bucket first;
2. candidates within each bucket retain deterministic display-priority, occurrence-time, and
   resource-ID ordering;
3. the result is still capped at six items;
4. resolved, rejected, and superseded items do not occupy protected positions;
5. impressions use the same ordering and record `importance-v3-protected-first`.

The real application RED regression is `8ffafed` (`test: reproduce protected glance starvation`)
and the product/coverage GREEN checkpoint is `cc2e10c` (`fix: prevent protected safety items
from being ranked out`). The final CI correction and deployed runtime are in `4f4fc84`.

## Local and CI verification

| Area | Result |
| --- | --- |
| Backend full suite | 194 passed |
| Global `app` coverage | 86.62%; `--cov-fail-under=85` passed |
| Ruff check / format | passed |
| mypy | passed |
| pip check | passed |
| Frontend Vitest | 45 passed |
| Frontend lint / Prettier / type-check / build | passed |
| Playwright core | 20 passed across desktop/mobile |
| Playwright Voice | 4 passed |
| Playwright publication | 2 passed |
| PostgreSQL 18 exact gate | passed at run 33702459026 |
| Deploy-candidate gate | passed at run 33702720681 |

The migration head remained `0015_feedback_backward_compat`; no migration, dependency,
requirements, lockfile, Voice, DeepSeek, or data-model meaning was changed in this closure.

## Hosted evidence

Anonymous checks against the exact deployed service passed:

- HTTP `/health`: 301 redirect to HTTPS.
- HTTPS `/health`, SPA root, current JavaScript, and current CSS: 200.
- Unauthenticated `/auth/me` and `/patients`: 401.
- Sustained watch: 15/15 samples, zero failures, zero observed 5xx.
- Render startup/access log observation: normal access lines present; zero observed formatter
  `ValueError`, `--- Logging error ---`, or logging traceback.

The anonymous watch was run by the credential-free helper
[`round9_closure_canary.mjs`](../../scripts/round9_closure_canary.mjs); it records aggregate
statuses and timings only.

The current authenticated Staff page was observed without reading or extracting cookies,
storage, passwords, or tokens:

- Glance contains six items and the protected "Conflicting allergy information" item is first.
- The card explains protected-first ranking and keeps priority distinct from medical risk.
- Staff can open the two conflict source assertions and their immutable source panels.
- Staff sees the read-only boundary; no clinical adjudication control is exposed.
- `Prepare patient update` opens a Draft publication review with immutable source evidence and
  the explicit message that accepting an AI suggestion does not publish it to the patient.

These are UI canary observations, not a substitute for a full authenticated benchmark. The
current connector exposes no safe page-context `fetch`/`performance` surface for 20 warm-up plus
200 measured same-origin requests, and no cookie/token extraction was attempted. Staff and
Patient hosted P50/P95/P99 therefore remain pending. The exact-commit closure also did not repeat
Clinician adjudication, Patient privacy, or authenticated SSE through a second session.

## Tag decision and boundaries

`real-clinic-live1` was deliberately **not** created. Its required closure conditions include a
completed authenticated hosted benchmark, a Staff warm P95 of at most 300 ms, and a current
Patient privacy canary; those conditions are not evidenced by the available connector. This is a
soft partial release record, not a fabricated complete gate.

The local WebM remains ignored and unchanged. The original user-supplied MP4 remains untracked,
untouched, and unread. No final ZIP or email was produced in this closure.
