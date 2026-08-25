# Nightingale acceptance matrix

Status values: `verified requirement`, `planned`, `in progress`, `passed`, `deferred`, `dropped`.

| ID | Requirement / risk | Class | Planned evidence | Current status |
| --- | --- | --- | --- | --- |
| UX-01 | Glance View readable and actionable in under 10 seconds | Mandatory | Six-or-fewer-item UI, timed demo script, usability screenshot/video | planned |
| UX-02 | Top Card includes content, open actions, and explicit flags | Mandatory | Seed scenario plus UI/E2E assertions | planned |
| UX-03 | Continuous time-ordered longitudinal timeline | Mandatory | Timeline API ordering test and demo | planned |
| DATA-01 | Manual, system, patient, clinician, and staff entry metadata | Mandatory | Schema constraints and API serialization tests | planned |
| AI-01 | Three distinct system-authored AI-scribed entry types | Mandatory | Seed/ingestion test for doctor, nurse, and patient session types | planned |
| COL-01 | Threaded comments with resolve/unresolve | Mandatory | API test and Scenario B demo | planned |
| COL-02 | Mentions | Optional | Parser/UI smoke test | deferred |
| COL-03 | Assignment | Optional | Task ownership API/UI test | deferred |
| REV-01 | Full snapshots and version increment | Mandatory | `test_revision_history.py` | planned |
| REV-02 | View changes since version/date | Mandatory | Diff API test and demo | planned |
| REV-03 | Revert to prior content without erasing history | Mandatory | `test_revision_history.py` | planned |
| AUD-01 | Who changed what, metadata-only audit log | Mandatory | Audit assertion; scan logs for note content | planned |
| PROV-01 | Every highlight has resolvable provenance | Mandatory | `test_highlight_provenance.py` | planned |
| PROV-02 | Click jumps to exact entry/span | Mandatory | Playwright anchor/highlight test and demo | planned |
| TRUST-01 | AI suggestions visibly distinct and accept/rejectable | Mandatory | UI/E2E test | planned |
| TRUST-02 | Semantic conflict is flagged or clinician-adjudicated | Mandatory | Conflict fixture and demo | planned |
| AUTH-01 | Patient sees summaries/instructions only | Mandatory | `test_rbac_scope.py` response-field assertions | planned |
| AUTH-02 | Staff and clinician cannot write/edit as each other | Mandatory | `test_rbac_scope.py` | planned |
| AUTH-03 | Staff/clinician/admin access is clinic-scoped | Mandatory | Cross-clinic negative tests | planned |
| AUTH-04 | Enforcement is server-side, not UI-only | Mandatory | Direct unauthorized API calls | planned |
| CONC-01 | Different-section concurrent writes do not overwrite | Mandatory | `test_concurrent_edits.py` | planned |
| CONC-02 | Same-section stale write has deterministic resolution | Mandatory | `409` plus preserved conflict assertion | planned |
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

## Hard release gate

Do not call the build submission-ready unless every Mandatory and Deliverable row is `passed`, or an explicit limitation is documented with a deliberate scope decision. Bonus rows may be dropped without blocking release.
