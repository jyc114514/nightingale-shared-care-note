# Nightingale acceptance matrix

Status values: `verified requirement`, `planned`, `in progress`, `passed`,
`passed with disclosed prototype boundary`, `deferred`, `dropped`.

| ID | Requirement / risk | Class | Planned evidence | Current status |
| --- | --- | --- | --- | --- |
| UX-01 | Glance View readable and actionable in under 10 seconds | Mandatory | Independent Simplified Chinese participant result: approximately 9 seconds, no coaching, four defined answers correct | passed |
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
| PRIV-04 | TLS in transit and encryption at rest | Mandatory | Render HTTPS redirect/health smoke, managed TLS documentation, and Render Postgres AES-256-at-rest documentation in [deployment_security.md](evidence/deployment_security.md) | passed |
| PERF-01 | Warm Glance View P95 <= 300 ms | Mandatory | [Gate C real-TCP benchmark](evidence/gate_c_warm_path.md) release-candidate run reports P95 56.053 ms; local SQLite approximation limitation documented | passed |
| BONUS-01 | Feedback increases priority of similar future content | Bonus | `test_self_learning_importance.py` with before/after scores | passed |
| BONUS-02 | Hybrid hot/warm/cold retrieval with source preservation | Bonus | Schema, policy, fixture, and architecture demo | passed |
| BONUS-03 | Ambient patient/clinical voice capture | Bonus | Level-C prerecorded synthetic audio and mock transcript evidence; full capture remains out of scope | in progress |
| DEL-01 | Working Git repository with clear history | Deliverable | Clean clone and log inspection | passed |
| DEL-02 | README setup/run/security/redaction explanation | Deliverable | Clean-machine rehearsal | passed |
| DEL-03 | 2–3 page technical brief with diagram/schema/trade-offs | Deliverable | PDF render and visual inspection | passed |
| DEL-04 | `ATTRIBUTION.txt` with libraries/models/licenses | Deliverable | Dependency/license audit | passed |
| DEL-05 | Demo video covers Scenarios A–C | Deliverable | [Final video QA](evidence/final_demo_video_qa.md): user-supplied original MP4; content QA explicitly waived by the user in the final release pass | passed with disclosed prototype boundary |

Current total: **Mandatory 25/25 passed**. Deliverables: **5/5 present**, with DEL-05 marked
`passed with disclosed prototype boundary`: the original MP4 was supplied by the user and its
content QA was explicitly waived for this pass. This is not a claim that Codex watched the video.

Round 4 adds a separate adversarial safety record for Scenario 12; it does not silently convert
the bounded portal gate into a general clinical or delivery claim.

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
| GATE-B-UX | Human timed under-10-second checklist is closed by an independent Simplified Chinese participant result; automated desktop/mobile checks remain separate | passed | [UX-01 evidence](evidence/ux_01_independent_test.md), [UX test protocol](UX_10_SECOND_TEST.md) |

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

| DEL-03-PDF | Phase 7.1 three-page A4 Technical Brief generated from local HTML, rendered to raster, and visually inspected page by page; final page footer overlap was corrected and rechecked | passed | [Nightingale_Technical_Brief.pdf](../deliverables/Nightingale_Technical_Brief.pdf), [technical_brief_qa.md](evidence/technical_brief_qa.md) |
| DEL-04-AUDIT | Direct backend/frontend dependency versions and observed license metadata recorded without guessing undeclared Python licenses | passed | [ATTRIBUTION.txt](../ATTRIBUTION.txt) |
| DEL-05-SCRIPT | Scenarios A-C script, shot list, bilingual/task/SSE/drawer/preview coverage, UX timing protocol, and synthetic browser screenshots are ready; final video still pending | in progress | [DEMO_SCRIPT.md](DEMO_SCRIPT.md), [DEMO_SHOTLIST.md](DEMO_SHOTLIST.md), [screenshots](../deliverables/screenshots/) |

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

## Phase 7.1 / observed UX fixes and demo preview evidence - 2026-08-26

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-7.1-SOURCE | Application checkpoint `30a90bf` keeps Unicode codepoint slicing, immutable v1/current v3 distinction, and full rendered text equality; horizontal padding was removed without changing provenance fields | passed | [`App.tsx`](../frontend/src/App.tsx), [`App.test.tsx`](../frontend/tests/App.test.tsx), [`gate-b.spec.ts`](../frontend/tests/e2e/gate-b.spec.ts) |
| PHASE-7.1-CONTEXT | Derived summaries now disclose that they are not original records and show localized entry type, occurred time, immutable version, source order, and distinct View original record controls | passed | [`context.py`](../backend/app/api/routes/context.py), [`App.tsx`](../frontend/src/App.tsx), [`test_data_decay.py`](../backend/tests/test_data_decay.py) |
| PHASE-7.1-COMMENTS | Comments open in a fixed desktop/mobile contextual drawer before API completion, expose loading/error states, trap Escape/focus, and return focus to the originating button | passed | [`App.tsx`](../frontend/src/App.tsx), [`App.test.tsx`](../frontend/tests/App.test.tsx), [`gate-b.spec.ts`](../frontend/tests/e2e/gate-b.spec.ts) |
| PHASE-7.1-TASKS | Assignment opens the same drawer pattern, states the entry/comment context, focuses the title, keeps task errors inside the drawer, and returns focus on close | passed | [`App.tsx`](../frontend/src/App.tsx), [`App.test.tsx`](../frontend/tests/App.test.tsx), [`gate-b.spec.ts`](../frontend/tests/e2e/gate-b.spec.ts) |
| PHASE-7.1-PREVIEW | Same-origin embedded preview provides real internal 1440x900 and 390x844 viewports, preserves query/auth state, prevents recursion, and closes with Escape | passed | [`App.tsx`](../frontend/src/App.tsx), [`App.test.tsx`](../frontend/tests/App.test.tsx), [`gate-b.spec.ts`](../frontend/tests/e2e/gate-b.spec.ts) |
| PHASE-7.1-REHEARSAL | PM/developer-familiar user completed Chinese desktop rehearsal in 5 seconds with 4/4 correct; not independent UX-01 evidence | recorded only | [`UX_10_SECOND_TEST.md`](UX_10_SECOND_TEST.md) |

Phase 7.1 regression evidence is **51 backend tests**, **17 Vitest tests**, and **12 Playwright
tests** across 1440x900 and 390x844. The independent UX-01 result was added later in Phase 9.4;
the final video and external submission remain open.

## Phase 8 / optional DeepSeek provider evidence - 2026-08-26

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-8-SELECTOR | Implementation checkpoint `7b1b05e` keeps fixture as the default; explicit `LLM_PROVIDER=deepseek` selects only the DeepSeek provider, rejects missing/unknown configuration, and records safe provider identity | passed | [`provider.py`](../backend/app/ai/provider.py), [`test_deepseek_provider.py`](../backend/tests/test_deepseek_provider.py) |
| PHASE-8-BOUNDARY | MockTransport proves only typed redacted synthetic text and the JSON shape cross the HTTP boundary; source reference, IDs, names, phone/IC/ID, comments, tasks, cookies, keys, and raw response are excluded | passed | [`deepseek.py`](../backend/app/ai/deepseek.py), [`test_deepseek_provider.py`](../backend/tests/test_deepseek_provider.py), [`test_ai_processing.py`](../backend/tests/test_ai_processing.py) |
| PHASE-8-OUTPUT | JSON schema, empty/truncated/invalid output, duplicate/missing quote, local Unicode span, HTTP error mapping, bounded retry, and no silent fixture fallback are tested | passed | [`schemas.py`](../backend/app/ai/schemas.py), [`deepseek.py`](../backend/app/ai/deepseek.py), [`test_deepseek_provider.py`](../backend/tests/test_deepseek_provider.py) |
| PHASE-8-JOB | Mock DeepSeek success creates a suggested system entry/highlight, refreshes materialized state, emits metadata-only SSE, and patient projection remains private; failure creates no source | passed | [`ai_processing.py`](../backend/app/services/ai_processing.py), [`test_ai_processing.py`](../backend/tests/test_ai_processing.py) |
| PHASE-8-UI | Staff/clinician-only AI Scribe Demo shows synthetic-data warning and processing/completed/failed states without provider details in the normal workflow; patient/admin do not receive the panel | passed | [`App.tsx`](../frontend/src/App.tsx), [`App.test.tsx`](../frontend/tests/App.test.tsx), [UI product-language audit](evidence/ui_product_language_audit.md) |
| PHASE-8-LAUNCHER | Ignored `.nightingale-local.json`, Configure DeepSeek, Use Local Fixture, child-only key injection, safe runtime/log boundary, fixture launcher smoke | passed | [`demo_common.ps1`](../scripts/demo_common.ps1), [`start_demo.ps1`](../scripts/start_demo.ps1), [`README_DEMO_LAUNCHER.md`](../scripts/README_DEMO_LAUNCHER.md) |
| PHASE-8-LIVE-SMOKE | One bounded official `deepseek-v4-flash` synthetic smoke returned `2xx`, valid schema, 1,342.11 ms, and 276 total tokens; no model-quality claim | recorded | [`deepseek_live_smoke.md`](evidence/deepseek_live_smoke.md) |

Phase 8 regression evidence is **71 backend tests / 88% coverage**, **19 Vitest tests**, and
**12 Playwright tests**. The live path is opt-in and cost/network dependent; the final video and
external submission remain open. UX-01 and PRIV-04 were closed by later evidence.

## Phase 9 / private publication, Render readiness, and Level-C Voice - 2026-08-27

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-9-GITHUB | One private repository created under `jyc114514`; local `main` pushed with no password-file or token use; remote main matched local at push time | passed | [private repository evidence](evidence/github_private_repository.md) |
| PHASE-9-RENDER-READINESS | Same-origin production API fallback, FastAPI static serving, Postgres psycopg URL normalization, secure production validation, Docker multi-stage image, and Free Web/Postgres Blueprint | passed | [Dockerfile](../Dockerfile), [render.yaml](../render.yaml), [production readiness tests](../backend/tests/test_production_readiness.py) |
| PHASE-9-RENDER | Exactly one Free Web Service and one Free Postgres; CI-gated PostgreSQL migration recovery; deploy `e766fe9` is Live with fixture AI and Level-C Voice fixture | passed | [deployment checklist](DEPLOYMENT_CHECKLIST.md), [deployment evidence](evidence/deployment_attempt.md), [security evidence](evidence/deployment_security.md) |
| PHASE-9-VOICE-CAPABILITY | GPU/ASR probe, isolated optional lock, package delta, honest Level-C decision; no functional Whisper transcript claim | passed | [voice capability probe](evidence/voice_capability_probe.md) |
| PHASE-9-VOICE-APP | Two synthetic WAV fixtures, mock timestamped transcript, audio hash/duration, immutable segments, role/patient authorization, source linkage, safe failures, and fixture-first summary path | passed | [voice routes](../backend/app/api/routes/voice.py), [voice service](../backend/app/services/voice.py), [test_voice.py](../backend/tests/test_voice.py) |
| PHASE-9-VOICE-UI | English/Chinese disclosure, audio preview, segment seek, confidence-unavailable label, no microphone, staff/clinician and patient privacy flows in the local fixture path | passed | [App.tsx](../frontend/src/App.tsx), [voice.spec.ts](../frontend/tests/e2e/voice.spec.ts), [voice capability probe](evidence/voice_capability_probe.md) |
| PHASE-9-SPOKEN-DEMO | English spoken script, English subtitles, and recording materials; no final video recorded | passed | [DEMO_SCRIPT_SPOKEN_EN.md](DEMO_SCRIPT_SPOKEN_EN.md), [DEMO_CUE_CARD_ZH_EN.md](DEMO_CUE_CARD_ZH_EN.md), [DEMO_SUBTITLES_EN.srt](DEMO_SUBTITLES_EN.srt) |
| PHASE-9-PUBLIC-GATE | Private-until-2026-08-28 18:00 rule, final secret scan, visibility approval, and no scheduled visibility action documented | passed | [PUBLIC_RELEASE_CHECKLIST.md](PUBLIC_RELEASE_CHECKLIST.md) |

Phase 9 local evidence is **85 backend tests / 88% coverage**, **37 Vitest tests**, **14 core
Playwright tests**, and **4 isolated Voice Playwright tests**. GitHub Actions run
`33032765274` passed the real PostgreSQL 18 migration/seed gate, and the existing Render service
is Live on the Voice-enabled `e766fe9` deployment. The authenticated production Voice smoke is
recorded in Phase 9.2/9.3. Final video, email submission, and public visibility remain open unless
their separate evidence is completed.

## Phase 9.1 / production Comments drawer regression - 2026-08-27

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-9.1-COMMENTS | Same-patient refresh preserves an open Comments drawer, SSE no longer reconnects on drawer/editor state changes, existing comments load, explicit close/backdrop/Escape behavior remains accessible, and missing entries close safely | passed | [App.tsx](../frontend/src/App.tsx), [App.test.tsx](../frontend/tests/App.test.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts), [deployment security evidence](evidence/deployment_security.md) |

Phase 9.1 evidence is **27 Vitest tests**, **14 core Playwright tests**, and an authenticated
production smoke on `8a46b96`: Comments remained visible for 5.5 seconds, an existing PostgreSQL
comment rendered, and the drawer closed through the explicit control. The independent UX-01 result
is recorded separately in Phase 9.4.

## Phase 9.2 / deployed Level-C Voice fixture - 2026-08-27

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-9.2-VOICE-FIXTURE | Render accepts only `disabled` or `fixture` in production, keeps `local_whisper` and unknown providers fail-closed, and the existing fixture configuration passed authenticated Clinical/Patient online smoke | passed | [config.py](../backend/app/config.py), [render.yaml](../render.yaml), [test_production_readiness.py](../backend/tests/test_production_readiness.py), [test_voice.py](../backend/tests/test_voice.py), [voice capability probe](evidence/voice_capability_probe.md), [deployment security evidence](evidence/deployment_security.md) |

Phase 9.2 is **Partial Bonus / Level C** only. The Render fixture configuration is Live and the
authenticated clinical/patient online flow passed. It does not mark full Ambient Voice passed:
there is no ASR inference, Whisper model, diarization, microphone capture, upload, or real PHI
audio.

## Phase 9.3 / Prompt B deployed rehearsal and recording materials - 2026-08-27

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-9.3-DEMO-REHEARSAL | English deployed rehearsal covered Glance, exact provenance, Level-C Voice, Staff collaboration, historical context, Patient privacy, and Clinician revision review; failed/stale and unavailable steps were replaced or removed | passed | [demo rehearsal](evidence/demo_rehearsal.md), [traceability](DEMO_REQUIREMENT_TRACEABILITY.md) |
| PHASE-9.3-DEMO-DOCS | Detailed English spoken script, English subtitles, and Chinese operator/session materials were refreshed after actual rehearsal | passed | [spoken script](DEMO_SCRIPT_SPOKEN_EN.md), [operator runbook](DEMO_OPERATOR_RUNBOOK_ZH.md), [bilingual cue card](DEMO_CUE_CARD_ZH_EN.md), [subtitles](DEMO_SUBTITLES_EN.srt), [shot list](DEMO_SHOTLIST.md), [recording checklist](DEMO_RECORDING_CHECKLIST.md), [video QA](DEMO_VIDEO_QA.md), [state prep](DEMO_STATE_PREP_ZH.md) |

Prompt B deliberately does not mark the final video as recorded. The exact new-note/manual-
highlight/two-browser-conflict steps were not claimed because they were unavailable or
unreproducible in the deployed rehearsal.

## Phase 9.4 / independent UX-01 and Staff-first final rehearsal - 2026-08-27

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-9.4-UX-01 | An anonymous independent participant using the supported Simplified Chinese interface completed the defined glance task in approximately nine seconds without coaching; priority, action/state, risk-versus-ranking, and source affordance were correct | passed | [independent UX evidence](evidence/ux_01_independent_test.md), [UX test record](UX_10_SECOND_TEST.md) |
| PHASE-9.4-DRY-RUN | Final deployed English dry run completed in Staff → Clinician → Patient order with two off-camera role cuts; no Voice was reprocessed and no new mutation was created | passed | [demo rehearsal](evidence/demo_rehearsal.md), [state prep](DEMO_STATE_PREP_ZH.md) |
| PHASE-9.4-RUNBOOK | Chinese operator guidance, bilingual cue card, English narration/subtitles, and final recording QA were prepared without generating the final video or packaging artifacts | passed | [operator runbook](DEMO_OPERATOR_RUNBOOK_ZH.md), [bilingual cue card](DEMO_CUE_CARD_ZH_EN.md), [spoken script](DEMO_SCRIPT_SPOKEN_EN.md), [subtitles](DEMO_SUBTITLES_EN.srt), [recording checklist](DEMO_RECORDING_CHECKLIST.md), [video QA](DEMO_VIDEO_QA.md) |

## Phase 9.5 / product-language audit - 2026-08-27

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-9.5-UI-LANGUAGE | Primary UI surfaces use product language for session status, Glance, source, context, AI, Voice, collaboration, conflicts, and Patient; technical identifiers remain in deliberate details/evidence | passed | [UI product-language audit](evidence/ui_product_language_audit.md), [App.tsx](../frontend/src/App.tsx), [English dictionary](../frontend/src/i18n/en.ts), [Chinese dictionary](../frontend/src/i18n/zh-CN.ts) |
| PHASE-9.5-VISUAL-QA | Local desktop/mobile screenshots cover workspace, source, Voice, Patient, Comments, Task, History/conflict/context, Guide, and Preview; local Gate B/Voice E2E suites are green | passed | [UI product-language audit](evidence/ui_product_language_audit.md), [local artifacts](../artifacts/gate-b/) |

Phase 9.5 is a local release-candidate change. It does not claim that the product-language update
has reached Render until the separately authorized push/deploy is completed.

## Phase 9.6 / local History and Voice regression fixes - 2026-08-27

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-9.6-HISTORY | Every History row uses aligned version/date/action columns; current rows retain a `Current`/`当前` status slot; English/Chinese desktop and mobile checks pass | passed | [App.tsx](../frontend/src/App.tsx), [App.test.tsx](../frontend/tests/App.test.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts), [regression evidence](evidence/history_voice_regression.md) |
| PHASE-9.6-VOICE | Local Voice fetches an authenticated WAV through the API host, creates/revokes Blob URLs safely, exposes loading/error states, and proves actual playback plus 8-second transcript seeking for clinical/patient paths | passed | [api.ts](../frontend/src/api.ts), [App.tsx](../frontend/src/App.tsx), [api.test.ts](../frontend/tests/api.test.ts), [App.test.tsx](../frontend/tests/App.test.tsx), [voice.spec.ts](../frontend/tests/e2e/voice.spec.ts), [regression evidence](evidence/history_voice_regression.md) |

Phase 9.6 is local-only. It does not push GitHub, trigger Render, regenerate delivery artifacts, or
change the backend Voice route, provider, authorization, or database schema.

## Phase 9.7 / final Render release-candidate verification - 2026-08-27

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| PHASE-9.7-DEPLOY | Final application commit `42a01b6` is Live on the existing Render Web Service as deploy `dep-da84vcp5efls73dm07vg`; the existing Postgres resource and private GitHub repository were reused | passed | [deployment evidence](evidence/deployment_attempt.md), [security evidence](evidence/deployment_security.md) |
| PHASE-9.7-ONLINE-VOICE | Authenticated Staff Voice suggestion creation, 24-second audio, exact 8-second transcript seek, and immutable source navigation passed; Clinician audio/source path and Patient-only Voice listing passed | passed | [online rehearsal](evidence/demo_rehearsal.md), [History/Voice evidence](evidence/history_voice_regression.md), [online screenshots](../artifacts/gate-b/) |
| PHASE-9.7-ONLINE-ROLES | Clinician History/Compare/Before-After and Staff Comments/Task/History/Source passed; Patient showed only two patient-facing timeline records and no internal controls | passed | [online rehearsal](evidence/demo_rehearsal.md), [security evidence](evidence/deployment_security.md) |
| PHASE-9.7-PRODUCT-LANGUAGE | Final online English DOM scan found no recorded developer/provider terms in the normal workflow; Staff, Clinician, and Patient product labels were visible | passed | [UI product-language audit](evidence/ui_product_language_audit.md) |
| PHASE-9.7-DELIVERY | Chinese operator instructions, English narration, subtitles, state prep, and QA checklist are ready; final video, refreshed PDF, ZIP, and MANIFEST remain intentionally pending | in progress | [operator runbook](DEMO_OPERATOR_RUNBOOK_ZH.md), [spoken script](DEMO_SCRIPT_SPOKEN_EN.md), [video QA](DEMO_VIDEO_QA.md) |

Phase 9.7 confirms the final deployed synthetic evaluation path. It does not claim live DeepSeek,
ASR inference, diarization, ambient microphone support, clinical production readiness, or a final
recorded video. The earlier Phase 9 rows retain their historical commit-specific evidence; this
section records the newer release-candidate deployment.

## Final release-candidate audit - 2026-08-28

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| FINAL-REGRESSION | Backend 85 passed / 88% coverage, Ruff, format, mypy, pip check, Alembic `0010_postgres_compat`, stable twice-run seed, frontend 37 Vitest, lint, Prettier, type-check, build, Gate B 14 Playwright, Voice 4 Playwright | passed | [final run record](evidence/final_release_regression.md) |
| FINAL-WARM-PATH | Real Uvicorn TCP warm path: 1,000 requests, concurrency 10, zero errors, P95 56.053 ms | passed | [warm-path evidence](evidence/gate_c_warm_path.md) |
| FINAL-BRIEF | Technical Brief source/HTML refreshed; final PDF is 3-page A4 and passed text/raster QA | passed | [PDF QA](evidence/technical_brief_qa.md), [PDF](../deliverables/Nightingale_Technical_Brief.pdf) |
| FINAL-VIDEO | Original MP4 supplied by the user; file metadata/hash are recorded and content QA is explicitly waived by the user; no Codex full-watch claim | passed with disclosed prototype boundary | [final video QA](evidence/final_demo_video_qa.md) |
| FINAL-CLEAN-CLONE | Final source commit clean-clone rehearsal | in progress | [clean-clone evidence](evidence/clean_clone_rehearsal.md) |
| FINAL-PACKAGING | Source ZIP, submission ZIP, manifest, and explicit exclusion checks | pending | `deliverables/submission/` |

## Round 1 / real-clinic backend safety evidence — 2026-09-01

These additive rows record the new local iteration. Earlier Phase 0–9 rows retain their
original commit-specific evidence and are not rewritten by this checkpoint.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| REAL-CLINIC-ASSERTION | Closed-vocabulary penicillin assertions use immutable source versions, exact Unicode-codepoint spans, quote hashes, safe abstention, idempotent persistence, and superseded revision lifecycle | passed | [clinical_assertions.py](../backend/app/services/clinical_assertions.py), [test_clinical_assertions.py](../backend/tests/test_clinical_assertions.py), [round1_backend_safety.md](evidence/round1_backend_safety.md) |
| REAL-CLINIC-CONFLICT | Same-clinic/patient active present/absent assertions open one deterministic dual-provenance conflict and preserve original sources | passed | [clinical_conflicts.py](../backend/app/services/clinical_conflicts.py), [clinical_conflicts.py](../backend/app/api/routes/clinical_conflicts.py), [test_clinical_conflicts.py](../backend/tests/test_clinical_conflicts.py) |
| REAL-CLINIC-SAFETY-FLOOR | Protected allergy conflict/confirmed-allergy highlights retain a deterministic 95.0 display floor with explicit ranking explanation fields | passed | [importance.py](../backend/app/services/importance.py), [glance.py](../backend/app/services/glance.py), [round1_backend_safety.md](evidence/round1_backend_safety.md) |
| REAL-CLINIC-PROTECTED-FEEDBACK | Protected feedback is recorded/audited but is excluded from preference-profile learning; ordinary feedback remains bounded and clinic scoped | passed | [importance.py](../backend/app/services/importance.py), [test_clinical_conflicts.py](../backend/tests/test_clinical_conflicts.py) |
| REAL-CLINIC-RBAC | Staff read/internal scope, clinician-only adjudication, patient denial, and foreign-clinic not-found behavior are enforced by the API | passed | [clinical_conflicts.py](../backend/app/api/routes/clinical_conflicts.py), [authorization.py](../backend/app/services/authorization.py), [test_clinical_conflicts.py](../backend/tests/test_clinical_conflicts.py) |
| REAL-CLINIC-MIGRATION | Additive 0011 schema reaches head, passes Alembic check, legacy/downgrade paths, and migration-backed application fixtures without create_all | passed with disclosed prototype boundary | [0011_real_clinic_safety.py](../backend/migrations/versions/0011_real_clinic_safety.py), [test_migrations.py](../backend/tests/test_migrations.py), [round1_backend_safety.md](evidence/round1_backend_safety.md) |

## Round 2 / conflict UI and Glance exposure evidence - 2026-09-01

These additive rows record the second local iteration. Earlier Phase 0-9 and Round 1 rows retain
their historical wording and commit-specific evidence.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| ROUND2-MIGRATION | New 0012 tables for bounded metadata-only Glance impression batches/items; fresh upgrade, downgrade/re-upgrade, legacy repair, and `alembic check` remain green without `create_all` | passed | [0012_glance_impressions.py](../backend/migrations/versions/0012_glance_impressions.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| ROUND2-CANDIDATES | Glance GET and impression POST share one provider-free deterministic candidate snapshot, six-item selection, eligible count, and 500-row storage cap | passed | [glance_read.py](../backend/app/services/glance_read.py), [gate_b.py](../backend/app/api/routes/gate_b.py), [round2_conflict_ui_exposure.md](evidence/round2_conflict_ui_exposure.md) |
| ROUND2-IMPRESSIONS | Internal idempotent impression POST/summary APIs validate duplicate/mismatched/invalid surfaces, preserve candidate metadata only, report truncation, and do not expose patient text | passed | [impressions.py](../backend/app/services/impressions.py), [impressions.py](../backend/app/api/routes/impressions.py), [test_impressions.py](../backend/tests/test_impressions.py) |
| ROUND2-ASSERTION-SOURCE | Clinical assertion source API revalidates clinic/patient, immutable version, exact Unicode span, quote hash, and safe corruption errors; old source survives later edits | passed | [clinical_assertions.py](../backend/app/services/clinical_assertions.py), [clinical_conflicts.py](../backend/app/api/routes/clinical_conflicts.py), [test_clinical_conflicts.py](../backend/tests/test_clinical_conflicts.py) |
| ROUND2-PROTECTED-REVIEW | Protected allergy conflicts cannot use generic Accept/Reject; card exposes protected attention/floor labels and feedback suppression; Staff is read-only and Clinician has four CAS decisions | passed | [App.tsx](../frontend/src/App.tsx), [highlights.py](../backend/app/services/highlights.py), [round2_conflict_ui_exposure.md](evidence/round2_conflict_ui_exposure.md) |
| ROUND2-PRIVACY | Patient UI makes no conflict/assertion/impression calls and direct protected endpoints return 403; Clinic B remains isolated | passed | [test_clinical_conflicts.py](../backend/tests/test_clinical_conflicts.py), [test_impressions.py](../backend/tests/test_impressions.py), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts) |
| ROUND2-BROWSER | Scenario D source replacement, dual drawer, Staff read-only, clinician stale 409/refresh, and patient privacy pass at 1440x900 and 390x844; screenshots reviewed | passed | [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts), [Scenario D screenshots](../artifacts/gate-b/) |
| ROUND2-PERF | Real Uvicorn TCP warm path at `803733d`: 50 warm-up, 1,000 requests, concurrency 10, zero errors, P50 64.165 ms, P95 83.045 ms, P99 99.848 ms, max 137.349 ms, six items | passed with disclosed prototype boundary | [round2_warm_path.md](evidence/round2_warm_path.md), [benchmark_warm_path.py](../backend/app/scripts/benchmark_warm_path.py) |
| ROUND2-REAL-CLINIC-AUDIT | Scenario 13 improves from DOES NOT to PARTIAL; Scenarios 14 and 15 remain PARTIAL because the slice is bounded and exposure data is not debiasing/calibration | recorded | [REAL_CLINIC_16_AUDIT.md](REAL_CLINIC_16_AUDIT.md), [ITERATION_DECISION.md](ITERATION_DECISION.md) |

## Round 3 / safe failure, provider resilience, and PHI logging evidence - 2026-09-02

These additive rows record the third local iteration. Earlier Phase 0-9 and Round 1-2 rows retain
their historical wording and commit-specific evidence.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| ROUND3-MIGRATION | New 0013 adds persistent clinic/provider circuit state and AI job retry metadata; fresh, downgrade/re-upgrade, writable copy of the existing 0012 database, and `alembic check` pass | passed with local-database permission note | [0013_ai_provider_resilience.py](../backend/migrations/versions/0013_ai_provider_resilience.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| ROUND3-LOGGING | Allowlisted JSON safe events, defensive PHI/credential/control sanitizer, generic exception boundary, and explicit non-recursive log audit pass negative leak tests | passed | [safe_logging.py](../backend/app/observability/safe_logging.py), [safe_exceptions.py](../backend/app/middleware/safe_exceptions.py), [audit_phi_logs.py](../backend/app/scripts/audit_phi_logs.py), [test_safe_logging.py](../backend/tests/test_safe_logging.py) |
| ROUND3-ORDERING | `ai_job_created` -> `ai_redaction_completed` -> provider call -> safe completion/failure -> provenance completion is tested; redaction failure has zero provider calls | passed | [ai_processing.py](../backend/app/services/ai_processing.py), [test_provider_resilience.py](../backend/tests/test_provider_resilience.py) |
| ROUND3-BUDGET | Optional external provider uses 8s attempt timeout, 12s monotonic total budget, max 2 attempts, and no blind retry for auth/balance/429/invalid output | passed | [deepseek.py](../backend/app/ai/deepseek.py), [ROUND3_SAFE_FAILURE_DESIGN.md](ROUND3_SAFE_FAILURE_DESIGN.md), [test_provider_resilience.py](../backend/tests/test_provider_resilience.py) |
| ROUND3-CIRCUIT | Persistent closed/open/half_open circuit is clinic/provider scoped, threshold 3, cooldown 60s, one CAS probe, success reset, failure reopen, and fixture bypass | passed | [provider_resilience.py](../backend/app/services/provider_resilience.py), [test_provider_resilience.py](../backend/tests/test_provider_resilience.py) |
| ROUND3-STATUS | Internal patient-scoped provider status returns safe availability/circuit/retry metadata; Patient is denied and no key/base URL/response body is exposed | passed | [ai_processing.py](../backend/app/api/routes/ai_processing.py), [test_provider_resilience.py](../backend/tests/test_provider_resilience.py) |
| ROUND3-DEGRADED-UI | Bilingual degraded/circuit-open AI panel shows no fallback, preserves existing workspace, supports bounded Check availability, and keeps Patient UI private | passed | [App.tsx](../frontend/src/App.tsx), [App.test.tsx](../frontend/tests/App.test.tsx), [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts), [PROVIDER_DEGRADED_MODE.md](PROVIDER_DEGRADED_MODE.md) |
| ROUND3-BROWSER | Scenario E passes at desktop/mobile; timeout/503 is route-mocked, existing source/comments/tasks/history remain usable, and Patient sees no outage details | passed | [gate-b.spec.ts](../frontend/tests/e2e/gate-b.spec.ts), [round3_safe_failure_logging.md](evidence/round3_safe_failure_logging.md) |
| ROUND3-PERF | Warm Glance: 1,000 TCP requests, concurrency 10, zero errors, P50 56.818 ms, P95 70.639 ms, P99 93.048 ms, max 107.593 ms; circuit-open: 100 requests, P50 16.721 ms, P95 17.911 ms, P99 18.111 ms, max 20.628 ms, zero measured provider calls | passed with disclosed local approximation boundary | [round3_safe_failure_logging.md](evidence/round3_safe_failure_logging.md), [benchmark_circuit_failfast.py](../backend/app/scripts/benchmark_circuit_failfast.py) |
| ROUND3-AUDIT-STATUS | #3 remains PARTIAL (local logging only); #4 SURVIVES strengthened; #8 remains PARTIAL (synchronous); #9 remains PARTIAL (no durable queue/replay) | recorded | [REAL_CLINIC_16_AUDIT.md](REAL_CLINIC_16_AUDIT.md), [ITERATION_DECISION.md](ITERATION_DECISION.md) |

## Round 4 / patient publication gate evidence - 2026-09-02

These additive rows record the bounded Scenario 12 implementation. The original 25-item
Mandatory total remains unchanged; the real-clinic audit status is explicitly `PARTIAL` because
the dosage grammar is narrow and external delivery is not implemented.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| ROUND4-DESIGN | State machine distinguishes internal suggestion acceptance, draft, clinician approval, portal publication, recall, correction, supersession, and entered-in-error | passed with disclosed prototype boundary | [ROUND4_PATIENT_PUBLICATION_DESIGN.md](ROUND4_PATIENT_PUBLICATION_DESIGN.md), [PATIENT_PUBLICATION_BOUNDARY.md](PATIENT_PUBLICATION_BOUNDARY.md) |
| ROUND4-MIGRATION | New `0014_patient_publications` schema adds workflow, immutable content versions, and deterministic source evidence without editing `0001`–`0013`; Alembic head/check and downgrade/re-upgrade pass | passed | [0014_patient_publications.py](../backend/migrations/versions/0014_patient_publications.py), [test_migrations.py](../backend/tests/test_migrations.py) |
| ROUND4-DOSAGE | Synthetic metformin integer-mg dosage evidence uses immutable source/version and Unicode-codepoint offsets; mismatch, ambiguity, unsupported grammar, and source changes fail closed | passed | [publication_evidence.py](../backend/app/services/publication_evidence.py), [test_patient_publications.py](../backend/tests/test_patient_publications.py) |
| ROUND4-WORKFLOW | Staff prepare/edit, Clinician approve/publish/recall/correct, workflow CAS `409`, audit metadata, and no Accept→Publish shortcut pass through the real API | passed | [patient_publications.py](../backend/app/services/patient_publications.py), [patient_publications.py](../backend/app/api/routes/patient_publications.py), [test_patient_publications.py](../backend/tests/test_patient_publications.py) |
| ROUND4-PATIENT-PROJECTION | Patient receives only current published content or safe withdrawal/correction notices; internal source, raw AI, workflow/evidence/history IDs are absent; legacy timeline remains unchanged | passed | [patients.py](../backend/app/api/routes/patients.py), [patient_publications.py](../backend/app/api/routes/patient_publications.py), [test_patient_publications.py](../backend/tests/test_patient_publications.py) |
| ROUND4-UI | Bilingual internal publication drawer shows exact source, dosage status, draft history, role boundary, explicit publish confirmation, recall/correction controls, and Patient projection | passed | [App.tsx](../frontend/src/App.tsx), [App.test.tsx](../frontend/tests/App.test.tsx) |
| ROUND4-BROWSER | Scenario F passes at 1440×900 and 390×844: wrong dosage block, Patient privacy, approval→publish, recall, correction, and two-context stale approval | passed | [patient-publication.spec.ts](../frontend/tests/e2e/patient-publication.spec.ts) |
| ROUND4-PERF | Published-care real TCP path: 50 warm-up + 1,000 requests, concurrency 10, zero errors, P95 46.797 ms on local SQLite/Uvicorn | passed with disclosed local approximation boundary | [round4_patient_publication.md](evidence/round4_patient_publication.md), [round4_patient_publication_p95.json](evidence/round4_patient_publication_p95.json) |
| ROUND4-AUDIT-STATUS | Scenario 12 improves from missing workflow to **PARTIAL** bounded portal gate; no external delivery/receipt/recall or general medication NLP is claimed | recorded | [REAL_CLINIC_16_AUDIT.md](REAL_CLINIC_16_AUDIT.md), [ITERATION_DECISION.md](ITERATION_DECISION.md) |

## Round 5 / release-candidate integration evidence - 2026-09-02

These rows reconcile Round 1–4 without adding clinical scope. Real PostgreSQL execution and
external GitHub Actions remain pending Round 6 authorization; offline SQL is not execution
evidence. Final video/PDF/ZIP artifacts are intentionally unchanged.

| ID | Evidence | Status | Evidence location |
| --- | --- | --- | --- |
| ROUND5-TEMP-HYGIENE | Genuine Round pytest/Ruff/Playwright artifacts identified; removable generated outputs deleted, ACL-protected pytest directories preserved and narrowly ignored | passed with disclosed ACL note | [ROUND5_INTEGRATION_AUDIT.md](ROUND5_INTEGRATION_AUDIT.md), [.gitignore](../.gitignore) |
| ROUND5-DIFF-AUDIT | Round 1–4 migrations, models, services, routes, frontend, tests, benchmarks, state/privacy distinctions and local/hosted claims reconciled | passed | [ROUND5_INTEGRATION_AUDIT.md](ROUND5_INTEGRATION_AUDIT.md), [route/privacy audit](evidence/round5_route_privacy_audit.md) |
| ROUND5-MIGRATION-FRESH | Fresh SQLite 0001→0014, schema/FK inspection, seed twice, stable counts, and Alembic check pass | passed | [ROUND5_INTEGRATION_AUDIT.md](ROUND5_INTEGRATION_AUDIT.md), [test_migrations.py](../backend/tests/test_migrations.py) |
| ROUND5-MIGRATION-LEGACY | Disposable 0010/0011/0012/0013 → 0014 paths preserve old synthetic records and pass seed/check; downgrade data-loss behavior documented | passed with disposable-database boundary | [ROUND5_INTEGRATION_AUDIT.md](ROUND5_INTEGRATION_AUDIT.md), [round5_legacy_probe.py](../backend/app/scripts/round5_legacy_probe.py) |
| ROUND5-POSTGRES-OFFLINE | PostgreSQL dialect offline SQL 0010→0014 contains publication/self-reference constraints and no SQLite temp token; fresh base→head limitation recorded | passed with disclosed offline limitation | [ROUND5_INTEGRATION_AUDIT.md](ROUND5_INTEGRATION_AUDIT.md), [real-clinic-postgres.yml](../.github/workflows/real-clinic-postgres.yml) |
| ROUND5-POSTGRES-CI | PostgreSQL 18/Python 3.12 workflow prepared with current 0014 schema, seed, tests and static gates; not externally executed in Round 5 | ready — pending Round 6 external CI | [real-clinic-postgres.yml](../.github/workflows/real-clinic-postgres.yml) |
| ROUND5-CLEAN-CLONE | Tracked-only clean clone v3 at `39ab0f0`: backend/frontend gates, launcher smoke, Gate B, Voice, and Scenario F pass at both viewports; clone cleanup has a documented Windows ACL note | passed with disclosed ACL note | [ROUND5_INTEGRATION_AUDIT.md](ROUND5_INTEGRATION_AUDIT.md), [clean-clone evidence](evidence/clean_clone_rehearsal.md) |
| ROUND5-REGRESSION | Primary final run: 175 backend tests/85% coverage, 45 frontend tests, static quality, log audit, secret/history scan and port checks pass | passed with disclosed local-boundary evidence | [ROUND5_INTEGRATION_AUDIT.md](ROUND5_INTEGRATION_AUDIT.md), [route/privacy audit](evidence/round5_route_privacy_audit.md) |
| ROUND5-DEMO | Scenario 13/15 primary safety path and Scenario 12 optional publication path documented with no new recording | passed | [REAL_CLINIC_DEMO_RUNBOOK.md](REAL_CLINIC_DEMO_RUNBOOK.md), [REAL_CLINIC_SCENARIO_DEMO.md](REAL_CLINIC_SCENARIO_DEMO.md) |
| ROUND5-BRIEF | Round 1–5 iteration brief records baseline, scope, architecture, evidence and non-claims | passed | [REAL_CLINIC_ITERATION_BRIEF.md](REAL_CLINIC_ITERATION_BRIEF.md) |

## Hard release gate

Do not call the build submission-ready unless every Mandatory and Deliverable row is `passed`, or an explicit limitation is documented with a deliberate scope decision. Bonus rows may be dropped without blocking release.
