# Final requirements audit

审计日期：2026-08-28
权威需求：[`requirements.txt`](../requirements.txt)
需求文件 SHA-256：`4659AF4A414AFF86C1DB6DA0EC3FEB4837236D625669AE7C9CFE5CC69BC934F5`

## Release gate decision

**PASS WITH DISCLOSED BOUNDARIES FOR PUSH/PACKAGE.** 逐条对照 candidate brief 后，没有发现
除 Ambient Voice bonus 外的 `failed` 或 `not proven` Mandatory requirement。Mandatory product
requirements 为 **25/25 passed**；五个指定 micro-tests 均有实际通过证据；README、ATTRIBUTION、
2–3 page Technical Brief/PDF、Git history、Judge access 和用户提供的 MP4 均存在。最终视频内容
QA 按用户本轮明确指令 waived：这不是 Codex 完整观看通过的声明。

本审计使用的实际回归结果记录在
[`final_release_regression.md`](evidence/final_release_regression.md)：backend 85 passed、88%
coverage、frontend 37 Vitest、Gate B 14 Playwright、Voice 4 Playwright；warm-path P95 为
56.053 ms。未重复运行这些检查。

允许的状态含义：`passed`、`passed with disclosed prototype boundary`、`partial bonus`、
`optional not selected`、`recommended substep not shown`、`not proven`、`failed`。

## 1. Mandatory product requirements

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Shared clinic-scoped longitudinal workspace and role-based collaboration (`requirements.txt:3–5`) | Mandatory | passed with disclosed prototype boundary | `backend/app/main.py`; `frontend/src/App.tsx`; `backend/app/api/routes/events.py` | Final regression and Gate B E2E passed | [`README.md`](../README.md); [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | Realtime is metadata-only SSE invalidation/refetch, not CRDT/OT or simultaneous character editing. |
| Unified patient page and glanceable, actionable Top/Glance View (`requirements.txt:8–9`) | Mandatory | passed | `backend/app/services/glance.py`; `backend/app/api/routes/gate_b.py`; `frontend/src/App.tsx` | `test_materialized_glance.py`, Gate B E2E, independent UX-01 record | [`ACCEPTANCE_MATRIX.md`](ACCEPTANCE_MATRIX.md); [`JUDGE_ACCESS.md`](../JUDGE_ACCESS.md) | Evidence is synthetic; independent timing is one participant, not a usability study. |
| Continuous time-ordered Longitudinal Timeline (`requirements.txt:10–11`) | Mandatory | passed | `backend/app/api/routes/gate_b.py`; timeline projection in `frontend/src/App.tsx` | Gate B API/browser checks passed | [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) | No EHR integration is claimed. |
| Required entry types: patient/AI sessions, doctor/nurse AI consults, staff/clinician manual edits, system events (`requirements.txt:12`) | Mandatory | passed | `backend/app/models/enums.py`; `backend/app/scripts/seed_demo.py`; `backend/app/services/ai_processing.py` | `test_ai_processing.py`, `test_gate_b_api.py`, Voice tests passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | AI/Voice inputs are deterministic synthetic fixtures by default. |
| Entry metadata: author role/id, timestamp, type, provenance pointer (`requirements.txt:13`) | Mandatory | passed | `backend/app/api/routes/gate_b.py`; `backend/app/schemas/gate_b.py` | Gate B API metadata assertions passed | [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | System authorship and entry ownership are separate fields; source references are synthetic. |
| Threaded comments and resolve/unresolve (`requirements.txt:14–15`) | Mandatory | passed | `backend/app/api/routes/comments.py`; `frontend/src/App.tsx` | Collaboration tests, App tests and Gate B E2E passed | [`DEMO_OPERATOR_RUNBOOK_ZH.md`](DEMO_OPERATOR_RUNBOOK_ZH.md) | The unavailable deployed new-note control is a recommended-scenario caveat, not a comment failure. |
| Full immutable revision snapshots, diff, revert (`requirements.txt:16–19`) | Mandatory | passed | `backend/app/services/entries.py`; `backend/app/api/routes/entries.py`; `entry_versions` model | `test_revision_history.py`, Gate B E2E passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Revert is additive; history is never erased. |
| Three distinct AI-scribed interaction types (`requirements.txt:20–25`) | Mandatory | passed with disclosed prototype boundary | `backend/app/services/ai_processing.py`; `backend/app/ai/provider.py`; seed fixtures | `test_ai_processing.py`, `test_ai_provider_boundary.py`, Gate B/Voice E2E passed | [`JUDGE_ACCESS.md`](../JUDGE_ACCESS.md); Technical Brief | Fixture provider is default; optional live provider is not required for the scored path. |
| AI provenance pointer to original source/session (`requirements.txt:26`) | Mandatory | passed | `backend/app/services/highlights.py`; `backend/app/models/highlight.py`; `backend/app/api/routes/gate_b.py` | `test_highlight_provenance.py` and Voice source checks passed | [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) | Pointers resolve within synthetic local records; no external session system is claimed. |
| Server-side patient/staff/clinician/admin RBAC and clinic scope (`requirements.txt:33–40`) | Mandatory | passed | `backend/app/services/authorization.py`; `backend/app/api/dependencies.py`; patient projection routes | `test_rbac_scope.py`, production-readiness tests, Gate B/Voice E2E passed | [`README.md`](../README.md); [`deployment_security.md`](evidence/deployment_security.md) | Admin is clinic-scoped oversight/read-only product path; no separate admin dashboard is claimed. |
| Traceable source-of-truth navigation for manual and AI highlights (`requirements.txt:41–43`) | Mandatory | passed | `backend/app/services/highlights.py`; `frontend/src/App.tsx` exact codepoint rendering | `test_highlight_provenance.py`, Unicode/repeated-quote tests, Gate B E2E passed | [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | Source navigation is immutable-version based; clinical prose is not translated. |
| Conflict flagged/preserved without silent overwrite (`requirements.txt:44`) | Mandatory | passed | `backend/app/services/entries.py`; conflict routes/models; UI conflict panel | `test_concurrent_edits.py`, provenance/revision tests, Gate B conflict E2E passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Clinician authority is a review/semantic boundary, not deletion of prior submissions. |

### Explicit Mandatory item register

The grouped table above explains the architecture; this register keeps the 25 acceptance items
distinct and prevents a grouped row from hiding a missing Mandatory item.

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| UX-01: Glance readable/actionable under 10 seconds (`requirements.txt:9`) | Mandatory | passed | Glance projection and UI cards | Independent UX-01 record and Gate B browser checks | [`UX_10_SECOND_TEST.md`](UX_10_SECOND_TEST.md) | One independent participant; not a statistical study. |
| UX-02: content, open actions, critical flags (`requirements.txt:9`) | Mandatory | passed | Top Card fields in `frontend/src/App.tsx`; `backend/app/api/routes/gate_b.py` | Gate B API/UI assertions passed | [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) | Synthetic display data only. |
| UX-03: continuous time-ordered timeline (`requirements.txt:10–11`) | Mandatory | passed | Timeline route and entry ordering | Gate B API/E2E passed | [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) | No EHR integration claim. |
| DATA-01: entry author/owner/type/time/provenance metadata (`requirements.txt:12–13`) | Mandatory | passed | `gate_b.py` serializer and entry models | Gate B metadata tests passed | [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | Synthetic source references only. |
| AI-01: three distinct system-authored AI entry types (`requirements.txt:21–25`) | Mandatory | passed with disclosed prototype boundary | AI processing service, enums, seed | `test_ai_processing.py` and Gate B/Voice E2E passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Fixture default; no model-quality claim. |
| COL-01: threaded comments with resolve/unresolve (`requirements.txt:14–15`) | Mandatory | passed | Comments route/model and contextual drawer | Collaboration/App/Gate B tests passed | [`DEMO_OPERATOR_RUNBOOK_ZH.md`](DEMO_OPERATOR_RUNBOOK_ZH.md) | New-note composer is a recommended step not shown in deployed rehearsal. |
| REV-01: full snapshots and version increment (`requirements.txt:16–18`) | Mandatory | passed | `entries.py`, `entry_versions` | `test_revision_history.py` passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Revert is additive. |
| REV-02: view changes since a version/date (`requirements.txt:18`) | Mandatory | passed | Diff route and History UI | Revision/E2E checks passed | [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) | Version numbers are selected from the actual page. |
| REV-03: revert without erasing history (`requirements.txt:18–19`) | Mandatory | passed | `revert_entry_content` creates a new snapshot | Revision and Gate B E2E passed | [`docs/evidence/history_voice_regression.md`](evidence/history_voice_regression.md) | No deletion/overwrite of prior versions. |
| AUD-01: metadata-only who/what audit (`requirements.txt:17–19`) | Mandatory | passed | `record_audit` and audit model | Revision/provenance audit assertions passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Bodies and titles are excluded from audit rows. |
| PROV-01: every highlight resolves to provenance (`requirements.txt:42`) | Mandatory | passed | Highlight service and source route | `test_highlight_provenance.py` passed | [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | Source is synthetic and immutable-version based. |
| PROV-02: click jumps to exact entry/span (`requirements.txt:43`) | Mandatory | passed | Codepoint span validation and source navigation UI | Unicode, repeated-quote, integrity, and E2E checks passed | [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) | Clinical source prose is not translated. |
| TRUST-01: visible, accept/rejectable AI suggestions (`requirements.txt:31`) | Mandatory | passed | Review route and role-aware Glance controls | Highlight review tests and E2E passed | [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) | Accept/Reject belongs to Clinician AI review, not tasks. |
| TRUST-02: conflict flagged/clinician-adjudicated (`requirements.txt:44`) | Mandatory | passed | Conflict model/routes and comparison UI | Conflict/revision/concurrency tests passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | No silent last-write-wins. |
| AUTH-01: patient-facing-only projection (`requirements.txt:36`) | Mandatory | passed | `patients.py` projection and authorization | RBAC patient denial/projection tests and E2E passed | [`JUDGE_ACCESS.md`](../JUDGE_ACCESS.md) | Synthetic patient link only. |
| AUTH-02: staff/clinician role-owned writes (`requirements.txt:37–38`) | Mandatory | passed | `authorization.py` role checks | `test_rbac_scope.py` passed | [`README.md`](../README.md) | UI hiding is not the enforcement mechanism. |
| AUTH-03: clinic-scoped staff/clinician/admin access (`requirements.txt:37–39`) | Mandatory | passed | Clinic membership and patient scope checks | Cross-clinic/admin tests passed | [`deployment_security.md`](evidence/deployment_security.md) | No cross-clinic sharing claim. |
| AUTH-04: server-side enforcement (`requirements.txt:40`) | Mandatory | passed | FastAPI dependencies and service authorization | Direct unauthorized API tests passed | [`README.md`](../README.md) | Production compliance is not claimed. |
| CONC-01: independent sections do not overwrite (`requirements.txt:51`, `67–68`) | Mandatory | passed | CAS entry update service | `test_concurrent_edits.py` passed | [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | SSE does not merge characters. |
| CONC-02: deterministic stale-write conflict (`requirements.txt:44`, `69`) | Mandatory | passed | Conflict record and 409 route path | `test_concurrent_edits.py` plus E2E conflict passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Both submissions remain for review. |
| PRIV-01: synthetic data only (`requirements.txt:53`) | Mandatory | passed with disclosed prototype boundary | Seed fixtures and repository boundary | Seed/repository scans passed | [`README.md`](../README.md) | No real PHI or clinical production claim. |
| PRIV-02: redact names, IC/ID and phones before LLM (`requirements.txt:53`) | Mandatory | passed | `backend/app/ai/redaction.py`; provider boundary | Redaction/fail-closed/provider-spy tests passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | External calls remain optional and synthetic. |
| PRIV-03: clean logs/no raw note content (`requirements.txt:53`) | Mandatory | passed | Safe error/audit/job logging | AI-processing caplog and audit tests passed | [`final_release_regression.md`](evidence/final_release_regression.md) | Evidence is bounded to the tested prototype. |
| PRIV-04: TLS in transit/encryption at rest (`requirements.txt:53`) | Mandatory | passed with disclosed prototype boundary | Render HTTPS/secure config and PostgreSQL path | Prior Render HTTPS/managed-Postgres evidence passed | [`deployment_security.md`](evidence/deployment_security.md) | Provider documentation plus observed HTTPS; not an independent cryptographic audit. |
| PERF-01: warm Glance P95 <= 300 ms (`requirements.txt:52`) | Mandatory | passed with disclosed prototype boundary | Materialized Glance read path | 1,000-request real-TCP benchmark P95 56.053 ms | [`gate_c_warm_path.md`](evidence/gate_c_warm_path.md) | File-backed SQLite/Uvicorn approximation, not hosted PostgreSQL benchmark. |

## 2. Required micro-tests

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| `test_rbac_scope.py`: cross-role writes and patient internal-data denial (`requirements.txt:57–59`) | Required micro-test | passed | `backend/tests/test_rbac_scope.py` | File was collected in the 85-test backend run and passed | [`ACCEPTANCE_MATRIX.md`](ACCEPTANCE_MATRIX.md) | Uses synthetic fixtures and server-side test clients. |
| `test_revision_history.py`: increment, revert, metadata-only audit (`requirements.txt:60–63`) | Required micro-test | passed | `backend/tests/test_revision_history.py` | File was collected and passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Audit logs intentionally omit content bodies. |
| `test_highlight_provenance.py`: generated highlight resolves to entry/span (`requirements.txt:64–66`) | Required micro-test | passed | `backend/tests/test_highlight_provenance.py` | File was collected and passed, including Unicode/repeated quote/integrity cases | [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) | Manual phrase-selection UI is not claimed as a deployed recommended-demo step. |
| `test_concurrent_edits.py`: independent sections and deterministic same-section conflict (`requirements.txt:67–69`) | Required micro-test | passed | `backend/tests/test_concurrent_edits.py` | File was collected and passed with 409/conflict preservation | [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | SSE is invalidation, not a CRDT/OT merge engine. |
| `test_self_learning_importance.py`: feedback increases similar priority (`requirements.txt:70–72`) | Bonus micro-test | passed | `backend/tests/test_self_learning_importance.py`; `backend/app/services/importance.py` | File was collected and passed with bounded/clinic-scoped feedback checks | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Similarity is deterministic structured features, not embedding or model learning. |

## 3. Required deliverables

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Working Git repository and clear commit history (`requirements.txt:75–78`) | Required deliverable | passed with disclosed prototype boundary | Git `main`, six local commits ahead of old remote baseline, no sensitive tracked names | Git status/diff audits passed | [`README.md`](../README.md); [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | GitHub publication is an authorized next external step, not yet completed at audit time. |
| README with setup/run, redaction and RBAC explanation (`requirements.txt:79`) | Required deliverable | passed | `README.md`; launcher scripts and app code | Clean-clone setup/build portions and local regression passed | [`README.md`](../README.md) | Local Python 3.10.20 is documented as a prototype limitation; production image targets 3.12. |
| 2–3 page Technical Brief with architecture, schema, assumptions and trade-offs (`requirements.txt:80–83`) | Required deliverable | passed | `docs/TECHNICAL_BRIEF.md`; `deliverables/technical_brief.html` | PDF has 3 A4 pages; extraction and raster QA passed | [`technical_brief_qa.md`](evidence/technical_brief_qa.md) | It is evaluation evidence, not clinical compliance certification. |
| `ATTRIBUTION.txt` (`requirements.txt:84`) | Required deliverable | passed | `ATTRIBUTION.txt` | Existing dependency/license audit retained | [`ATTRIBUTION.txt`](../ATTRIBUTION.txt) | No new external model or provider is required by the default path. |
| Demo Video (`requirements.txt:85`) | Required deliverable | passed with disclosed prototype boundary | User-supplied original MP4 exists; no code dependency | File size/hash fact is available; no new video content check was run | [`final_demo_video_qa.md`](evidence/final_demo_video_qa.md); [`DEMO_VIDEO_QA.md`](DEMO_VIDEO_QA.md) | User explicitly waived further content QA; Codex does not claim complete playback or content approval. |

## 4. Recommended demo scenarios

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Scenario A: Staff sees Glance and opens an AI source (`requirements.txt:87–89`) | Recommended scenario | passed with disclosed prototype boundary | Glance/source routes and UI | Gate B E2E and independent UX evidence passed | [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) | Final MP4 content was not re-reviewed in this audit. |
| Scenario B: new note, manual phrase highlight, edit, comments, revision audit (`requirements.txt:90–93`) | Recommended scenario | recommended substep not shown | Existing-note editing, highlight, comments, tasks and revision code exist | Local API/UI tests pass; deployed rehearsal did not expose new-note/manual-highlight controls | [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | New-note/manual phrase-selection UI is not claimed; this does not block Mandatory release. |
| Scenario C: dated longitudinal context, priority explanation and self-learning (`requirements.txt:94–97`) | Recommended scenario | passed with disclosed prototype boundary | Archival context and importance services/UI | `test_data_decay.py`, `test_self_learning_importance.py`, Gate B E2E passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Data decay is a representation/policy prototype, not a production retention/deletion policy. |

## 5. Optional collaboration features

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Mentions (`requirements.txt:15`, optional) | Optional | passed | `backend/app/api/routes/comments.py`; mention model; UI autocomplete | Collaboration/App/Gate B tests passed | [`DEMO_OPERATOR_RUNBOOK_ZH.md`](DEMO_OPERATOR_RUNBOOK_ZH.md) | Only active same-clinic staff/clinician collaborators are mentionable. |
| Assignments/tasks (`requirements.txt:15`, optional) | Optional | passed with disclosed prototype boundary | `backend/app/api/routes/tasks.py`; task projection and CAS conflict model | Collaboration/task tests and Gate B E2E passed | [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md) | Formal task lifecycle is documented; final video content is not independently re-watched. |

## 6. Bonus self-learning importance

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Adaptive importance and feedback (`requirements.txt:27–31`, `70–72`) | Bonus | passed with disclosed prototype boundary | `backend/app/services/importance.py`; materialized Glance fields/UI explanation | `test_self_learning_importance.py`, materialized Glance and browser checks passed | [`gate_d_bonus.md`](evidence/gate_d_bonus.md); Technical Brief | Bounded feature feedback changes display priority only; it never silently changes medical risk or diagnosis. |

## 7. Bonus hybrid storage/data decay

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Hot/warm/cold schema and source-preserving policy (`requirements.txt:32`, `97`) | Bonus | passed with disclosed prototype boundary | `backend/app/services/archival.py`; archival models and context routes | `test_data_decay.py`, migration and Gate B checks passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md); context screenshots | Canonical records are preserved; production backup, retention and deletion operations were not independently exercised. |

## 8. Bonus Ambient Voice

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Patient and clinical voice-created entries (`requirements.txt:45–48`) | Bonus | partial bonus | `backend/app/api/routes/voice.py`; `backend/app/services/voice.py`; WAV fixtures | `test_voice.py`, Voice E2E 4 passed, prior authenticated fixture evidence | [`voice_capability_probe.md`](evidence/voice_capability_probe.md); [`JUDGE_ACCESS.md`](../JUDGE_ACCESS.md) | Only prerecorded synthetic audio plus prepared timestamped transcript. No microphone, upload, live ASR, Whisper inference, diarization, automatic speaker labels, noisy-environment robustness, or production multilingual medical transcription is claimed. |

## 9. Deployment and security evidence

| Requirement | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Server-side RBAC, no cross-role overwrite (`requirements.txt:51`) | Mandatory technical constraint | passed | Authorization dependencies/services and role-owned entry writes | `test_rbac_scope.py`, concurrent/revision tests passed | [`deployment_security.md`](evidence/deployment_security.md) | Production compliance beyond this synthetic evaluation is not claimed. |
| Warm Glance P95 <= 300 ms (`requirements.txt:52`) | Mandatory technical constraint | passed with disclosed prototype boundary | Materialized `patient_glance_items` read path | 1,000 real TCP requests, concurrency 10, zero errors, P95 **56.053 ms** | [`gate_c_warm_path.md`](evidence/gate_c_warm_path.md) | Measured on file-backed SQLite/Uvicorn, not a hosted PostgreSQL production benchmark. |
| Synthetic-only redaction, TLS in transit, encryption at rest (`requirements.txt:53`) | Mandatory security constraint | passed with disclosed prototype boundary | `backend/app/ai/redaction.py`; production config and Render deployment files | Redaction/fail-closed tests passed; prior Render HTTPS/managed PostgreSQL evidence passed | [`deployment_security.md`](evidence/deployment_security.md); [`README.md`](../README.md) | TLS is supported by observed redirect/HTTPS plus provider documentation; this is not an independent cryptographic audit. |
| Any suitable Python/Node stack (`requirements.txt:54`) | Technical choice | passed | FastAPI + React/TypeScript + Alembic | Full local regression passed | [`TECHNICAL_BRIEF.md`](TECHNICAL_BRIEF.md) | Shared local `ai_env` remains Python 3.10.20 by explicit prototype decision; production Docker target is 3.12. |
| PostgreSQL migration compatibility and Render reuse | Deployment evidence | passed with disclosed prototype boundary | Alembic `0010_postgres_compat`; Render Docker/Blueprint | Prior real PostgreSQL 18 CI and Render migration evidence passed; not repeated | [`deployment_attempt.md`](evidence/deployment_attempt.md) | Current host HTTPS recheck was not treated as new evidence; no Render write or manual deploy is part of this audit. |

## 10. Known prototype boundaries and non-blockers

| Boundary | Classification | Status | Code evidence | Test evidence | Demo/document evidence | Remaining caveat |
| --- | --- | --- | --- | --- | --- | --- |
| Optional DeepSeek V4 Flash adapter | Optional | optional not selected | `backend/app/ai/deepseek.py`; provider selector | Mock boundary/output/failure tests passed; no live call required | [`deepseek_live_smoke.md`](evidence/deepseek_live_smoke.md) | Fixture remains default; no provider compliance/model-quality claim. |
| Manual new-note/manual phrase-selection recommended steps | Recommended substep | recommended substep not shown | Existing-note/highlight paths are implemented | Local coverage exists, deployed rehearsal lacked controls | [`DEMO_REQUIREMENT_TRACEABILITY.md`](DEMO_REQUIREMENT_TRACEABILITY.md) | Not a Mandatory blocker. |
| Full clean-clone launcher cleanup | Supplemental release evidence | passed with disclosed prototype boundary | Launcher scripts unchanged | Fresh clone migration/seed/backend/frontend build passed; official cleanup hit managed-Windows `taskkill` access denial; ports were clear afterward | [`clean_clone_rehearsal.md`](evidence/clean_clone_rehearsal.md) | Re-run on a host permitting ownership-checked process cleanup for a fully green launcher smoke. |
| Final MP4 content QA | User-owned review | passed with disclosed prototype boundary | User-supplied file is untouched | Size/hash fact available; no further play/decode/frame inspection per user instruction | [`final_demo_video_qa.md`](evidence/final_demo_video_qa.md) | Do not call this Codex full-playback approval; user may review before sending. |
| Scoring and deadline (`requirements.txt:99–108`) | Communication/submission | passed with disclosed prototype boundary | Final brief, scripts, SRT, email draft | Document consistency checks passed | [`DEMO_RECORDING_MASTER_ZH_EN.md`](DEMO_RECORDING_MASTER_ZH_EN.md); [`SUBMISSION_EMAIL_DRAFT.md`](../deliverables/submission/SUBMISSION_EMAIL_DRAFT.md) | No score is invented; email is not sent by Codex. |

## Audit conclusion

- Non-Voice Mandatory: **25/25 passed**; no `failed` or `not proven` Mandatory item found.
- Required micro-tests: **5/5 actual files present and passed** in the recorded 85-test run.
- Required local deliverables: README, ATTRIBUTION, Technical Brief/PDF, test files, Git history,
  Judge access, evidence, and user-supplied MP4 are present.
- Optional/bonus: mentions, assignments, self-learning and data-decay are implemented; Ambient
  Voice remains **partial bonus** only.
- Recommended demo gaps: deployed new-note/manual phrase-selection controls are not shown; they are
  accurately classified as `recommended substep not shown`.
- Authorized next steps: use GitHub browser/device authorization for a non-force push, then create
  and verify source/submission ZIPs. Do not upload the MP4, password file, API key, database, or ZIP
  to GitHub. Do not send the email.
