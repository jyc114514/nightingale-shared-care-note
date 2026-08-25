# Phase 4 Bonus evidence - 2026-08-26

This record covers the local synthetic implementation only. It does not claim hosted PostgreSQL,
external LLM, TLS, or encryption-at-rest evidence.

## Backend

- Python: 3.10.20 in the pre-existing `ai_env`; `pip check` passed.
- Alembic head: `0006_gate_d_archival`.
- `pytest`: **46 passed**.
- Coverage: **97%** (`2905` statements, `97` missed) from the full backend suite; data file was
  written under ignored `artifacts/gate-d/`.
- Ruff check, Ruff format check, and `mypy app tests`: passed.
- `requirements.txt` SHA-256 remains
  `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5`.

## Migration and seed

- Fresh upgrade, downgrade/re-upgrade, legacy-index repair, and `alembic check` passed.
- Two consecutive synthetic seed runs produced identical counts:

  - 2 clinics
  - 5 users
  - 2 patients
  - 7 entries
  - 5 highlights and 5 materialized Glance items
  - 2 comments
  - 1 archival summary and 2 archival source pointers

- Temporary SQLite files used for this check were removed after validation. Canonical entries and
  immutable entry versions were not deleted by the archival refresh.

## Frontend and browser

- Vitest: **8 passed**.
- ESLint, Prettier check, TypeScript build/type-check, and production Vite build: passed.
- Playwright: **8 passed** across desktop `1440x900` and mobile `390x844`.
- Browser evidence includes ranking explanation/pin feedback, exact immutable provenance, revision
  and conflict flows, nested comments, derived Historical context disclosure/source pointers,
  and patient projection/privacy.

## Scope boundary

Adaptive importance and archival context are deterministic local prototype logic. No raw note text,
patient identifiers, embeddings, external provider call, or API key is used by either Bonus path.
