# Nightingale recording cue card

Target: 4:20 · English UI and narration · synthetic data only

1. **Open — Clinician A**: English, Sarah Tan, `Live updates: Connected`.
2. **Glance**: `Top Card` / `What needs attention now`; show content, action, status, item kind,
   risk and `Why ranked? Ranking priority, not a medical risk score.`
3. **Source**: AI nurse card → `Open source`; show `Immutable source`, v1, code-point offset and
   exact `<mark>`; close with `Close source`.
4. **Voice Level C**: select `Synthetic nurse follow-up · clinical`; play; `Process sample` once;
   click the 8-second segment; show mock transcript, timestamps, confidence unavailable and source.
5. **Staff**: off-camera role cut; `Staff note` → `Edit` → `Save revision`; no new-note control.
6. **Mention**: `Comments` → type trailing `@clinician` → choose `@Clinician A · clinician` →
   `Add comment`; show mention metadata.
7. **Collaboration**: `Resolve` → `Unresolve`; `Pin` → `Unpin`.
8. **Clinician audit**: `Clinician section` → `Edit` → `Save revision` → `History` → `Compare`
   v1 → v2 → `Revert` v1; show new version and retained history; accept one suggestion only if
   review buttons remain.
9. **Longitudinal context**: show Hot, Warm and `Derived summary · not the original record`;
   click `View original record` and show the April 2025 Patient summary.
10. **Patient privacy**: off-camera cut to Sarah Patient; show `Internal Glance View is hidden`,
    patient timeline and only `Synthetic patient follow-up · patient`; no source button.
11. **Close**: say HTTPS/PostgreSQL/synthetic-only boundary; mention optional redacted DeepSeek
    adapter without making a live call.

Safety: never show passwords, keys, environment values, database URLs, browser storage, or a
provider console. Remove any step that fails rather than narrating success. UX-01 still needs an
independent unfamiliar participant.
