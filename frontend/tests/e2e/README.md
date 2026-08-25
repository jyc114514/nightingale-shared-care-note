# Gate B browser workflows

`pnpm e2e` starts a real temporary Alembic-migrated SQLite database, runs the synthetic seed,
starts Uvicorn and Vite on clean local ports, and runs Scenario A/B against the real API. The
global setup records only the PIDs it started; teardown stops those exact process trees before
removing temporary files.

The temporary demo password is generated at test setup and written only to the ignored
`frontend/test-results/gate-b/e2e-password.txt`; teardown removes it together with the database.
Screenshots are written to the ignored `artifacts/gate-b/` folder for the 1440x900 and 390x844
projects.
