# Technical Brief PDF QA - 2026-08-26

Artifact: [`Nightingale_Technical_Brief.pdf`](../../deliverables/Nightingale_Technical_Brief.pdf)

- Source HTML: [`technical_brief.html`](../../deliverables/technical_brief.html)
- Editable source: [`TECHNICAL_BRIEF.md`](../TECHNICAL_BRIEF.md)
- Renderer: [`render_technical_brief.mjs`](../../scripts/render_technical_brief.mjs), Playwright
  Chromium with `printBackground` and CSS A4 sizing.
- PDF page count: **3**.
- Text extraction check: all three pages contain non-empty text; page text lengths were 1,417,
  1,766, and 2,186 characters respectively. The architecture, schema, evidence, and limitation
  sections are present in the expected page groups.
- Raster render check: all three pages were rendered to PNG with the installed PyMuPDF fallback
  because Poppler command-line binaries were not available on PATH. Each page was visually
  inspected after the final regeneration.
- Visual result: no clipped diagram, page overflow, unreadable table, or footer overlap remains.
  Page 3 was tightened once after inspection to keep the safety card and footer separated.
- The final regeneration reflects the reproducible backend coverage result of 87% and does not
  retain the earlier 97% self-report that could not be reproduced with the same command.

The PDF describes local synthetic evidence and explicitly separates measured behavior from
unverified PostgreSQL, deployment TLS/encryption-at-rest, external-provider, and UX sign-off
claims.
