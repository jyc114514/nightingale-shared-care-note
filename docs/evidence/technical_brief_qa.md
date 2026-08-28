# Technical Brief PDF QA - 2026-08-26

The first section below is retained as historical evidence. The final release-candidate QA is
recorded after it and supersedes the old PDF metrics and hash.

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

## Source update notice - 2026-08-27

`docs/TECHNICAL_BRIEF.md` now records the independent Simplified Chinese UX-01 result and the
Staff-first deployed rehearsal. The PDF above was intentionally not regenerated in this task, so
its older UX wording and hash remain historical evidence; it must not be treated as the final PDF
after the source update.

## Final release-candidate PDF QA - 2026-08-28

- Source HTML: [`technical_brief.html`](../../deliverables/technical_brief.html)
- Editable source: [`TECHNICAL_BRIEF.md`](../TECHNICAL_BRIEF.md)
- PDF page count: **3** A4 pages.
- Text extraction check: all three pages contain non-empty text; page text lengths were **1,539**,
  **1,732**, and **2,581** characters. The extracted text contains the current 85-backend-test,
  37-Vitest, 18-Playwright, and 56.053 ms metrics, and contains no `Level-C`/`Level C` wording or
  superseded 81/86-test and 67.823 ms metrics.
- Raster render check: all three pages were rendered with the bundled Poppler `pdftoppm` binary
  and visually inspected. Diagrams, cards, tables, footers, page numbers, and text margins are
  legible with no clipping, overlap, or footer collision.
- Final PDF SHA-256: `F6AA0C764D949B016FA460ED0CFFD7ABBEDEE82AE5A662CA76F2560084C7EFA0`.

The final brief accurately describes prerecorded synthetic audio with a prepared timestamped
transcript, the optional DeepSeek boundary, Render PostgreSQL/HTTPS evidence, and the current
local regression results. It does not claim ASR inference, microphone capture, model quality,
clinical production readiness, or complete final-video content QA.
