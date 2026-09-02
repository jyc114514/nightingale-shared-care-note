# Round 9 Render live and canary evidence

Date: 2026-09-03

Status: **the repaired full application is Live; advanced production canary and hosted
authenticated benchmark remain partial.**

## Exact release path

- Repository: `jyc114514/nightingale-shared-care-note`
- Repair branch: `codex/round9-safe-logging-recovery`
- PostgreSQL 18 CI: [run 33650978171](https://github.com/jyc114514/nightingale-shared-care-note/actions/runs/33650978171)
- Verified CI source: `c6e9851288c745ceb66dad32078d1385ffbe3424`
- Release tag: `real-clinic-rc5` (peeled to the same commit)
- Main: fast-forwarded from `ef0e1e8` to `c6e9851`; no force push
- Existing Render Web Service: `nightingale-shared-care-note`
- Existing service ID: `srv-da7p56s9v7es73f7n12g`
- Deploy: `dep-dac4dgek1f9s73e4qu30`, manually deployed from `c6e9851`
- URL: `https://nightingale-shared-care-note.onrender.com`
- Auto-Deploy: kept disabled for controlled release
- Database target: existing managed Render PostgreSQL 18; no new resource was created

## Deployment and anonymous canary

The Render dashboard showed `Deploy succeeded | Live` for the exact repair commit. The observed
startup window reported PostgreSQL migration context, idempotent synthetic seed counts,
application startup completion, Uvicorn running, and ordinary access requests. No formatter
exception or logging traceback was observed.

Anonymous Node HTTPS checks produced:

- HTTP `/health`: `301` redirect to HTTPS.
- HTTPS `/health`, `/`, current JavaScript asset, and current CSS asset: `200`.
- Unauthenticated `/auth/me` and `/patients`: `401`.
- Missing SPA route: `200` fallback.
- Sustained watch: **15/15** health/root/current asset probes successful, **0 failures** and
  **0 observed 5xx**; observed request times were approximately 0.14–0.21 seconds.

## Authenticated browser canary

Fresh user-provided browser sessions verified the deployed product without extracting cookies,
storage, passwords, or environment values:

- **Staff:** correct Staff identity and clinic, six-item Glance cap, source panel, Comments,
  Tasks, and History open/close paths.
- **Clinician:** correct Clinician identity and clinic, History with Before/After comparison,
  exact immutable source span navigation, and clinician-only review controls.
- **Patient:** correct Patient identity and projection; no internal Glance, raw AI, comments,
  tasks, history, conflicts, or staff/clinician controls were exposed. Patient Voice remained the
  prerecorded synthetic fixture path.
- **SSE:** the authenticated internal page reported the connected live-update state; the browser
  did not create a repeated Comments/EventSource loop during the observed path.

The production database had accumulated synthetic rehearsal highlights. The protected allergy
conflict and patient-publication actions were not visible in the current top-six Glance slice,
so they are **not claimed as passed in this production canary**. No production cleanup or write
was performed to manufacture that state.

## Boundaries and stop decisions

- No Render rollback was required after the repair; no second speculative deployment was made.
- `real-clinic-live1` was not created because the full advanced canary was not observable.
- The hosted authenticated benchmark is recorded separately as pending in
  [`round9_hosted_performance.md`](round9_hosted_performance.md). No browser cookie or token was
  extracted to manufacture a benchmark credential.
- Managed TLS/encryption-at-rest evidence supports the prototype boundary, but is not an
  independent cryptographic audit or clinical compliance certification.
