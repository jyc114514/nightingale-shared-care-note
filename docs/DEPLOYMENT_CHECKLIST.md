# Deployment checklist

Status: **not deployed**. This checklist records the evidence required before making production
claims; Phase 7/8 adds only a local Windows launcher, metadata-only local SSE, and an optional
redaction-gated DeepSeek adapter. No deployment, account, or hosting action was taken.

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

## Optional external provider boundary

- [x] Keep `LLM_PROVIDER=fixture` as the default and network-free test/demo path.
- [x] If DeepSeek is selected, use only `deepseek-v4-flash` through the official API endpoint.
- [x] Store only an external key-file path in ignored `.nightingale-local.json`; never commit or
      expose the key/path to the browser, runtime metadata, logs, PDFs, or ZIPs.
- [x] Redact and validate synthetic text server-side before the provider call; do not send source
      reference, patient/clinic/user IDs, names, phones, IC/ID values, comments, or task metadata.
- [x] Keep provider failures explicit; no silent fixture fallback.
- [x] Record the one bounded synthetic smoke in [`deepseek_live_smoke.md`](evidence/deepseek_live_smoke.md).
- [ ] Perform a provider-specific data-processing/compliance review and production cost/latency evaluation.

## Current local boundary

SQLite + real Uvicorn TCP is measured locally. PostgreSQL, TLS, encryption-at-rest, deployment
backup, hosted operational controls, and external LLM quality remain unknown. The DeepSeek smoke
proves one bounded request only; it does not establish provider compliance or production quality.
`Start Nightingale Demo.cmd` is a local convenience wrapper, not deployment.
