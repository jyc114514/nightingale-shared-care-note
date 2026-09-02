# Nightingale real-clinic iteration — Round 9

Date: 2026-09-03

## Current status

**ROUND 9 PARTIAL — FULL APPLICATION LIVE; AUTHENTICATED HOSTED BENCHMARK PENDING.**

The Uvicorn access-log regression was reproduced with the real `AccessFormatter`, fixed without
changing migrations, dependencies, Voice, DeepSeek, or product data semantics, and verified in
PostgreSQL 18 CI before the existing Render service was updated. The exact deployed code is
`c6e9851288c745ceb66dad32078d1385ffbe3424`; the service is Live at
<https://nightingale-shared-care-note.onrender.com>.

## What is evidenced

- Safe logging preserves formatter-compatible access arguments, redacts query values, and fails
  closed on sanitizer errors. See [`round9_safe_logging_recovery.md`](docs/evidence/round9_safe_logging_recovery.md).
- The existing Render service, managed PostgreSQL 18 target, HTTPS redirect, anonymous health and
  asset checks, Staff/Clinician/Patient canaries, and 15/15 sustained watch are recorded in
  [`round9_render_live.md`](docs/evidence/round9_render_live.md).
- The local synthetic iteration demo is available as a 54.76-second 1280×720 WebM with visible
  English captions. Its QA is in [`round9_demo_qa.md`](docs/evidence/round9_demo_qa.md).
- The iteration brief PDF is a separate artifact from the original Technical Brief.

## Deliberate non-claims

The current production Glance top-six is influenced by accumulated synthetic rehearsal state, so
the protected allergy/publication controls were not observable in the live top-six and are not
claimed as live-canary passes. No production cleanup was performed. The authenticated hosted
benchmark remains pending because no safe authenticated request surface was available without
extracting cookies/tokens. Global `app` coverage measured 83.30% because standalone scripts are
included; runtime application coverage excluding those scripts measured 92.9%. These are visible
quality caveats, not hidden by changing thresholds.

This round does not claim clinical production readiness, general clinical NLP, live ASR, live
DeepSeek output, FHIR conformance, or human final-video approval. It does not create the final
submission ZIP or send email.
