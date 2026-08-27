# Deployment checklist

Status: **Render deployment blocked after two meaningful attempts; no third attempt will be
made in this phase.**

## Required before a hosted demo

- [ ] Choose a managed PostgreSQL provider and record the provider, region, backup policy, and
      encryption-at-rest evidence.
- [ ] Set `DATABASE_URL` through the platform secret store; never commit it or expose it to the
      browser.
- [ ] Set a random `SESSION_SECRET` with at least 32 characters.
- [ ] Set `COOKIE_SECURE=true`; verify production startup fails closed when it is false.
- [ ] Configure the exact frontend Origin allowlist; verify credentialed writes reject foreign
      origins.
- [ ] Terminate HTTPS/TLS at the platform and record certificate/transport evidence.
- [ ] Run `alembic upgrade head` against a disposable deployment database, then `alembic check`.
- [ ] Run synthetic seed or a deployment-specific fixture only; never load real patient data.
- [ ] Verify logs contain request/job metadata only and no raw note, credentials, or tokens.
- [ ] Re-run the warm-path benchmark against the actual database/service topology.
- [ ] Verify backups, retention, deletion, incident response, and access review with the provider.

## Render blueprint boundary

- [x] Exactly one Docker web service named `nightingale-shared-care-note`, Free plan, Singapore
      region, `/health` HTTP health check was created.
- [x] Exactly one Free Render Postgres database was created and connected through the Blueprint
      `connectionString`.
- [x] The production image build completed on the first deployment attempt and includes the
      frontend build plus FastAPI static serving on the Render `$PORT`.
- [x] Production startup validates secure settings, runs `alembic upgrade head`, and runs the
      synthetic seed only when `DEMO_SEED_ENABLED=true`.
- [x] `LLM_PROVIDER=fixture` and `VOICE_PROVIDER=disabled`; no DeepSeek key or Voice dependency is
      part of the Render production configuration.
- [ ] Confirm a healthy Render service URL, successful migration/seed, HTTPS smoke, secure cookie,
      and database encryption evidence in `docs/evidence/deployment_security.md`.
- [ ] Repair the PostgreSQL-specific `0002_gate_b` comments batch migration, then perform a future
      bounded deployment attempt under an explicitly reopened deployment gate.

The exact two-attempt outcome is recorded in
[`deployment_attempt.md`](evidence/deployment_attempt.md). The reserved service address is
`https://nightingale-shared-care-note.onrender.com`, but it is not reported as a working demo
because both deployments failed before health.

Render Free limitations must remain visible: free web services spin down after inactivity, the
filesystem is ephemeral, and Free Postgres is limited to 1 GB and expires after 30 days. This is
an evaluation deployment, not a clinical production guarantee.

Official references used for the readiness design: [Blueprint specification](https://render.com/docs/blueprint-spec),
[HTTP health checks](https://render.com/docs/health-checks), [Free instance limitations](https://render.com/docs/free),
[managed TLS](https://render.com/docs/tls), and [Render Postgres encryption](https://render.com/docs/postgresql-creating-connecting).

## Optional external provider boundary

- [x] Keep `LLM_PROVIDER=fixture` as the default and network-free test/demo path.
- [x] If DeepSeek is selected, use only `deepseek-v4-flash` through the official API endpoint.
- [x] Store only an external key-file path in ignored `.nightingale-local.json`; never commit or
      expose the key/path to the browser, runtime metadata, logs, PDFs, or ZIPs.
- [x] Redact and validate synthetic text server-side before the provider call; do not send source
      reference, patient/clinic/user IDs, names, phones, IC/ID values, comments, or task metadata.
- [x] Keep provider failures explicit; no silent fixture fallback.
- [x] Record the one bounded synthetic smoke in [`deepseek_live_smoke.md`](evidence/deepseek_live_smoke.md).
- [ ] Perform a provider-specific data-processing/compliance review and production cost/latency
      evaluation.

## Current local and external boundary

SQLite + real Uvicorn TCP is measured locally. Render resources exist, but the application has not
completed PostgreSQL migrations or reached a healthy service. Therefore PostgreSQL runtime,
TLS, encryption-at-rest, deployment backup, hosted operational controls, and external LLM quality
remain unverified. The DeepSeek smoke proves one bounded local request only; it does not establish
provider compliance or production quality. `Start Nightingale Demo.cmd` is a local convenience
wrapper, not deployment.
