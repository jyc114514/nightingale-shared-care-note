# Render deployment security evidence - 2026-08-27

## Scope and status

This record covers the successful synthetic evaluation deployment of Nightingale. It is evidence
for the Render transport/database boundary, not a clinical compliance certification.

- Web Service: `nightingale-shared-care-note`, Free, Singapore
- Postgres: `nightingale-shared-care-note-db`, Free, Singapore, PostgreSQL 18, 1 GB
- Migration baseline deploy: `dep-da7ptlek1f9s73ch6910` (`d2a12cd`)
- Comments fix deploy: `dep-da7s4v3l550s73cusqv0` (`8a46b96`)
- URL: `https://nightingale-shared-care-note.onrender.com`

## Transport encryption

Observed from the deployed service:

- `http://nightingale-shared-care-note.onrender.com/health` returned `301` to the HTTPS URL.
- `https://nightingale-shared-care-note.onrender.com/health` returned `200` with the expected
  health JSON.
- Chrome loaded the HTTPS application root without a certificate warning.

Render documents fully managed TLS certificates for `onrender.com` services and automatic HTTP to
HTTPS redirects: [Render managed TLS](https://render.com/docs/tls). This provider-level control,
combined with the observed redirect and HTTPS response, supports the prototype's TLS-in-transit
requirement. No custom domain or certificate-management claim is made.

## Database encryption and connection boundary

The Render Dashboard showed the existing database as **available**, **Free**, **PostgreSQL 18**,
**Singapore**, with **1 GB** storage. The Blueprint supplies its connection string to the web
service; the database URL is never stored in this repository or exposed in this record.

Render's official Postgres documentation states that Render Postgres databases and backups use
AES-256 encryption at rest, and that external database connections use Render-managed TLS:
[Create and connect to Render Postgres](https://render.com/docs/postgresql-creating-connecting).
The deployed application used the internal Render service/database connection path, and its
startup log reported `Context impl PostgresqlImpl`.

This is provider documentation plus dashboard resource evidence, not an independent cryptographic
audit. The Free database is temporary and intended only for evaluation.

## Application security observations

- The deployed `render.yaml` sets `COOKIE_SECURE=true`, an HTTPS-only `ALLOWED_ORIGINS` value,
  `LLM_PROVIDER=fixture`, and `VOICE_PROVIDER=fixture`.
- Startup validates production settings before migration and seed.
- The public unauthenticated `/auth/me` endpoint returned `401`.
- The sign-in screen was served from the same-origin FastAPI SPA.
- The authenticated clinician smoke opened Comments, kept the drawer visible beyond 5 seconds,
  loaded an existing PostgreSQL comment record, and closed it only through the explicit close
  control. Render logs showed `/entries/{entry_id}/comments` returning `200 OK`.
- Opening Comments did not create a new `/patients/{patient_id}/events` request in the observed
  Render log window, consistent with the stable EventSource lifecycle fix.
- Render startup logs contained migration/status/request metadata and synthetic seed counts only;
  no raw note text or provider response content was observed.
- The live successful login/`Set-Cookie` path was not exercised because the seed password is a
  platform-generated secret that was intentionally not read or transmitted by this audit.
  Local secure-cookie fail-closed tests remain the evidence for that application control.

## Migration and seed evidence

The successful Render deploy log recorded:

- Alembic PostgreSQL implementation and all revisions through `0010_postgres_compat`.
- `Application startup complete` and repeated `GET /health 200 OK` checks.
- Stable synthetic seed counts: 2 clinics, 2 patients, 5 users, 7 entries, 2 comments, 5
  highlights, 5 Glance items, 1 archival summary, and 2 archival sources.

The independent GitHub Actions PostgreSQL 18 gate also passed the full upgrade, downgrade/re-upgrade,
schema/FK, seed-idempotency, `alembic check`, and 82-test regression path:
[workflow run 33032765274](https://github.com/jyc114514/nightingale-shared-care-note/actions/runs/33032765274).

## Remaining limits

- No real PHI, clinical data, or live DeepSeek/Voice provider is part of this deployment.
- Backup/restore, retention/deletion, incident response, and operational access review were not
  independently exercised.
- The service uses Render Free capacity and is not a clinical production deployment.
