# Public release checklist

Status: **private repository; no public release performed**.

The GitHub repository must remain private until **2026-08-28 18:00 Asia/Shanghai**. Any
visibility change requires the user/administrator to approve and perform the action after the
final review. No scheduled GitHub Action may change visibility.

Before any future public release:

- Run a final tracked, working-tree, Git-history, and ZIP secret scan.
- Confirm no GitHub, Render, or DeepSeek credentials, key paths, `.nightingale-local.json`,
  databases, runtime logs, environment dumps, model caches, or raw uploaded audio are present.
- Inspect GitHub Actions logs and artifacts, if Actions are enabled.
- Confirm deployment secrets exist only in the hosting secret store and that `LLM_PROVIDER=fixture`
  and `VOICE_PROVIDER=fixture` remain the public-demo defaults; the Voice path is still Level C
  only.
- Recheck `ATTRIBUTION.txt`, dependency licenses, synthetic-only fixtures, and Voice scope labels.
- Reconfirm independent UX-01 evidence and deployment TLS/encryption-at-rest evidence.
- Review the final video and package contents before sending any submission email.

The current repository is intentionally private. No email, GitHub Release, Pages site, public
visibility change, or final video upload is part of this checkpoint.
