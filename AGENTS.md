# Nightingale project operating instructions

## Source of truth

- `requirements.txt` is the authoritative candidate brief. Do not edit or reinterpret it silently.
- Read `docs/PROJECT_PLAN.md`, `docs/ACCEPTANCE_MATRIX.md`, and `docs/CODEX_RUNBOOK.md` before changing code.
- If a convenient implementation conflicts with the brief, preserve the brief and report the conflict.

## Product and safety boundary

- Use synthetic data only. Never add real patient data, credentials, API keys, access tokens, or identifying logs.
- Treat AI output as a suggestion. It may rank, summarize, or extract, but it must not silently overwrite a human-authored source or present an unsupported diagnosis as fact.
- Keep `display_priority`, explicit source `risk_level`, and clinician confirmation as separate fields.
- Every AI-derived highlight must resolve to a specific immutable source version and source span.
- Redact names, IC/ID numbers, and phone numbers before any text is sent to an external LLM. Log identifiers and metadata, not raw note text.
- A patient must never receive internal comments or raw AI-scribed notes from any API response.

## Scope order

1. Mandatory security and data correctness: clinic scoping, role permissions, revision history, audit metadata, optimistic concurrency, and provenance.
2. Mandatory product path: Glance View, longitudinal timeline, three AI-scribed entry types, comments, and source navigation.
3. AI processing and warm-path performance.
4. Bonus self-learning importance and data-decay representation.
5. Ambient voice only if every mandatory gate is green and delivery assets are already complete.

Do not trade a mandatory gate for a bonus feature. Do not implement CRDT/OT in this prototype.

## Architecture guardrails

- Preferred implementation is a FastAPI backend, React/TypeScript frontend, and PostgreSQL target database, as detailed in `docs/PROJECT_PLAN.md`.
- Server-side authorization is canonical. Hiding a control in the UI is never authorization.
- Use immutable `entry_versions`. A revert creates a new version that copies earlier content; it never removes history.
- Different entries or sections may update independently. A same-section stale write must return a deterministic conflict, preserve both submissions, and never use silent last-write-wins.
- Clinician authority resolves semantic truth; it does not permit erasing patient, staff, or AI source records.
- Keep LLM calls off the Glance View read path. The warm read must use precomputed/materialized data.
- Do not expose a database service-role credential to the browser.

## Required verification

The repository must contain and run these exact test files:

- `test_rbac_scope.py`
- `test_revision_history.py`
- `test_highlight_provenance.py`
- `test_concurrent_edits.py`
- Bonus: `test_self_learning_importance.py`

Also validate frontend lint/type checks, at least one end-to-end happy path, redaction behavior, and a recorded warm-path P95 measurement. Tests must exercise real application behavior rather than reimplementing the expected logic inside the test.

## Working method

- Work one phase at a time using `docs/CODEX_RUNBOOK.md`.
- Before editing, state the phase, owned files, success criteria, and verification commands.
- After each phase, update the status column and evidence links in `docs/ACCEPTANCE_MATRIX.md`.
- Keep migrations, shared configuration, and dependency manifests on one controlled write path.
- Preserve unrelated user changes. Do not rewrite the project structure opportunistically.
- Local, reversible implementation and tests are authorized once the user asks to start building. External account creation, deployment, email submission, purchases, and destructive operations require explicit authorization.

