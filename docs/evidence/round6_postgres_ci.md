# Round 6 external PostgreSQL 18 CI evidence

Status: **code gate passed; final evidence-commit gate is still required before the
`real-clinic-rc2` tag is created.** This record covers the authorized external CI action only.

## Scope and boundary

- Repository: `jyc114514/nightingale-shared-care-note`.
- Branch pushed: `codex/real-clinic-safety` only.
- No `main` push, pull request, Render deploy, production database access, or tag push was used
  in the code-gate phase.
- The workflow uses a disposable PostgreSQL 18 service, Python 3.12, locked backend dependencies,
  synthetic CI values, fixture AI, and Voice disabled. It contains no production credential.
- The baseline tag `72h-submission` and local `real-clinic-rc1` were not moved.

## Attempt history

| Attempt | Commit | GitHub Actions run | Result | Root cause / action |
| --- | --- | --- | --- | --- |
| 1 | `6de7f0c35e1668a063f13b079a3ef4f6b8aae059` | `33591652918` | failed | CI reached the backend static gate; mypy reported the optional `faster_whisper` import as `import-not-found`. |
| 2 | `2af8073536817fa5f2a19a02d25bd069fa8d5803` | `33592195446` | passed | Corrected only the mypy ignore code in `backend/app/voice/providers.py`; no runtime, dependency, migration, or data-model change. |

Run 2: [GitHub Actions run 33592195446](https://github.com/jyc114514/nightingale-shared-care-note/actions/runs/33592195446)

The second run was a push-triggered run for the exact commit `2af8073`, completed successfully in
about 2 minutes 26 seconds. GitHub reported a Node.js 20 action deprecation annotation for the
existing checkout/setup actions; it did not fail the job.

## PostgreSQL gate coverage

The successful run passed all steps in the single PostgreSQL 18 job:

1. Install `backend/requirements.lock` under Python 3.12.
2. Run `alembic upgrade head` through `0014_patient_publications` on a fresh PostgreSQL database.
3. Run `alembic check`.
4. Downgrade to `0013_ai_provider_resilience`, re-upgrade to head, and run `alembic check` again.
5. Inspect the expected tables, publication columns, PostgreSQL indexes/FKs, and the widened
   Alembic version column.
6. Run the synthetic seed twice and verify stable safe counts, including publication rows and
   publication evidence.
7. Run the complete backend regression and Round 1–4 safety suite.
8. Run Ruff check/format, mypy, and `pip check`.

This is the first real PostgreSQL execution evidence for the complete `0001`–`0014` chain. The
workflow did not use SQLite as a fallback and did not connect to the Render database.

## Local validation boundary

The current PowerShell session had no existing `ai_env` or PATH Python interpreter. An isolated
`uv` Python 3.12 attempt confirmed that the original `faster_whisper` mypy error was gone, but the
local temporary environment itself had unrelated missing `traitlets` typing imports and a Ruff
wrapper failure. Those local limitations are not represented as local full-suite success; the
authoritative clean-environment result is the successful GitHub Actions run above.

## Next gate

The documentation-only evidence commit must be pushed to the same branch and must pass a new
exact-SHA PostgreSQL 18 run. Only after that final run may `real-clinic-rc2` be created and pushed.
Render remains outside Round 6.
