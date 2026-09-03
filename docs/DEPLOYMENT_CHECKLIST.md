# Deployment checklist

## Round 9 closure addendum (2026-09-03)

The current existing-service release is `4f4fc84c3451152e63135bd7fdd7b851bb43a1ea`, tagged
`real-clinic-rc6`, and Live as Render deploy `dep-dacd2lgn74is73co3t2g`. PostgreSQL 18 CI run
`33702459026` and deploy-candidate run `33702720681` passed. The protected-first Glance repair,
global 86.62% application coverage, anonymous HTTPS boundaries, clean access logging, and 15/15
sustained watch are detailed in [`evidence/round9_closure.md`](evidence/round9_closure.md).

The hosted authenticated benchmark remains unchecked because no permitted same-origin page
request/performance surface is available through the current browser connector. No cookies,
storage, passwords, or tokens were extracted. `real-clinic-live1` was not created, and Patient/
Clinician exact-commit canaries were not re-claimed from earlier RC5 evidence.

## Historical earlier deployment checklist records

Status: **Render deployment live with synthetic evaluation limitations documented.**

## Hosted evidence

- [x] Exactly one Docker web service named `nightingale-shared-care-note`, Free plan, Singapore
      region, `/health` HTTP health check.
- [x] Exactly one Free Render Postgres database, PostgreSQL 18, Singapore, connected through the
      Blueprint `connectionString`.
- [x] Production image builds the frontend and serves it from FastAPI on the Render `$PORT`.
- [x] Production startup validates secure settings, runs the complete Alembic chain through
      `0010_postgres_compat`, and runs synthetic seed only with `DEMO_SEED_ENABLED=true`.
- [x] `LLM_PROVIDER=fixture` and `VOICE_PROVIDER=fixture`; no DeepSeek key or Voice model is in
      the Render production image/configuration.
- [x] Successful Voice fixture deploys `dep-da7t9tjl550s73cvmhgg` (Auto-Deploy) and
      `dep-da7t9u0chk0s73c7dbl0` (Blueprint sync) from commit `e766fe9` are Live at
      `https://nightingale-shared-care-note.onrender.com`.
- [x] Final release-candidate commits `1779407` and `42a01b6` were pushed to the same private
      repository. The latest existing-service deploy `dep-da84vcp5efls73dm07vg` from `42a01b6`
      is Live; no duplicate Render resource was created.
- [x] HTTP-to-HTTPS redirect, HTTPS `/health`, SPA root, unauthenticated `401`, migration/seed
      logs, and PostgreSQL schema evidence are recorded in
      [`deployment_security.md`](evidence/deployment_security.md).
- [x] Render provider TLS and Postgres AES-256-at-rest documentation is linked in the security
      evidence.

## Application and operational follow-up

- [x] `DATABASE_URL` is supplied by the platform Blueprint connection string; it is not committed
      or exposed to the browser.
- [x] `SESSION_SECRET` and `DEMO_SEED_PASSWORD` are platform-generated and were not copied into
      the repository, logs, screenshots, or this record.
- [x] `COOKIE_SECURE=true` and the exact HTTPS Origin are declared in the deployed Blueprint;
      local production validation fails closed when secure settings are missing.
- [x] Perform an authenticated production login smoke with the platform-generated demo password
      entered manually by the user. The audit did not read, print, or transmit that secret.
- [ ] Re-run the warm-path benchmark against the hosted PostgreSQL/service topology.
- [ ] Verify backups, restore, retention, deletion, incident response, and access review with the
      provider.
- [ ] Complete independent UX-01, final video playback, and submission email steps.

Render Free limitations remain material: free web services can spin down after inactivity, the
filesystem is ephemeral, and Free Postgres is limited to 1 GB with a temporary lifetime. This is
an evaluation deployment, not a clinical production guarantee.

Official references: [Blueprint specification](https://render.com/docs/blueprint-spec), [HTTP health checks](https://render.com/docs/health-checks),
[Free instance limitations](https://render.com/docs/free), [managed TLS](https://render.com/docs/tls), and
[Render Postgres encryption](https://render.com/docs/postgresql-creating-connecting).

## Optional external provider boundary

- [x] Fixture remains the default and network-free AI path.
- [x] DeepSeek remains opt-in and local-only; it is not part of Render configuration.
- [x] Redaction and schema validation remain server-side, with explicit provider failure behavior.
- [x] Voice remains Level C fixture-only locally and is enabled on Render only through the fixture
      provider; no ASR inference, microphone, upload, or diarization is deployed.
- [x] Complete authenticated online Voice smoke with Staff, Clinician, and Patient sessions. The
      final check confirmed the Staff suggestion/source path, Clinician audio availability, and
      Patient-only audio/privacy projection; no microphone, upload, ASR, or diarization was used.
