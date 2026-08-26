# Technical Brief PDF QA - 2026-08-26

Artifact: [`Nightingale_Technical_Brief.pdf`](../../deliverables/Nightingale_Technical_Brief.pdf)

- Source HTML: [`technical_brief.html`](../../deliverables/technical_brief.html)
- Editable source: [`TECHNICAL_BRIEF.md`](../TECHNICAL_BRIEF.md)
- Renderer: [`render_technical_brief.mjs`](../../scripts/render_technical_brief.mjs), Playwright
  Chromium with `printBackground` and CSS A4 sizing.
- PDF page count: **3**.
- Text extraction check: all three pages contain non-empty text; page text lengths were 1,505,
  1,759, and 2,568 characters and include the architecture, schema, Phase 8 evidence, demo, and
  limitation sections.
- Raster render check: all three pages were rendered to PNG with the bundled Poppler `pdftoppm`
  binary. Each page was visually inspected after the final regeneration.
- Visual result: no clipped diagram, page overflow, unreadable table, or footer overlap remains.
- Metrics in the brief match the Phase 8 evidence: backend 71 tests, 88% coverage,
  frontend 19 Vitest tests, Playwright 12 tests, and warm-path P95 67.823 ms.
- The brief also records the optional DeepSeek adapter, redaction boundary, bounded live smoke,
  contextual comments/tasks, fixed internal preview viewports, and the human UX-01 limitation.
- Final PDF SHA-256: `E07AEBA2C8B7E0623DF61C709AD3CB46DD24EE797AD3E8E14B3341009CAB3827`.

The PDF describes local synthetic evidence and explicitly separates measured behavior from
unverified PostgreSQL, deployment TLS/encryption-at-rest, external-provider, final-video, and
human UX sign-off claims.
