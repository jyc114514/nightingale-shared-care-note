# Gate B browser workflows

`pnpm e2e` starts a real temporary Alembic-migrated SQLite database, runs the synthetic seed,
starts Uvicorn and Vite on clean local ports, and runs the 16 core workflow checks at desktop and
mobile viewports. The separate `pnpm e2e:voice` command
uses the same isolated setup for the four Voice fixture checks, so Voice-created entries cannot
change the serial state assumptions of the core scenarios:

- Scenario A: clinician Glance item action/risk/status, collapsed “Why ranked?” contributions,
  pin/unpin feedback, exact immutable source, `<mark>` quote, source entry/version, URL deep-link
  refresh, accept, and reject.
- Scenario B: staff edit/version increment, diff, revert-as-new-version, contextual comments/task
  drawers, nested root/reply comments, resolve, and unresolve.
- Scenario C: a real stale `expected_version` write returns `409`; the UI shows current and
  preserved attempted content as an optimistic conflict, then refreshes Historical context and
  shows the derived summary disclosure/source-pointer path, distinct from a clinical conflict.
- Scenario D: the protected allergy conflict card shows its floor and protected-feedback notice;
  Staff receives a read-only dual-source drawer, source navigation replaces the selected source,
  two Clinician pages race the same decision version and expose one refreshed `409`, and a Patient
  receives neither conflict data nor impression/assertion API access.
- Patient privacy: cookie patient sees only patient-facing entries; direct internal Glance access
  is denied and no raw AI/internal comment is rendered.

The Demo preview check verifies same-origin embedded Desktop 1440x900 and Mobile 390x844
internal viewports, query/auth preservation, no recursive toolbar, no host overflow, and Escape
close.

The current core run completed 16 passed tests: eight scenarios in each of the 1440x900 and
390x844 projects. The current Voice run completed four passed tests: clinical and patient fixture
flows at both viewports. Scenario B includes keyboard mention autocomplete, assignment/task
creation and completion, and a second browser receiving metadata-only SSE invalidation. Scenario
D includes the protected conflict source drawer, clinician CAS competition, and patient API
denials. The global setup
records only the PIDs it started; teardown stops those exact process trees before removing
temporary files.

The temporary demo password is generated at test setup and written only to the ignored
`frontend/test-results/gate-b/e2e-password.txt`; teardown removes it together with the database.
Screenshots are written to the ignored `artifacts/gate-b/` folder for the 1440x900 and 390x844
projects.
