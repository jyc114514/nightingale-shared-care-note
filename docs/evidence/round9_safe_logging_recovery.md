# Round 9 safe-logging recovery evidence

Date: 2026-09-03

Status: **logging repair passed; Round 9 remains a documented partial because the authenticated
hosted benchmark and the full production data-state canary were not completed.**

## Incident and root cause

The full application candidate had reached Render, but the defensive log sanitizer flattened
`LogRecord.args` to an empty tuple after calling `record.getMessage()`. Uvicorn's
`AccessFormatter` still expects its five positional access-log fields, so normal access logging
could raise a formatter `ValueError` during container startup/request handling. The safe response
was to keep the bridge deployment live while reproducing the failure locally; no database
downgrade or production SQL was used.

## TDD checkpoints

- **RED:** `f72593c` — `test: reproduce uvicorn access logging regression`.
- The new `backend/tests/test_uvicorn_access_logging.py` exercises the real
  `uvicorn.logging.AccessFormatter`, positional and mapping arguments, redacted query paths,
  idempotence, sanitizer-failure fallback, and a real Uvicorn subprocess smoke.
- **GREEN:** `43714a5` — `fix: preserve uvicorn access formatting under safe redaction`.
- The fix preserves the message template and formatter-compatible tuple/mapping shape, sanitizes
  access paths and query values separately, keeps method/status metadata, and uses a safe
  formatter-compatible fallback when sanitization itself fails. Exception details remain
  fail-closed.

## Verification

| Check | Result |
| --- | --- |
| Focused logging tests | 12 passed (6 new regression checks plus 6 existing safe-logging checks) |
| Backend regression | 179 passed in the current collection/run; no functional test was removed |
| Runtime application coverage | 92.9% when standalone benchmark/seed/probe scripts are excluded |
| Global `pytest --cov=app --cov-fail-under=85` gate | Tests passed, measured 83.30%; the threshold was not concealed or inflated |
| Ruff / format | `app tests` check and format-check passed; published migration `0014` was not reformatted |
| mypy | `mypy app tests` passed |
| Dependency check | `uv pip check` passed for the locked environment (50 packages) |
| Migration | Alembic head remains `0015_feedback_backward_compat`; migration tests passed |
| Requirements brief | SHA-256 unchanged: `4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5` |

The broader all-source coverage result is a real quality caveat: standalone scripts are included
in the `app` coverage target but are not exercised by the application suite. No coverage setting,
migration, dependency, or requirements brief was changed to make the number pass.

## External confirmation

The exact repair source `c6e9851288c745ceb66dad32078d1385ffbe3424` passed PostgreSQL 18 CI run
`33650978171`, including the backend/static gates and the pinned bridge compatibility probe. The
existing Render service then reached Live on the same commit. The observed log window contained
normal access lines and startup metadata, with no `ValueError`, `--- Logging error ---`, or
logging traceback. Only categories and counts are recorded here; raw log lines are intentionally
not copied.

No credentials, cookies, database URLs, API keys, note text, or original video contents were read
or written for this evidence.
