# Local Bonus and Phase 7 evidence - 2026-08-26

This record covers local synthetic implementation only. It does not claim hosted PostgreSQL,
external LLM, TLS, encryption-at-rest, deployment, or real patient data.

## Backend

- Python 3.10.20 in the pre-existing `ai_env`; pip check passed.
- Alembic head: `0008_collaboration_events`.
- Full backend suite: **51 passed**; reproducible coverage: **88%**.
- Ruff check/format and `mypy app tests`: passed.
- Requirements SHA-256 remains
  `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5`.

## Bonus and optional collaboration

- Adaptive importance remains clinic-scoped, idempotent, bounded, and separate from risk/provenance.
- Hybrid hot/warm/cold context preserves canonical source pointers and protection overrides.
- Mentions validate stable active same-clinic user IDs and deduplicate comment-user pairs.
- Assignments validate same-clinic staff/clinician assignees, preserve source pointers, support CAS
  status updates, and materialize open actions into Glance.
- SSE events persist only resource identifiers/kinds and actor metadata; no raw title, note,
  comment, quote, patient name, identifier, phone, or secret is sent in the stream.

## Browser and performance

- Vitest: **14 passed**.
- Playwright: **10 passed** at desktop `1440x900` and mobile `390x844`.
- The real-TCP warm-path benchmark on `3129da3` measured P50 49.774 ms, P95 67.823 ms, P99
  80.593 ms, max 86.835 ms, and zero errors.
