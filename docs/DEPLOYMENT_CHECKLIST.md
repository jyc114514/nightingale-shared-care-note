# Deployment checklist

Status: **not deployed**. This checklist records the evidence required before making production
claims; Phase 7 adds only a local Windows launcher and metadata-only local SSE. No provider,
account, or hosting action was taken.

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

## Current local boundary

SQLite + real Uvicorn TCP is measured locally. PostgreSQL, TLS, encryption-at-rest, deployment
backup, hosted operational controls, and external LLM quality remain unknown until a provider is
explicitly selected. `Start Nightingale Demo.cmd` is a local convenience wrapper, not deployment.
