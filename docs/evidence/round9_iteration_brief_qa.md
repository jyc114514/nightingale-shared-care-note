# Round 9 iteration brief PDF QA

## Earlier pre-closure PDF QA

Date: 2026-09-03

Artifact: [`Nightingale_Real_Clinic_Iteration_Brief.pdf`](../../deliverables/iteration/Nightingale_Real_Clinic_Iteration_Brief.pdf)

- Editable HTML source: [`real_clinic_iteration_brief.html`](../../deliverables/iteration/real_clinic_iteration_brief.html)
- Renderer: [`render_round9_brief.mjs`](../../scripts/render_round9_brief.mjs), Playwright Chromium,
  A4 print CSS, and `printBackground`.
- Page count: **3**.
- Extracted text lengths: **2,071**, **2,150**, and **2,781** characters.
- Raster QA: all three final PDF pages were rendered with PyMuPDF and visually inspected. No
  clipping, overflow, diagram collision, unreadable table, or footer overlap was observed.
- Forbidden-term scan in extracted PDF text: `password` 0, `api key` 0, `cookie` 0, `Level-C` 0,
  `Level C` 0.
- PDF size: **102,903 bytes**.
- PDF SHA-256: `3D5D3FD29F136E63B3C7B85DA6F6C5F32DCE8D5C43C7AB8E79513815480A240B`.

The brief uses only Round 9 evidence and labels the hosted authenticated benchmark as pending.
It does not replace [`Nightingale_Technical_Brief.pdf`](../../deliverables/Nightingale_Technical_Brief.pdf),
and it does not claim live LLM/ASR quality, microphone capture, FHIR conformance, clinical
validation, or production compliance.

## Closure regeneration

The PDF was regenerated after the Round 9 closure evidence update. The final extracted text
lengths are **2,071**, **2,196**, and **2,541** characters for pages 1-3. The final artifact is
**102,303 bytes** with SHA-256
`1DB616B6F6D9D7636B1AF485D30A63C817A3FDF87B3546FDCD871BD60FD815C8`.

The closure PDF includes `4f4fc84`, `real-clinic-rc6`, PostgreSQL CI run `33702459026`, Render
deploy `dep-dacd2lgn74is73co3t2g`, 86.62% global application coverage, the protected-first Staff
canary, and the authenticated hosted benchmark limitation. All three pages were raster-rendered
and visually inspected after this regeneration; no clipping, overflow, collision, unreadable
table, or footer overlap was observed. Forbidden-term scan remained zero for `password`, `api key`,
`cookie`, `Level-C`, and `Level C`.
