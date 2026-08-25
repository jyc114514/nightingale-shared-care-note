# Nightingale acceptance matrix

Status values: `verified requirement`, `planned`, `in progress`, `passed`, `deferred`, `dropped`.

| ID | Requirement / risk | Class | Planned evidence | Current status |
| --- | --- | --- | --- | --- |
| UX-01 | Glance View readable and actionable in under 10 seconds | Mandatory | Six-or-fewer-item UI, timed demo script, usability screenshot/video | planned |
| UX-02 | Top Card includes content, open actions, and explicit flags | Mandatory | Seed scenario plus UI/E2E assertions | planned |
| UX-03 | Continuous time-ordered longitudinal timeline | Mandatory | Timeline API ordering test and demo | planned |
| DATA-01 | Manual, system, patient, clinician, and staff entry metadata | Mandatory | SQLAlchemy schema, synthetic seed, and API serialization in [Gate A tests](../backend/tests/test_rbac_scope.py) | passed |
| AI-01 | Three distinct system-authored AI-scribed entry types | Mandatory | Seed/ingestion test for doctor, nurse, and patient session types | planned |
| COL-01 | Threaded comments with resolve/unresolve | Mandatory | API test and Scenario B demo | planned |
| COL-02 | Mentions | Optional | Parser/UI smoke test | deferred |
| COL-03 | Assignment | Optional | Task ownership API/UI test | deferred |
| REV-01 | Full snapshots and version increment | Mandatory | [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| REV-02 | View changes since version/date | Mandatory | Diff API assertion in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| REV-03 | Revert to prior content without erasing history | Mandatory | Revert/version assertions in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| AUD-01 | Who changed what, metadata-only audit log | Mandatory | Audit metadata/content exclusion assertion in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| PROV-01 | Every highlight has resolvable provenance | Mandatory | `test_highlight_provenance.py` | planned |
| PROV-02 | Click jumps to exact entry/span | Mandatory | Playwright anchor/highlight test and demo | planned |
| TRUST-01 | AI suggestions visibly distinct and accept/rejectable | Mandatory | UI/E2E test | planned |
| TRUST-02 | Semantic conflict is flagged or clinician-adjudicated | Mandatory | Conflict fixture and demo | planned |
| AUTH-01 | Patient sees summaries/instructions only | Mandatory | Patient response-field and raw-AI denial assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-02 | Staff and clinician cannot write/edit as each other | Mandatory | Cross-role write assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-03 | Staff/clinician/admin access is clinic-scoped | Mandatory | Cross-clinic and admin scope assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-04 | Enforcement is server-side, not UI-only | Mandatory | Direct unauthorized API calls in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| CONC-01 | Different-section concurrent writes do not overwrite | Mandatory | Independent-session parallel writes in [`test_concurrent_edits.py`](../backend/tests/test_concurrent_edits.py) | passed |
| CONC-02 | Same-section stale write has deterministic resolution | Mandatory | `409` plus preserved conflict assertion in [`test_concurrent_edits.py`](../backend/tests/test_concurrent_edits.py) | passed |
| PRIV-01 | Synthetic data only | Mandatory | Seed provenance and repository scan | planned |
| PRIV-02 | Names, IC/ID, phones redacted before external LLM | Mandatory | Unit/integration redaction tests with provider spy | planned |
| PRIV-03 | Clean logs; raw note content absent | Mandatory | Log-capture test and manual scan | planned |
| PRIV-04 | TLS in transit and encryption at rest | Mandatory | Deployment-provider evidence and explicit local limitation | planned |
| PERF-01 | Warm Glance View P95 <= 300 ms | Mandatory | Reproducible benchmark JSON/Markdown artifact | planned |
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

## Hard release gate

Do not call the build submission-ready unless every Mandatory and Deliverable row is `passed`, or an explicit limitation is documented with a deliberate scope decision. Bonus rows may be dropped without blocking release.
