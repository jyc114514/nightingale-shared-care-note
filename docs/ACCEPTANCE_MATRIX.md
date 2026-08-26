# Nightingale acceptance matrix

Status values: `verified requirement`, `planned`, `in progress`, `passed`, `deferred`, `dropped`.

| ID | Requirement / risk | Class | Planned evidence | Current status |
| --- | --- | --- | --- | --- |
| UX-01 | Glance View readable and actionable in under 10 seconds | Mandatory | Six-or-fewer-item UI, timed demo script, usability screenshot/video | in progress |
| UX-02 | Top Card includes content, open actions, and explicit flags | Mandatory | Seed scenario plus explicit action/risk/status UI assertions | passed |
| UX-03 | Continuous time-ordered longitudinal timeline | Mandatory | Timeline API ordering test and demo | passed |
| DATA-01 | Manual, system, patient, clinician, and staff entry metadata | Mandatory | Current immutable-version author/owner assertions in [test_gate_b_api.py](../backend/tests/test_gate_b_api.py) | passed |
| AI-01 | Three distinct system-authored AI-scribed entry types | Mandatory | Seed/ingestion test for doctor, nurse, and patient session types | passed |
| COL-01 | Threaded comments with resolve/unresolve | Mandatory | Nested-tree API/UI assertions and Scenario B root/reply/resolve/unresolve | passed |
| COL-02 | Mentions | Optional | Clinic-scoped stable-user API, keyboard autocomplete, and Scenario B E2E | passed |
| COL-03 | Assignment | Optional | Clinic-scoped task API, CAS/projection tests, and Scenario B E2E | passed |
| REV-01 | Full snapshots and version increment | Mandatory | [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| REV-02 | View changes since version/date | Mandatory | Diff API assertion in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| REV-03 | Revert to prior content without erasing history | Mandatory | Revert/version assertions in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| AUD-01 | Who changed what, metadata-only audit log | Mandatory | Audit metadata/content exclusion assertion in [`test_revision_history.py`](../backend/tests/test_revision_history.py) | passed |
| PROV-01 | Every highlight has resolvable provenance | Mandatory | `test_highlight_provenance.py` | passed |
| PROV-02 | Click jumps to exact entry/span | Mandatory | Codepoint exact-span, immutable-version, deep-link, and Playwright source assertions | passed |
| TRUST-01 | AI suggestions visibly distinct and accept/rejectable | Mandatory | Backend review authorization and frontend role-control tests | passed |
| TRUST-02 | Semantic conflict is flagged or clinician-adjudicated | Mandatory | Conflict-review fixture, source preservation, and UI warning state | passed |
| AUTH-01 | Patient sees summaries/instructions only | Mandatory | Patient response-field and raw-AI denial assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-02 | Staff and clinician cannot write/edit as each other | Mandatory | Cross-role write assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-03 | Staff/clinician/admin access is clinic-scoped | Mandatory | Cross-clinic and admin scope assertions in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| AUTH-04 | Enforcement is server-side, not UI-only | Mandatory | Direct unauthorized API calls in [`test_rbac_scope.py`](../backend/tests/test_rbac_scope.py) | passed |
| CONC-01 | Different-section concurrent writes do not overwrite | Mandatory | Independent-session parallel writes in [`test_concurrent_edits.py`](../backend/tests/test_concurrent_edits.py) | passed |
| CONC-02 | Same-section stale write has deterministic resolution | Mandatory | `409` plus preserved conflict assertion in [`test_concurrent_edits.py`](../backend/tests/test_concurrent_edits.py) | passed |
| PRIV-01 | Synthetic data only | Mandatory | Seed provenance and repository scan | passed |
| PRIV-02 | Names, IC/ID, phones redacted before external LLM | Mandatory | [test_redaction.py](../backend/tests/test_redaction.py), provider spy, and fail-closed job test | passed |
| PRIV-03 | Clean logs; raw note content absent | Mandatory | [test_ai_processing.py](../backend/tests/test_ai_processing.py) caplog/audit/job safety assertions | passed |
| PRIV-04 | TLS in transit and encryption at rest | Mandatory | Deployment-provider evidence and explicit local limitation | planned |
| PERF-01 | Warm Glance View P95 <= 300 ms | Mandatory | [Gate C real-TCP benchmark](evidence/gate_c_warm_path.md) on feature-freeze `3129da3` reports P95 67.823 ms; local SQLite approximation limitation documented | passed |
| BONUS-01 | Feedback increases priority of similar future content | Bonus | `test_self_learning_importance.py` with before/after scores | passed |
| BONUS-02 | Hybrid hot/warm/cold retrieval with source preservation | Bonus | Schema, policy, fixture, and architecture demo | passed |
| BONUS-03 | Ambient patient/clinical voice capture | Bonus | Only after all mandatory gates | dropped by default |
| DEL-01 | Working Git repository with clear history | Deliverable | Clean clone and log inspection | passed |
| DEL-02 | README setup/run/security/redaction explanation | Deliverable | Clean-machine rehearsal | passed |
| DEL-03 | 2–3 page technical brief with diagram/schema/trade-offs | Deliverable | PDF render and visual inspection | passed |
| DEL-04 | `ATTRIBUTION.txt` with libraries/models/licenses | Deliverable | Dependency/license audit | passed |
| DEL-05 | Demo video covers Scenarios A–C | Deliverable | Script checklist and final playback | in progress |

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
| GATE-B-MIGRATION | Alembic `0002_gate_b` plus corrective `0003_gate_b_repair` preserve fresh and legacy upgrade paths; upgrade/check/downgrade/re-upgrade pass without `create_all` | passed | [0002_gate_b.py](../backend/migrations/versions/0002_gate_b.py), [0003_gate_b_repair.py](../backend/migrations/versions/0003_gate_b_repair.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| GATE-B-TIMELINE | Timeline orders by `occurred_at DESC, id DESC`; seed contains doctor, nurse, and patient-session AI-scribed sources with non-empty references | passed | [gate_b.py](../backend/app/api/routes/gate_b.py), [test_gate_b_api.py](../backend/tests/test_gate_b_api.py), [seed_demo.py](../backend/app/scripts/seed_demo.py) |
| GATE-B-PROVENANCE | Twelve focused checks cover manual/AI highlights, source IDs, exact slices, SHA-256, Unicode offsets, immutable versions, invalid/cross-source/cross-clinic/patient cases | passed | [test_highlight_provenance.py](../backend/tests/test_highlight_provenance.py), [highlights.py](../backend/app/services/highlights.py) |
| GATE-B-GLANCE | Internal Glance API caps at six, has deterministic priority ordering, keeps display priority separate from risk level, and excludes rejected/superseded items | passed | [test_gate_b_api.py](../backend/tests/test_gate_b_api.py), [App.tsx](../frontend/src/App.tsx) |
| GATE-B-COMMENTS | Same-entry threaded comments, reply parent validation, resolve/unresolve, metadata-only audit, and patient denial are exercised | passed | [comments.py](../backend/app/api/routes/comments.py), [test_gate_b_api.py](../backend/tests/test_gate_b_api.py) |
| GATE-B-TRUST | Clinicians can review suggestions; staff are denied review; conflict-review status preserves the source and remains visible to internal users | passed | [test_highlight_provenance.py](../backend/tests/test_highlight_provenance.py), [App.tsx](../frontend/src/App.tsx) |
| GATE-B-BROWSER | Real cookie login, `/auth/me`, patient list, source navigation, history/edit/comments, and patient privacy states pass at desktop and mobile viewports | passed | [App.test.tsx](../frontend/tests/App.test.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts), ignored [gate-b screenshots](../artifacts/gate-b/) |
| GATE-B-SECURITY | Production secure-cookie fail-closed validation and foreign-Origin write rejection pass; SQLite test pool releases temporary files | passed | [config.py](../backend/app/config.py), [dependencies.py](../backend/app/api/dependencies.py), [test_gate_b_api.py](../backend/tests/test_gate_b_api.py) |
| GATE-B-UX | Human timed under-10-second checklist and final usability review are still pending | in progress | [gate-b README](../frontend/tests/e2e/README.md) |

The browser run completed `8 passed` using real Uvicorn, real Vite, a migrated file-backed SQLite
database, and synthetic seed data at 1440x900 and 390x844. It covered exact source/deep-link/
review, diff/revert/thread, real stale-write conflict, and patient privacy. Teardown removed
ports 8000/5173 and the temporary database. The earlier exploratory timing remains recorded in
[gate_b_warm_path.md](evidence/gate_b_warm_path.md); Gate C now owns the materialized warm-path
benchmark and evidence.

## Phase 2.5 / Gate B closeout evidence - 2026-08-25

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| GATE-B-CLOSEOUT-MIGRATION | Legacy 0001 index drift is repaired by 0003 without editing 0001/0002; `alembic check` is clean after fresh and stamped legacy upgrades | passed | [0003_gate_b_repair.py](../backend/migrations/versions/0003_gate_b_repair.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| GATE-B-CLOSEOUT-METADATA | Timeline serializes immutable current-version author role/id separately from owner role; review timestamps use current UTC and audit actions distinguish accepted/rejected | passed | [gate_b.py](../backend/app/api/routes/gate_b.py), [highlights.py](../backend/app/services/highlights.py), [test_gate_b_api.py](../backend/tests/test_gate_b_api.py), [test_highlight_provenance.py](../backend/tests/test_highlight_provenance.py) |
| GATE-B-CLOSEOUT-PROVENANCE | Frontend validates Array.from codepoint spans with no indexOf fallback, renders immutable source version in Timeline, and restores patient/highlight URL links | passed | [App.tsx](../frontend/src/App.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts) |
| GATE-B-CLOSEOUT-TRUST-UI | Top Card visibly shows item kind/status/risk/action/source/priority; nested comments and conflict comparison are browser-tested | passed | [App.tsx](../frontend/src/App.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts) |

## Phase 3 / Gate C local evidence - 2026-08-25

These rows establish the local synthetic boundary only. They do not claim external-provider,
hosted PostgreSQL, TLS, or encryption-at-rest evidence.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| GATE-C-MIGRATION | `0004_gate_c` creates processing jobs and materialized Glance rows, backfills existing highlights, and leaves `alembic check` clean | passed | [0004_gate_c.py](../backend/migrations/versions/0004_gate_c.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| GATE-C-REDACTION | Known synthetic names, SG IDs/FIN/NRIC/IC, phone formats, stable tokens, second-detector fail-closed behavior, and no-provider-on-failure are tested | passed | [redaction.py](../backend/app/ai/redaction.py), [test_redaction.py](../backend/tests/test_redaction.py), [test_ai_processing.py](../backend/tests/test_ai_processing.py) |
| GATE-C-PROVIDER | Typed `RedactedPayload` boundary, deterministic fixture provider, spy payload inspection, schema validation, malformed/unavailable failure paths pass without external network/API keys | passed | [provider.py](../backend/app/ai/provider.py), [schemas.py](../backend/app/ai/schemas.py), [test_ai_provider_boundary.py](../backend/tests/test_ai_provider_boundary.py), [test_ai_processing.py](../backend/tests/test_ai_processing.py) |
| GATE-C-JOBS | Three interaction types create new system-authored AI entries and suggested exact immutable highlights; idempotency prevents duplicates; patient mutation/read is denied | passed | [ai_processing.py](../backend/app/services/ai_processing.py), [ai_processing.py](../backend/app/api/routes/ai_processing.py), [test_ai_processing.py](../backend/tests/test_ai_processing.py) |
| GATE-C-MATERIALIZED | Glance reads only `patient_glance_items`, remains capped/ordered/filtered, retains source IDs/offset/hash, and makes zero provider calls | passed | [glance.py](../backend/app/services/glance.py), [gate_b.py](../backend/app/api/routes/gate_b.py), [test_materialized_glance.py](../backend/tests/test_materialized_glance.py) |
| GATE-C-LOGS | Job/audit metadata excludes raw note/comment/provider content; provider failure and validation paths expose only safe error codes; caplog sentinel checks pass | passed | [test_ai_processing.py](../backend/tests/test_ai_processing.py), [test_highlight_provenance.py](../backend/tests/test_highlight_provenance.py) |
| GATE-C-PERF | Real Uvicorn TCP benchmark: 50 warm-up, 1,000 samples, concurrency 10, 26 patients, 208 benchmark rows, zero errors, P50 49.774 ms, P95 67.823 ms, P99 80.593 ms, max 86.835 ms, six items | passed | [gate_c_warm_path.md](evidence/gate_c_warm_path.md), [gate_c_warm_path.json](evidence/gate_c_warm_path.json), [benchmark_warm_path.py](../backend/app/scripts/benchmark_warm_path.py) |

## Phase 4A / Bonus adaptive importance evidence - 2026-08-26

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| BONUS-01-SCHEMA | Alembic `0005_gate_d_importance` adds append-only feedback events, rebuildable clinic-scoped profiles, and persisted ranking contribution fields without changing prior migrations; migration tests pass | passed | [0005_gate_d_importance.py](../backend/migrations/versions/0005_gate_d_importance.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| BONUS-01-SCORE | Structured feature signatures, bounded positive/negative updates, idempotency, clinic isolation, and separation from risk/provenance pass against the real API | passed | [importance.py](../backend/app/services/importance.py), [test_self_learning_importance.py](../backend/tests/test_self_learning_importance.py) |
| BONUS-01-UI | Glance cards expose a collapsed “Why ranked?” explanation and role-aware pin/unpin feedback; desktop/mobile browser checks pass | passed | [App.tsx](../frontend/src/App.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts) |

## Phase 4B / Hybrid archival context evidence - 2026-08-26

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| BONUS-02-SCHEMA | Alembic `0006_gate_d_archival` adds rebuildable archival summaries and composite source pointers; fresh, downgrade/re-upgrade, legacy upgrade, and `alembic check` paths pass | passed | [0006_gate_d_archival.py](../backend/migrations/versions/0006_gate_d_archival.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| BONUS-02-POLICY | Deterministic 14-day hot / 90-day cold policy, manifest hash, stable period upsert, and protection overrides keep open actions, risk, conflicts, discussion, pinned/accepted, and care-plan sources out of cold summaries | passed | [archival.py](../backend/app/services/archival.py), [test_data_decay.py](../backend/tests/test_data_decay.py) |
| BONUS-02-API | Context read and explicit refresh enforce clinic scope and role permissions; patient projection omits internal entries and raw AI content | passed | [context.py](../backend/app/api/routes/context.py), [test_data_decay.py](../backend/tests/test_data_decay.py) |
| BONUS-02-UI | Historical context panel discloses derived summaries and follows canonical source pointers on desktop/mobile browser paths | passed | [App.tsx](../frontend/src/App.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts) |

## Phase 7 / Delivery artifact evidence - 2026-08-26

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| DEL-01-CLEAN-CLONE | Feature-freeze checkpoint `3129da3` cloned into a fresh directory; migration, seed, launcher, backend/frontend quality, and 10 browser checks passed | passed | [clean_clone_rehearsal.md](evidence/clean_clone_rehearsal.md), [`.gitattributes`](../.gitattributes) |
| DEL-02-CLEAN-SETUP | README setup, migration-first seed, redaction boundary, local limitation, and clean-clone commands were executed successfully | passed | [README.md](../README.md), [clean_clone_rehearsal.md](evidence/clean_clone_rehearsal.md) |

| DEL-03-PDF | Three-page A4 Technical Brief generated from local HTML, rendered to raster, and visually inspected page by page; final page footer overlap was corrected and rechecked | passed | [Nightingale_Technical_Brief.pdf](../deliverables/Nightingale_Technical_Brief.pdf), [technical_brief_qa.md](evidence/technical_brief_qa.md) |
| DEL-04-AUDIT | Direct backend/frontend dependency versions and observed license metadata recorded without guessing undeclared Python licenses | passed | [ATTRIBUTION.txt](../ATTRIBUTION.txt) |
| DEL-05-SCRIPT | Scenarios A-C script, shot list, bilingual/task/SSE coverage, UX timing protocol, and synthetic browser screenshots are ready; final video still pending | in progress | [DEMO_SCRIPT.md](DEMO_SCRIPT.md), [DEMO_SHOTLIST.md](DEMO_SHOTLIST.md), [screenshots](../deliverables/screenshots/) |

## Phase 7 / usability, local demo, and collaboration evidence - 2026-08-26

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-7A-I18N | Typed English/简体中文 chrome dictionaries, URL-over-localStorage precedence, document language, source-data boundary, translated ARIA names | passed | [`frontend/src/i18n`](../frontend/src/i18n), [`App.test.tsx`](../frontend/tests/App.test.tsx) |
| PHASE-7A-GUIDE | Closed-by-default bilingual read-only Learning Guide with close/Escape behavior and UX-01 instructions | passed | [`App.tsx`](../frontend/src/App.tsx), [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) |
| PHASE-7B-LAUNCHER | Clean runtime, migration/seed/health, second-start idempotency, PID safety, logs/secret scan, safe stop, no port residue | passed | [`scripts/test_demo_launcher.ps1`](../scripts/test_demo_launcher.ps1), [`README_DEMO_LAUNCHER.md`](../scripts/README_DEMO_LAUNCHER.md) |
| PHASE-7C-MENTIONS | Active same-clinic collaborator directory, stable IDs, dedupe, cross-clinic/patient denial, metadata-only mention audit | passed | [`test_collaboration.py`](../backend/tests/test_collaboration.py), [`comments.py`](../backend/app/api/routes/comments.py) |
| PHASE-7D-TASKS | Migration 0007, task source pointers, assignee validation, status/projection, CAS conflict, patient/admin policy, Glance action | passed | [`0007_collaboration_mentions_tasks.py`](../backend/migrations/versions/0007_collaboration_mentions_tasks.py), [`tasks.py`](../backend/app/api/routes/tasks.py) |
| PHASE-7E-SSE | Migration 0008, persisted monotonic events, Last-Event-ID parser, heartbeat, scoped stream, two-browser invalidation E2E | passed | [`events.py`](../backend/app/api/routes/events.py), [`test_events.py`](../backend/tests/test_events.py), [`gate-b.spec.ts`](../frontend/tests/e2e/gate-b.spec.ts) |
| PHASE-7F-A11Y | Focus trap/return, visible focus, translated names, live status, reduced-motion scrolling, keyboard autocomplete | passed | [`App.tsx`](../frontend/src/App.tsx), [`App.test.tsx`](../frontend/tests/App.test.tsx) |

The feature-freeze regression reports backend **51 passed / 88% coverage**, frontend **14 Vitest
tests**, and **10 Playwright tests**. Warm-path evidence is the real-TCP SQLite approximation on
`3129da3`: P50 49.774 ms, P95 67.823 ms, P99 80.593 ms, max 86.835 ms, zero errors.

## Hard release gate

Do not call the build submission-ready unless every Mandatory and Deliverable row is `passed`, or an explicit limitation is documented with a deliberate scope decision. Bonus rows may be dropped without blocking release.
