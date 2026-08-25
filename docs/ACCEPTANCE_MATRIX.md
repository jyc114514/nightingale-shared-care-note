# Nightingale acceptance matrix

Status values: `verified requirement`, `planned`, `in progress`, `passed`, `deferred`, `dropped`.

| ID | Requirement / risk | Class | Planned evidence | Current status |
| --- | --- | --- | --- | --- |
| UX-01 | Glance View readable and actionable in under 10 seconds | Mandatory | Six-or-fewer-item UI, timed demo script, usability screenshot/video | in progress |
| UX-02 | Top Card includes content, open actions, and explicit flags | Mandatory | Seed scenario plus UI/E2E assertions | passed |
| UX-03 | Continuous time-ordered longitudinal timeline | Mandatory | Timeline API ordering test and demo | passed |
| DATA-01 | Manual, system, patient, clinician, and staff entry metadata | Mandatory | SQLAlchemy schema, synthetic seed, and API serialization in [Gate A tests](../backend/tests/test_rbac_scope.py) | passed |
| AI-01 | Three distinct system-authored AI-scribed entry types | Mandatory | Seed/ingestion test for doctor, nurse, and patient session types | passed |
| COL-01 | Threaded comments with resolve/unresolve | Mandatory | API test and Scenario B demo | passed |
| COL-02 | Mentions | Optional | Parser/UI smoke test | deferred |
| COL-03 | Assignment | Optional | Task ownership API/UI test | deferred |
| REV-01 | Full snapshots and version increment | Mandatory | [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| REV-02 | View changes since version/date | Mandatory | Diff API assertion in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| REV-03 | Revert to prior content without erasing history | Mandatory | Revert/version assertions in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| AUD-01 | Who changed what, metadata-only audit log | Mandatory | Audit metadata/content exclusion assertion in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| PROV-01 | Every highlight has resolvable provenance | Mandatory | `test_highlight_provenance.py` | passed |
| PROV-02 | Click jumps to exact entry/span | Mandatory | Playwright source navigation plus immutable-source assertions | passed |
| TRUST-01 | AI suggestions visibly distinct and accept/rejectable | Mandatory | Backend review authorization and frontend role-control tests | passed |
| TRUST-02 | Semantic conflict is flagged or clinician-adjudicated | Mandatory | Conflict-review fixture, source preservation, and UI warning state | passed |
| AUTH-01 | Patient sees summaries/instructions only | Mandatory | Patient response-field and raw-AI denial assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-02 | Staff and clinician cannot write/edit as each other | Mandatory | Cross-role write assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-03 | Staff/clinician/admin access is clinic-scoped | Mandatory | Cross-clinic and admin scope assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-04 | Enforcement is server-side, not UI-only | Mandatory | Direct unauthorized API calls in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| CONC-01 | Different-section concurrent writes do not overwrite | Mandatory | Independent-session parallel writes in [`test_concurrent_edits.py`](../backend/tests/test_concurrent_edits.py) | passed |
| CONC-02 | Same-section stale write has deterministic resolution | Mandatory | `409` plus preserved conflict assertion in [`test_concurrent_edits.py`](../backend/tests/test_concurrent_edits.py) | passed |
| PRIV-01 | Synthetic data only | Mandatory | Seed provenance and repository scan | passed |
| PRIV-02 | Names, IC/ID, phones redacted before external LLM | Mandatory | Unit/integration redaction tests with provider spy | planned |
| PRIV-03 | Clean logs; raw note content absent | Mandatory | Log-capture test and manual scan | planned |
| PRIV-04 | TLS in transit and encryption at rest | Mandatory | Deployment-provider evidence and explicit local limitation | planned |
| PERF-01 | Warm Glance View P95 <= 300 ms | Mandatory | [Exploratory Gate B timing](evidence/gate_b_warm_path.md); production/materialized-path benchmark still required | planned |
| BONUS-01 | Feedback increases priority of similar future content | Bonus | `test_self_learning_importance.py` with before/after scores | planned |
| BONUS-02 | Hybrid hot/warm/cold retrieval with source preservation | Bonus | Schema, policy, fixture, and architecture demo | planned |
| BONUS-03 | Ambient patient/clinical voice capture | Bonus | Only after all mandatory gates | dropped by default |
| DEL-01 | Working Git repository with clear history | Deliverable | Clean clone and log inspection | planned |
| DEL-02 | README setup/run/security/redaction explanation | Deliverable | Clean-machine rehearsal | planned |
| DEL-03 | 2–3 page technical brief with diagram/schema/trade-offs | Deliverable | PDF render and visual inspection | planned |
| DEL-04 | `ATTRIBUTION.txt` with libraries/models/licenses | Deliverable | Dependency/license audit | planned |
| DEL-05 | Demo video covers Scenarios A–C | Deliverable | Script checklist and final playback | planned |

## Phase 0 recorded evidence — 2026-08-25

These rows record only the repository/environment scaffold. Product requirements above remain
`planned` unless a later gate provides their evidence.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| P0-ENV | Confirmed Conda `ai_env`, safe before/after snapshots, package delta, and clean pip checks | passed | [ENVIRONMENT_REPORT.md](ENVIRONMENT_REPORT.md), [environment artifacts](../artifacts/environment/) |
| P0-BACKEND | FastAPI app, `/health`, application test, lint, format check, mypy, and live endpoint check | passed | [backend/app/main.py](../backend/app/main.py), [backend/tests/test_health.py](../backend/tests/test_health.py), [ENVIRONMENT_REPORT.md](ENVIRONMENT_REPORT.md) |
| P0-FRONTEND | React/Vite shell, backend health display, unit test, lint, type-check, and build | passed | [frontend/src/App.tsx](../frontend/src/App.tsx), [frontend/tests/App.test.tsx](../frontend/tests/App.test.tsx), [ENVIRONMENT_REPORT.md](ENVIRONMENT_REPORT.md) |
| P0-REPRO | Local Git repository, safe ignore rules, backend/frontend lockfiles, and reproducible commands | passed | [README.md](../README.md), [`.gitignore`](../.gitignore), [backend/requirements.lock](../backend/requirements.lock), [frontend/pnpm-lock.yaml](../frontend/pnpm-lock.yaml) |

## Phase 1 / Gate A recorded evidence - 2026-08-25

These rows are limited to the Gate A boundary. UX, AI, provenance, privacy redaction,
performance, and bonus rows remain planned/deferred until their own phases.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| GATE-A-MIGRATION | Real Alembic `upgrade head` created the 11-table schema on an empty temporary SQLite file | passed | [alembic.ini](../backend/alembic.ini), [0001_gate_a.py](../backend/migrations/versions/0001_gate_a.py) |
| GATE-A-SEED | Two seed runs preserved 2 clinics, 5 users, 2 patients, 7 entries, and 1 comment | passed | [seed_demo.py](../backend/app/scripts/seed_demo.py), [README.md](../README.md) |
| GATE-A-TESTS | Eight real FastAPI tests passed; coverage run reported 83% total | passed | [backend/tests](../backend/tests), [ENVIRONMENT_REPORT.md](ENVIRONMENT_REPORT.md) |
| GATE-A-ASYNC | Health and Gate A tests use HTTPX `AsyncClient` plus `ASGITransport`; no old TestClient warning | passed | [test_health.py](../backend/tests/test_health.py), [ENVIRONMENT_REPORT.md](ENVIRONMENT_REPORT.md) |

## Phase 2 / Gate B recorded evidence - 2026-08-25

These rows record the implemented Gate B boundary only. They do not imply that the later
redaction/provider/performance or delivery gates are complete.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| GATE-B-MIGRATION | Alembic `0002_gate_b` adds occurred/source metadata, threaded comment fields, and highlights; upgrade/check/downgrade/re-upgrade pass without `create_all` | passed | [0002_gate_b.py](../backend/migrations/versions/0002_gate_b.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| GATE-B-TIMELINE | Timeline orders by `occurred_at DESC, id DESC`; seed contains doctor, nurse, and patient-session AI-scribed sources with non-empty references | passed | [gate_b.py](../backend/app/api/routes/gate_b.py), [test_gate_b_api.py](../backend/tests/test_gate_b_api.py), [seed_demo.py](../backend/app/scripts/seed_demo.py) |
| GATE-B-PROVENANCE | Twelve focused checks cover manual/AI highlights, source IDs, exact slices, SHA-256, Unicode offsets, immutable versions, invalid/cross-source/cross-clinic/patient cases | passed | [test_highlight_provenance.py](../backend/tests/test_highlight_provenance.py), [highlights.py](../backend/app/services/highlights.py) |
| GATE-B-GLANCE | Internal Glance API caps at six, has deterministic priority ordering, keeps display priority separate from risk level, and excludes rejected/superseded items | passed | [test_gate_b_api.py](../backend/tests/test_gate_b_api.py), [App.tsx](../frontend/src/App.tsx) |
| GATE-B-COMMENTS | Same-entry threaded comments, reply parent validation, resolve/unresolve, metadata-only audit, and patient denial are exercised | passed | [comments.py](../backend/app/api/routes/comments.py), [test_gate_b_api.py](../backend/tests/test_gate_b_api.py) |
| GATE-B-TRUST | Clinicians can review suggestions; staff are denied review; conflict-review status preserves the source and remains visible to internal users | passed | [test_highlight_provenance.py](../backend/tests/test_highlight_provenance.py), [App.tsx](../frontend/src/App.tsx) |
| GATE-B-BROWSER | Real cookie login, `/auth/me`, patient list, source navigation, history/edit/comments, and patient privacy states pass at desktop and mobile viewports | passed | [App.test.tsx](../frontend/tests/App.test.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts), ignored [gate-b screenshots](../artifacts/gate-b/) |
| GATE-B-SECURITY | Production secure-cookie fail-closed validation and foreign-Origin write rejection pass; SQLite test pool releases temporary files | passed | [config.py](../backend/app/config.py), [dependencies.py](../backend/app/api/dependencies.py), [test_gate_b_api.py](../backend/tests/test_gate_b_api.py) |
| GATE-B-UX | Human timed under-10-second checklist and final usability review are still pending | in progress | [gate-b README](../frontend/tests/e2e/README.md) |

The browser run completed `4 passed` using real Uvicorn, real Vite, a migrated file-backed SQLite
database, and synthetic seed data at 1440x900 and 390x844. The run produced four ignored
screenshots and verified that ports 8000/5173 and the temporary database were removed by teardown.
An exploratory Gate B timing is recorded in [gate_b_warm_path.md](evidence/gate_b_warm_path.md),
but the Glance endpoint is currently a direct database-backed prototype read rather than a
measured materialized warm path; `PERF-01` therefore remains planned.

## Hard release gate

Do not call the build submission-ready unless every Mandatory and Deliverable row is `passed`, or an explicit limitation is documented with a deliberate scope decision. Bonus rows may be dropped without blocking release.
