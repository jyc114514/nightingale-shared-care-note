# Technical Brief PDF QA - 2026-08-26

Artifact: [`Nightingale_Technical_Brief.pdf`](../../deliverables/Nightingale_Technical_Brief.pdf)

- Source HTML: [`technical_brief.html`](../../deliverables/technical_brief.html)
- Editable source: [`TECHNICAL_BRIEF.md`](../TECHNICAL_BRIEF.md)
- Renderer: [`render_technical_brief.mjs`](../../scripts/render_technical_brief.mjs), Playwright
  Chromium with `printBackground` and CSS A4 sizing.
- PDF page count: **3**.
- Text extraction check: all three pages contain non-empty text; page text lengths were 1,448,
  1,759, and 2,360 characters and include the architecture, schema, Phase 7 evidence, demo, and
  limitation sections.
- Raster render check: all three pages were rendered to PNG with the installed PyMuPDF fallback
  because Poppler command-line binaries were not available on PATH. Each page was visually
  inspected after the final regeneration.
- Visual result: no clipped diagram, page overflow, unreadable table, or footer overlap remains.
- Metrics in the brief match the feature-freeze evidence: backend 51 tests, 88% coverage,
  frontend 14 Vitest tests, Playwright 10 tests, and warm-path P95 67.823 ms.
- Final PDF SHA-256: `86CC98313ADFE06447406029401F45BEA4564A1374F106E96B14B6ED10A78E1C`.

The PDF describes local synthetic evidence and explicitly separates measured behavior from
unverified PostgreSQL, deployment TLS/encryption-at-rest, external-provider, final-video, and
human UX sign-off claims.
