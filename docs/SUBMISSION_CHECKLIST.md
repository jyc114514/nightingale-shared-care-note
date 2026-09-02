# Submission checklist

## Local artifacts

- [x] `README.md` with setup, security, redaction, seed, test, and limitation instructions.
- [x] `ATTRIBUTION.txt` with observed direct dependency versions/license metadata.
- [x] `docs/TECHNICAL_BRIEF.md` editable brief.
- [x] `deliverables/Nightingale_Technical_Brief.pdf` rendered 3-page brief.
- [x] `deliverables/technical_brief.html` editable/renderable brief source.
- [x] `docs/DEMO_SCRIPT.md`, `docs/DEMO_SHOTLIST.md`, and `docs/UX_10_SECOND_TEST.md`.
- [x] `JUDGE_ACCESS.md` with live URL, verified synthetic account emails, role order, and feature map.
- [x] `docs/DEPLOYMENT_CHECKLIST.md` with explicit hosted-evidence boundary.
- [x] `docs/evidence/gate_d_bonus.md`, `docs/evidence/technical_brief_qa.md`, and final video evidence.
- [x] Phase 7/7.1 bilingual UI/Guide, one-click launcher, mentions/tasks, SSE, accessibility,
      contextual drawers and fixed-viewport preview checkpoints; final local regression evidence
      is recorded after the application checkpoint.
- [x] Independent UX-01 result: Simplified Chinese interface, approximately nine seconds, no
      coaching, four defined answers correct; role and viewport were not separately recorded.
- [ ] Final video content QA after human review. The original MP4 exists locally and its machine
      metadata/full decode are recorded, but its 10:39 duration and complete content still require
      human confirmation.

## Release gates

- [x] Mandatory local application paths and bonus paths have automated evidence.
- [x] Git checkpoint history is inspectable and current worktree is clean at the last checkpoint.
- [ ] Final clean-clone rehearsal from the final source commit; package manifest is included in the
      local submission bundle.
- [ ] Private GitHub upload verification, if authorized and authenticated.
- [ ] Final human review of screenshots/brief/demo and recorded video.
- [ ] Email submission by the user; Codex must not send it.

## Round 5 release-candidate boundary

- Round 5 local integration and scenario evidence is recorded in
  [`ROUND5_INTEGRATION_AUDIT.md`](ROUND5_INTEGRATION_AUDIT.md) and
  [`evidence/round5_release_candidate.md`](evidence/round5_release_candidate.md).
- PostgreSQL 18 GitHub Actions is prepared but not executed until the user authorizes Round 6
  external CI. No push, Render deployment, video review, PDF regeneration, or ZIP regeneration is
  part of Round 5.
