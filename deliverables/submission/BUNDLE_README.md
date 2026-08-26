# Nightingale local submission bundle

This folder contains the locally assembled handoff bundle for the synthetic Nightingale prototype.
The source ZIP is generated from the final Git checkpoint and excludes `.git`, dependency trees,
temporary databases, test reports, credentials, and API keys.

Included handoff materials:

- `Nightingale_source_<commit>.zip`: reproducible source snapshot.
- `Nightingale_Technical_Brief.pdf`: three-page technical brief.
- `ATTRIBUTION.txt`: direct dependency and license audit.
- `README.md`: setup, verification, security boundary, and limitations.
- `SUBMISSION_EMAIL_DRAFT.md`: copyable draft; Codex does not send it.
- `MANIFEST.txt`: generated SHA-256 inventory for the local bundle.

The final video and human UX-01 sign-off are intentionally not claimed. Hosted PostgreSQL,
TLS/encryption-at-rest, provider data-processing/compliance, and model-quality evidence remain
outside this local bundle. The source snapshot records one bounded synthetic DeepSeek smoke without
including any key, path, prompt, or response body.
