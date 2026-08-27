# Render deployment attempt - 2026-08-27

## Outcome

**Blocked after two meaningful deployment attempts.** The existing Render Blueprint created
exactly one Free Web Service and one Free Postgres database. No second resource pair, paid
resource, billing change, custom domain, worker, Redis, or destructive database operation was
created or performed. The repository and Render service remain private.

The deployment track is stopped at the two-attempt boundary required by the Phase 9 handoff. No
third source push or manual redeploy was triggered.

## Resources and source

- Blueprint: `exs-da7p448n74is73a07s0g`
- Web Service: `nightingale-shared-care-note` (`srv-da7p56s9v7es73f7n12g`), Free, Singapore
- Postgres: `nightingale-shared-care-note-db`, Free, Singapore, available in the Render dashboard
- Reserved service URL: `https://nightingale-shared-care-note.onrender.com`
- Private GitHub source: `jyc114514/nightingale-shared-care-note`, branch `main`
- Repair commit pushed before attempt 2: `9fe8c40` (`fix: make Gate B migration PostgreSQL safe`)

The URL is recorded as a service address only. It is **not** a successful application URL:
neither deployment reached a healthy running service, so no hosted smoke or production cookie
claim is made.

## Attempt 1

- Deploy ID: `dep-da7p5749v7es73f7n450`
- Source: `a4d7bd6`
- Trigger: Blueprint
- Result: failed while running the application after the Docker image build completed
- Blocker: `0002_gate_b` used `batch_alter_table("entries", recreate="always")`. PostgreSQL
  could not drop `entries_pkey` because foreign keys in `entry_versions`, `conflicts`, and
  `comments` depended on it.

## Attempt 2

- Deploy ID: `dep-da7p9o7lk1mc738bdor0`
- Source: `9fe8c40`
- Trigger: Auto-Deploy from the pushed repair commit
- Result: failed while running the application after 43.7 seconds
- Blocker: after the `entries` path was changed to in-place PostgreSQL `ALTER COLUMN`, the
  subsequent PostgreSQL `comments` batch recreate dropped the original `comments_pkey` before
  creating `_alembic_tmp_comments`. Its self-referential foreign key
  `parent_comment_id REFERENCES comments(id)` then failed with:
  `psycopg.errors.InvalidForeignKey: there is no unique constraint matching given keys for
  referenced table "comments"`.

This is a migration implementation blocker, not evidence that the application or PostgreSQL
schema is production-ready. The next repair would need a PostgreSQL-specific in-place comments
path while preserving the SQLite batch path; it was intentionally not attempted in this phase
because the two-attempt limit has been reached.

## Local evidence before the repair

- Focused migration and production-readiness tests: 7 passed.
- Ruff check: passed.
- mypy: passed.
- The patched migration file passed its individual Ruff format check.
- Offline PostgreSQL generation showed the repaired `entries` statements as in-place
  `ALTER COLUMN ... SET NOT NULL`; full offline generation cannot render the existing live-
  reflection comments batch and therefore is not treated as deployment evidence.

## Security boundary

No deployment secret, database connection string, API key, raw note, patient identifier, or
credential was written to the repository or included in this record. Because no deployment
reached health, there is no valid evidence yet for HTTPS smoke, secure cookie behavior against the
live app, successful Alembic head, seed execution, or encryption-at-rest. `PRIV-04` remains
**planned**. Do not create `deployment_security.md` until a healthy deployment supplies those
facts.
