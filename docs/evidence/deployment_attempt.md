# Render deployment attempts - 2026-08-27

## Final outcome

**Healthy deployment achieved on the existing resources after migration recovery.** Exactly one
Free Render Web Service and one Free Render Postgres database were used. No duplicate resource
pair, paid plan, billing change, custom domain, worker, Redis, or destructive database operation
was created or performed.

- Blueprint: `exs-da7p448n74is73a07s0g`
- Web Service: `nightingale-shared-care-note` (`srv-da7p56s9v7es73f7n12g`), Free, Singapore
- Postgres: `nightingale-shared-care-note-db` (`dpg-da7p4gk9v7es73f7l6eg-a`), Free, Singapore
- Successful deploy: `dep-da7ptlek1f9s73ch6910`
- Successful source: `d2a12cd`
- Service URL: `https://nightingale-shared-care-note.onrender.com`
- GitHub repository: `jyc114514/nightingale-shared-care-note` (private)

## Attempt history

### Attempt 1

- Deploy ID: `dep-da7p5749v7es73f7n450`
- Source: `a4d7bd6`
- Trigger: Blueprint
- Result: failed during startup migration after the Docker image build completed
- Blocker: `0002_gate_b` used `batch_alter_table("entries", recreate="always")`; PostgreSQL
  rejected dropping `entries_pkey` while `entry_versions`, `conflicts`, and `comments` still
  depended on it.

### Attempt 2

- Deploy ID: `dep-da7p9o7lk1mc738bdor0`
- Source: `9fe8c40`
- Trigger: Auto-Deploy
- Result: failed during startup migration after 43.7 seconds
- Blocker: the `comments` batch recreate dropped `comments_pkey` before creating the temporary
  table with its self-referential `parent_comment_id REFERENCES comments(id)` foreign key.

### Recovery and CI

The isolated branch `codex/postgres-migration-fix` repaired the PostgreSQL paths and added a real
PostgreSQL 18 GitHub Actions gate. The successful run was:

- Run: `33032765274`
- Job: `98388787825`
- Source: `d2a12cd`
- Result: success in 1m34s
- Evidence: full `0001→0010` upgrade, `alembic check`, downgrade to `0001` and re-upgrade,
  PostgreSQL schema/FK assertions, seed twice with stable counts, and 82 backend tests.

The recovery included:

- PostgreSQL in-place changes for `entries` and `comments` in `0002_gate_b`, while preserving
  SQLite batch behavior.
- PostgreSQL widening of Alembic's bookkeeping `version_num` before the long `0007` revision is
  recorded.
- `0010_postgres_compat`, a forward corrective migration that removes the redundant PostgreSQL
  `users_email_key` constraint while retaining the ORM-required unique `ix_users_email` index.

## Successful Render startup evidence

Render deploy logs for `dep-da7ptlek1f9s73ch6910` show `Context impl PostgresqlImpl`, all migration
steps through `0010_postgres_compat`, successful synthetic seed counts, `Application startup
complete`, Uvicorn listening on the Render port, and repeated `GET /health 200 OK` checks.

The logged seed counts were:

`clinics=2`, `patients=2`, `users=5`, `entries=7`, `comments=2`, `highlights=5`,
`glance_items=5`, `archival_summaries=1`, `archival_sources=2`.

No raw note text, credentials, database URL, API key, or patient identifier was copied into this
record.

## Deployment smoke

- HTTP `/health`: `301` with `Location: https://nightingale-shared-care-note.onrender.com/health`.
- HTTPS `/health`: `200`, body `{"status":"ok","phase":"4-bonus-local"}`.
- HTTPS `/`: `200`, SPA mount present, no localhost API origin in the returned HTML.
- Unauthenticated `/auth/me`: `401`.
- Browser navigation to the HTTPS root displayed the sign-in screen and synthetic persona choices.

The production login flow was not exercised because `DEMO_SEED_PASSWORD` is a platform-generated
secret and was intentionally neither read nor printed. `COOKIE_SECURE=true`, fixture LLM, and
Voice-disabled settings are declared in the deployed `render.yaml`; local production validation
also fails closed when secure cookie settings are missing.

## External security boundary

The detailed TLS and database evidence is in [`deployment_security.md`](deployment_security.md).
This is an evaluation deployment using synthetic data only. Render Free web instances may sleep,
and the Free Postgres resource is limited and temporary; no clinical compliance, PHI readiness, or
production operational guarantee is claimed.
