# Gate B browser workflows

`pnpm e2e` starts a real temporary Alembic-migrated SQLite database, runs the synthetic seed,
starts Uvicorn and Vite on clean local ports, and runs four real API scenarios at desktop and
mobile viewports:

- Scenario A: clinician Glance item action/risk/status, collapsed “Why ranked?” contributions,
  pin/unpin feedback, exact immutable source, `<mark>` quote, source entry/version, URL deep-link
  refresh, accept, and reject.
- Scenario B: staff edit/version increment, diff, revert-as-new-version, nested root/reply
  comments, resolve, and unresolve.
- Scenario C: a real stale `expected_version` write returns `409`; the UI shows current and
  preserved attempted content as an optimistic conflict, then refreshes Historical context and
  shows the derived summary disclosure/source-pointer path, distinct from a clinical conflict.
- Patient privacy: cookie patient sees only patient-facing entries; direct internal Glance access
  is denied and no raw AI/internal comment is rendered.

The current run completed 8 passed tests: four scenarios in each of the 1440x900 and 390x844
projects. The global setup records only the PIDs it started; teardown stops those exact process
trees before removing temporary files.

The temporary demo password is generated at test setup and written only to the ignored
`frontend/test-results/gate-b/e2e-password.txt`; teardown removes it together with the database.
Screenshots are written to the ignored `artifacts/gate-b/` folder for the 1440x900 and 390x844
projects.
