# Render deployment security evidence - 2026-08-27

## Scope and status

This record covers the successful synthetic evaluation deployment of Nightingale. It is evidence
for the Render transport/database boundary, not a clinical compliance certification.

- Web Service: `nightingale-shared-care-note`, Free, Singapore
- Postgres: `nightingale-shared-care-note-db`, Free, Singapore, PostgreSQL 18, 1 GB
- Migration baseline deploy: `dep-da7ptlek1f9s73ch6910` (`d2a12cd`)
- Comments fix deploy: `dep-da7s4v3l550s73cusqv0` (`8a46b96`)
- Voice fixture Auto-Deploy: `dep-da7t9tjl550s73cvmhgg` (`e766fe9`), Live
- Voice fixture Blueprint sync: `dep-da7t9u0chk0s73c7dbl0` (`e766fe9`), Live
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
- The final Voice fixture configuration is deployed, but the authenticated Voice UI flow was not
  re-run because the available browser session had expired. Live Voice listing, playback,
  processing, transcript, seeking, and source navigation therefore remain user-login evidence.

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

## Authenticated browser addendum - 2026-08-27

After manual login, the existing HTTPS deployment was exercised in English with sequential
synthetic Clinical, Staff, and Patient sessions. The browser did not expose any credential,
environment value, database URL, raw log line, or provider key.

- Clinical/Staff pages showed the internal workspace, source-linked Glance cards, and
  `Live updates: Connected`.
- The Patient page showed `Internal Glance View is hidden`, only patient-facing timeline entries,
  only the patient Voice fixture, and no Comments, Assign task, History, clinical sample, or
  generated-source control.
- Render Deploys showed the existing service as `Live` on `e766fe9`. The Logs surface was checked
  by classification only; no raw Voice transcript, password/key pattern, DeepSeek, or Whisper
  claim was found.
- The authenticated Voice smoke completed the synthetic clinical and patient fixture flows. This
  proves deployed Level-C fixture wiring, not live ASR, diarization, or production PHI readiness.

The browser rehearsal also recorded a one-refresh fallback for an initially stale Comments state;
after refresh the drawer opened, remained visible beyond five seconds, and closed through its
explicit control. Full step evidence is in [`demo_rehearsal.md`](demo_rehearsal.md).

## Final release-candidate online addendum - 2026-08-27

The earlier statements that the product-language and authenticated Voice checks were pending are
historical. After the final UI correction, the existing HTTPS service was verified on the Live
`42a01b6` deployment (`dep-da84vcp5efls73dm07vg`). The preceding `1779407` deployment
(`dep-da84pac9v7es73a35t5g`) also reached Live. Both used the existing Render Web Service and
Postgres; no new resource was created.

The user manually authenticated sequential English Staff, Clinician, and Patient sessions. The
browser automation did not inspect cookies, passwords, storage, environment values, database URLs,
or provider keys.

- Staff Voice created one user-authorized synthetic suggestion. The result was `Ready for review`,
  the audio metadata was 24 seconds with `readyState=4`, transcript segment 2 sought to exactly
  `8.0` seconds, and `View source` displayed the original source plus the exact highlighted span.
- Staff Source, Comments, Task, and History opened on the final deployment. History retained the
  aligned `Current` row, and the Comments drawer showed the existing synthetic mention comment.
- Clinician showed `Clinician view`; its audio metadata was ready, History exposed `Current`,
  `Compare`, and `Revert`, Compare showed Before/After, and a Glance source opened with the
  expected highlighted quote. No Clinician write action was executed.
- Patient showed `Patient view` and `Your care summary`, only patient-facing timeline records, and
  the patient Voice sample. The player metadata was ready at 24 seconds with no media error. The
  patient DOM contained zero buttons named `Comments`, `History`, `Assign task`, `Edit`, `Accept`,
  `Reject`, `View source`, or `Open source`; no internal Glance, raw suggestion, or team discussion
  text was present.
- The final normal English workflow scan found zero occurrences of the developer/provider terms
  `Level-C`, `fixture`, `mock-transcript-fixture`, `precomputed-v1`, `Python code-point`,
  `SHA-256`, `source_entry_id`, `source_version_id`, `expected_version`, `actual_version`, `CAS`,
  `metadata-only`, `migration`, `Alembic`, `cookie session`, `Fixture suggestion`, `No action
  label`, and `No action state`.

The browser checks are product and privacy evidence for a synthetic evaluation deployment. They do
not upgrade the result to live LLM/ASR, ambient Voice, clinical production readiness, or a provider-
independent cryptographic audit.
