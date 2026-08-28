# Nightingale local submission bundle

This folder contains the locally assembled handoff bundle for the synthetic Nightingale prototype.
The source ZIP is generated from the final Git checkpoint and excludes `.git`, dependency trees,
temporary databases, test reports, credentials, API keys, and all MP4 files. The submission ZIP
contains the original MP4 once, with its original filename and bytes unchanged.

Included handoff materials:

- `Nightingale_source_<commit>.zip`: reproducible source snapshot.
- `Nightingale_submission_<commit>.zip`: email attachment bundle containing the source snapshot,
  delivery documents, evidence, screenshots, and the original MP4.
- `Nightingale_Technical_Brief.pdf`: three-page technical brief.
- `ATTRIBUTION.txt`: direct dependency and license audit.
- `README.md`: setup, verification, security boundary, and limitations.
- `SUBMISSION_EMAIL_DRAFT.md`: copyable draft; Codex does not send it.
- `MANIFEST.txt`: generated SHA-256 inventory for the local bundle.

The original MP4 is not uploaded to GitHub. Its machine metadata and decode result are recorded in
`final_demo_video_qa.md`; complete content playback remains a human-review item in the current
release pass. The source snapshot records one bounded synthetic DeepSeek smoke without including
any key, path, prompt, or response body. The demo password is supplied separately in the email and
is not included in either ZIP.
