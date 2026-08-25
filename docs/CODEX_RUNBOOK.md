# Codex / Luna Max runbook

## 1. What “Luna Max” means here

Select `gpt-5.6-luna` with `max` reasoning in the Codex model controls. This is a model-plus-reasoning configuration, not a shell command. Use it for one bounded phase at a time. Do not give it “build the whole challenge” as a single task.

Each phase prompt below requires the agent to read the source files, make only in-scope changes, run real verification, update the acceptance matrix, and stop with evidence. Keep migrations and shared dependency files on one sequential path.

## 2. Verified machine readiness

Detected:

- Git 2.53
- Node 24.16
- npm 11.13
- pnpm 11.22
- uv 0.11
- Existing extension folders for Python, Pylance, Jupyter, and PowerShell

Not detected on PATH:

- Python / `py`
- Docker
- Supabase CLI
- `psql`
- VS Code `code` CLI

No VS Code executable was found in the normal per-user/system install paths or Start Apps. This may mean VS Code is absent, portable, or its registration is broken. Verify this before the first IDE session.

## 3. Minimal VS Code extensions

Required for the recommended stack:

- `openai.chatgpt` — Codex
- `ms-python.python` — Python (already present in the extension folder)
- `ms-python.vscode-pylance` — Pylance (already present)
- `charliermarsh.ruff` — Ruff lint/format integration
- `dbaeumer.vscode-eslint` — frontend linting
- `esbenp.prettier-vscode` — frontend formatting
- `bradlc.vscode-tailwindcss` — Tailwind class support
- `ms-playwright.playwright` — end-to-end test runner UI

Optional, not needed on the critical path:

- `tamasfe.even-better-toml`
- `usernamehw.errorlens`

Do not spend time installing GitLens, database GUI packs, Docker extensions, REST clients, AI autocomplete competitors, or a Supabase extension before a real need appears. The repository should expose repeatable CLI commands; extensions are convenience only.

The repository includes `.vscode/extensions.json`, so VS Code can offer this exact recommendation set after it is installed.

After a working `code` command is available, the same set can be installed explicitly:

```powershell
code --install-extension openai.chatgpt
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-playwright.playwright
```

## 4. Python bootstrap policy

Use uv to provision a project-local Python 3.12 toolchain instead of depending on a missing global Python installation. Keep uv's cache and interpreter directory inside the workspace if the Codex sandbox cannot write to the default user cache. Do not commit the interpreter, virtual environment, or cache.

Expected PowerShell bootstrap shape for the implementation phase:

```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PWD '.python'
uv python install 3.12
uv venv --python 3.12 .venv
uv run python --version
```

The implementation agent should discover the exact supported uv flags and create reproducible commands in the README. It must not install Docker as a prerequisite.

## 5. Phase prompts to paste into Codex

### Phase 0 — repository and scaffold, maximum 4 hours

```text
Work only on Phase 0 of the Nightingale plan. Read requirements.txt, AGENTS.md,
docs/PROJECT_PLAN.md, docs/ACCEPTANCE_MATRIX.md, and docs/CODEX_RUNBOOK.md first.

Goal: create a reproducible project scaffold, not product features.

Use the recommended FastAPI + React/TypeScript/Vite architecture. Initialize Git,
preserve requirements.txt unchanged, add safe .gitignore rules, provision a project-local
Python 3.12 environment with uv, scaffold backend and frontend, pin dependencies with
lockfiles, and create README/technical-brief/ATTRIBUTION/test skeletons. Add .env.example
with placeholders only. Do not request, print, or commit credentials. Do not install Docker.

Create a minimal health endpoint and one rendered frontend shell so both processes can be
verified. Add lint, type-check, unit-test, and clean-start commands. Run them. Record actual
commands and results in docs/ACCEPTANCE_MATRIX.md without marking unimplemented product
requirements passed.

Stop after Phase 0. Report changed files, exact verification performed, failures/caveats,
and the next gate. Do not start RBAC, AI, or bonus features.
```

### Phase 1 — data model, authentication, RBAC, revision, concurrency

```text
Implement only Gate A from docs/PROJECT_PLAN.md. Read the current repository and matrix
before editing. Keep migrations and shared config on this single write path.

Build synthetic seeded identities for patient, staff, clinician, and admin; clinic and
patient ownership; immutable entries and entry_versions; metadata-only audit logs; revert
as a new version; and optimistic concurrency using expected_version. Enforce clinic and role
permissions in backend authorization code. A same-section stale write must return 409 and
preserve a conflict record; different sections must update independently. Never implement
authorization as a UI-only role switch.

Implement the exact required files test_rbac_scope.py, test_revision_history.py, and
test_concurrent_edits.py against real application behavior. Include cross-clinic negative
tests and patient response-field tests. Run migrations, tests, lint, and type checks. Update
only the relevant acceptance rows with evidence.

Stop when Gate A is green or when a concrete blocker is proven. Report evidence and do not
start the UI, AI, or bonus phase.
```

### Phase 2 — Top Card, timeline, comments, provenance, trust UI

```text
Implement only Gate B from docs/PROJECT_PLAN.md on top of the passing Gate A foundation.

Build a clinician/staff patient page with a six-item-or-fewer Glance View and a continuous
timeline. Support all required entry metadata and the three distinct system-authored
AI-scribed entry types. Add threaded comments with resolve/unresolve, clinician-owned and
staff-owned editing, version diff/revert UI, accept/reject states, and exact source-span
navigation.

Provenance must point to source_entry_id, immutable source_version_id, offsets, quote, and
quote hash. Add test_highlight_provenance.py plus a browser test that clicks a highlight and
visibly selects/scrolls to the exact source. Do not silently overwrite content or present AI
text as clinician-confirmed. Mentions/assignment may be added only after the required path is
green.

Use the synthetic scenario in the plan and make the UI readable at laptop and mobile widths.
Run backend tests, frontend lint/type checks, and focused browser tests. Update matrix evidence.
Stop after Gate B and report what is demonstrably usable.
```

### Phase 3 — redaction, AI boundary, materialized Glance View, performance

```text
Implement only Gate C from docs/PROJECT_PLAN.md. Preserve the passing core behavior.

Add a provider interface and deterministic fixture provider first. Then add an optional
external LLM adapter behind environment configuration; never require a live model for tests
or the demo fallback. Before any provider call, redact names, SG-style IC/ID values, and phone
numbers; validate the payload and fail closed if prohibited patterns remain. Use a provider
spy test to prove only redacted text crosses the boundary. Keep raw note text out of logs.

Process extraction/ranking off the Glance View read path. Persist validated structured output
and materialized patient_glance_items. The warm read endpoint must perform no LLM call.
Create a reproducible benchmark with warm-up, request count, concurrency, dataset description,
and JSON/Markdown output; verify P95 <= 300 ms or report the measured failure honestly.

Run all mandatory tests, lint, type checks, E2E happy path, and log/redaction checks. Update
matrix evidence. Stop after Gate C; do not begin bonus work unless every mandatory gate is green.
```

### Phase 4 — bonus cutoff

```text
First audit every Mandatory row in docs/ACCEPTANCE_MATRIX.md. If any mandatory row is not
green, fix that instead and do not build bonus features.

If the core is green, implement bounded per-clinic importance adaptation that changes display
priority only. Use positive and negative feedback, bounded adjustments, and explicit feature
contributions. Implement test_self_learning_importance.py showing a real before/after increase
for similar content without mutating source risk_level. Add a hot/warm/cold derivative retrieval
representation whose summaries always link to canonical immutable sources and whose retention
language is policy-controlled.

Do not implement ambient voice. Run the full regression suite and update evidence. Stop at the
bonus cutoff even if additional ideas remain.
```

### Phase 5 — freeze, adversarial QA, and delivery

```text
Feature freeze is active. Do not add new product features.

Audit the implementation line by line against requirements.txt and docs/ACCEPTANCE_MATRIX.md.
Test direct unauthorized API calls, cross-clinic access, stale writes, missing provenance,
redaction bypass attempts, log leakage, failed AI calls, empty/loading/error UI states, and a
clean-clone setup. Re-run the warm-path benchmark. Inspect the repository for secrets and real
identifiers.

Finish README, ATTRIBUTION.txt, and the 2–3 page technical brief. The brief must distinguish
implemented behavior, measured evidence, assumptions, deployment guarantees, and deferred work.
Create and rehearse a concise Scenarios A–C demo script. Render/inspect the brief PDF and play
back the final video. Verify every requested deliverable exists and opens.

Report a release checklist with passed/failed/deferred evidence. Do not email, upload, deploy,
or make the repository public unless the user explicitly authorizes that external action.
```

## 6. Short audit prompt after any phase

```text
Review the current phase without changing files. Compare the diff and real test output against
requirements.txt, AGENTS.md, and docs/ACCEPTANCE_MATRIX.md. List only concrete gaps, unsupported
claims, security/correctness risks, and the smallest next actions, with file references. Treat a
passing partial test as insufficient evidence for the whole acceptance row.
```
