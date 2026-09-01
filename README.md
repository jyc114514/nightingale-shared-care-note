# Nightingale

Nightingale is a synthetic-data prototype for a clinic-scoped longitudinal care-note
collaboration product. The repository is at **Phase 9 / final release candidate**: Gate A-C
authentication, clinic-scoped RBAC, immutable revisions, audit metadata, optimistic concurrency,
Glance/timeline/source navigation, bilingual UI chrome, safe one-click demo startup, mentions,
internal assignments, and metadata-only near-real-time invalidation are implemented locally.

The product path is designed around a simple review workflow: make the next step visible, keep the
original record easy to verify, and preserve human review for every suggestion. The hosted Render
evaluation uses synthetic data, managed PostgreSQL 18, fixture AI, and a pre-recorded Voice example
with a prepared timestamped transcript. It is an evaluation prototype, not a clinical production
guarantee. Technical provider, redaction, performance, and deployment boundaries are documented
below and in the Technical Brief. Judge entry points are collected in [`JUDGE_ACCESS.md`](JUDGE_ACCESS.md),
and the final recording artifact is kept outside GitHub and included only in the submission bundle.
The repository-root `requirements.txt` is the candidate brief,
**not** a pip requirements file; never run `pip install -r requirements.txt`.

## Runtime and database

All backend commands use the already verified Conda environment:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
& $pyExe --version
& $pyExe -m pip check
```

The prototype deliberately runs on Python 3.10.20 in that shared environment. This is a
documented prototype limitation, not a production recommendation; production migration to
Python 3.12+ is a follow-up. The shared environment is not upgraded or replaced during this
sprint.

SQLite is used for local development/tests. The hosted Render evaluation uses PostgreSQL through
`DATABASE_URL`; local development can still use SQLite. Copy `.env.example` to a local `.env`, set
a random `SESSION_SECRET` of at least 32 characters, and set `DEMO_SEED_PASSWORD` only when
running the synthetic seed. `.env` is ignored by Git.

## Backend setup

Install the lockfile-pinned dependencies and apply the real Alembic schema:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
$uvExe = 'C:\Users\JI YANCHEN\.local\bin\uv.exe'
$env:UV_CACHE_DIR = Join-Path $PWD '.uv-cache'
& $uvExe pip install --python $pyExe --requirement backend\requirements.lock

Push-Location backend
& $pyExe -m alembic upgrade head
& $pyExe -m uvicorn app.main:app --reload --port 8000
Pop-Location
```

For a local synthetic demo, use a local-only password and run the idempotent seed. The seed
refuses to run unless the database is at the current Alembic head and prints opaque IDs/counts,
not note text or credentials:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
$env:DEMO_SEED_PASSWORD = 'set-a-local-only-password'
Push-Location backend
& $pyExe -m alembic upgrade head
& $pyExe -m app.scripts.seed_demo
Pop-Location
Remove-Item Env:DEMO_SEED_PASSWORD
```

The seed creates two synthetic clinics, five users, two synthetic patients, ten entries, three
distinct system AI-scribed entry types, six source-linked highlights/materialized Glance rows,
two source-anchored penicillin assertions with one protected conflict, a threaded internal
comment fixture, a bounded wrong-dosage publication draft, and a derived archival summary with
immutable source pointers. Re-running it preserves aggregate counts. Mentions and tasks are
created through the clinic-scoped collaboration APIs so the seed remains deterministic and
read-only by default.

### Round 4 patient publication gate

Round 4 adds a local, synthetic, portal-only publication workflow. `Accept` on an internal AI
highlight never publishes to a patient. Staff can prepare/edit a draft; only a Clinician can
approve and then explicitly publish it. The bounded metformin dosage evidence check is
source/version anchored and fails closed on mismatch, ambiguity, or unsupported grammar.
Recall and correction are separate versioned transitions, while the Patient projection exposes
only current published content or safe notices. See
[`PATIENT_PUBLICATION_BOUNDARY.md`](docs/PATIENT_PUBLICATION_BOUNDARY.md), the
[`Round 4 design`](docs/ROUND4_PATIENT_PUBLICATION_DESIGN.md), and the
[`Round 4 evidence`](docs/evidence/round4_patient_publication.md).

### Round 2 local safety and exposure iteration

The current local iteration adds Alembic `0012_glance_impressions`, a shared provider-free Glance
candidate builder, metadata-only exposure impressions, and a protected dual-source allergy
conflict review drawer. Staff can inspect both sources but cannot adjudicate; clinicians use a
versioned decision with database CAS; patients receive none of the conflict, assertion, or
impression data. Exposure records contain candidate/surface metadata only and are an observable
denominator for later evaluation; they do not claim IPS, counterfactual correction, or unbiased
self-learning. The local evidence is recorded in
[`round2_conflict_ui_exposure.md`](docs/evidence/round2_conflict_ui_exposure.md) and
[`round2_warm_path.md`](docs/evidence/round2_warm_path.md). This iteration remains local-only:
it does not push, deploy, call DeepSeek, or change Voice.

### Round 3 local safe-failure iteration

The current local resilience slice adds Alembic `0013_ai_provider_resilience`, a persistent
clinic/provider circuit with `closed`, `open`, and `half_open` states, and a bounded DeepSeek
adapter budget of 8 seconds per attempt, 12 seconds total, and 2 attempts. Provider failures are
never silently replaced by fixture output. Internal users can query the clinic-scoped provider
status; the AI panel exposes available/degraded/temporarily unavailable states while preserving
existing Glance, timeline, tasks, comments, and source navigation. The application logger accepts
only allowlisted metadata, unexpected exceptions return a generic response, and the explicit local
log audit command is:

```powershell
Push-Location backend
& $pyExe -m app.scripts.audit_phi_logs path\to\local.log --known-name "Synthetic Patient"
Pop-Location
```

Round 3 remains local-only and synthetic. It does not provide a durable queue, automatic replay,
third-party retention evidence, live provider calls, PostgreSQL production evidence, or clinical
SLA.

## Gate B API and UI

- `POST /auth/login`, `GET /auth/me`, and `POST /auth/logout` use an HttpOnly signed cookie.
- `GET /patients` and `GET /patients/{patient_id}/timeline` are clinic/link scoped; patient
  projections omit internal entries, comments, raw AI notes, conflicts, and revision history.
- `GET /patients/{patient_id}/glance` returns at most six deterministic active highlights and
  excludes rejected/superseded items. It reads only the `patient_glance_items` materialized
  projection; it does not call a provider.
- `GET /highlights/{highlight_id}/source` resolves the immutable entry version, exact quote,
  Python Unicode-codepoint offsets, and source reference.
- Clinicians can create manual highlights and review suggestions; staff can read/comment but
  cannot accept/reject; admins are read-only; patients cannot access internal highlights.
- `GET/POST /entries/{entry_id}/comments` supports same-entry threaded replies and
  `PATCH /comments/{comment_id}/resolution` supports resolve/unresolve.
- Existing Gate A routes provide role-owned edits, immutable version history, diff, revert-as-new-
  version, and deterministic `409` stale-write conflicts.
- `POST /patients/{patient_id}/ai-processing` accepts the three AI-scribed entry types through a
  typed redacted payload. The deterministic fixture remains the default; an explicitly configured
  optional DeepSeek V4 Flash adapter uses only redacted synthetic text and never overwrites a human
  entry. Provider failures stay failures and do not silently fall back to fixture.
- `GET /ai-processing/provider` exposes only safe provider name/model/configured metadata to
  authorized staff/clinicians; it never returns a key, key-file path, or base URL.
- `GET /patients/{patient_id}/ai-processing/provider-status` exposes clinic-scoped availability,
  circuit state, bounded retry-after, and whether new suggestions are available to internal users.
  It never contacts the provider or exposes keys, URLs, response bodies, or account data.
- `GET /ai-processing/{job_id}` exposes job metadata and safe error codes, not raw input,
  provider prompts, or provider responses.
- `POST /highlights/{highlight_id}/feedback` records clinic-scoped staff/clinician feedback with
  an idempotency key. Feedback updates a bounded adaptive ranking contribution and the
  materialized Glance projection; it never mutates explicit risk or provenance.
- `GET /patients/{patient_id}/context` returns hot full-detail entries, warm metadata indexes,
  and derived archival periods. `POST /patients/{patient_id}/context/refresh` rebuilds only the
  derivative summaries for staff/clinicians; canonical entries and immutable versions are never
  deleted or rewritten.
- Cold summaries carry a policy version, manifest hash, source entry/version pointers, and an
  explicit “Derived summary · not the original record” disclosure. Each source row also shows
  authorized entry type, occurred time, and immutable version. Open actions, explicit risk,
  active conflicts, unresolved discussion, pinned/accepted highlights, and clinician-confirmed
  care-plan entries remain protected from compression.
- `GET /patients/{patient_id}/mentionable-users` returns only active staff/clinician collaborators
  in the current clinic. Comment creation accepts stable `mentioned_user_ids`; it never guesses
  identities by scanning comment text.
- `GET/POST /patients/{patient_id}/tasks` and `PATCH /tasks/{task_id}` provide clinic-scoped
  assignments with source entry/comment pointers, assignee validation, status transitions, and
  deterministic stale-version `409` conflicts. Patient task access is denied server-side.
- `GET /patients/{patient_id}/events` is a persisted metadata-only SSE invalidation stream with
  cookie authentication, patient scope, heartbeat, reconnect through `Last-Event-ID`, and no raw
  note/comment/title/quote payload. The browser refetches canonical APIs after an event.

The frontend uses real cookie login and `/auth/me`, a clinic-scoped patient list, a calm light
clinical workspace, Top Card, timeline, source click-to-focus/scroll, immutable Unicode
codepoint highlighting, comments, version history, diff/revert, conflict comparison, AI review
badges, role-aware controls, an internal AI Scribe Demo panel, a collapsed **Why ranked?**
explanation with pin/unpin feedback,
English/简体中文 application-chrome localization, a read-only bilingual Learning Guide, keyboard
mention autocomplete, contextual assignment/task drawers, fixed-viewport Desktop/Mobile demo
preview, and a reconnecting live-update indicator. Clinical
note content, comments, quotes, revisions and user-entered source data remain in their original
language; the UI never calls a translation API.
There is no UI-only role switch.

## Phase 9 local demo and production boundary

Double-click `Start Nightingale Demo.cmd` for English or `启动 Nightingale 中文演示.cmd` for
Chinese UI chrome. The launcher discovers the existing local Python/pnpm/Node tools, runs
lockfile checks, `alembic upgrade head`, first-run synthetic seed, backend/frontend health checks,
and opens the browser only after both services are ready. It records only verified child PIDs and
logs under ignored `artifacts/local-runtime/`; `Stop Nightingale Demo.cmd` verifies the PID and
executable/health boundary before stopping them. Unknown port owners are never killed.

Manual setup commands remain supported. `Configure DeepSeek.cmd` stores only an external key-file
path in ignored `.nightingale-local.json`; `Use Local Fixture.cmd` restores the no-network default.
Clinical source text is deliberately not translated.

The optional DeepSeek adapter uses `deepseek-v4-flash` through the official
`https://api.deepseek.com/chat/completions` endpoint. It receives only validated redacted synthetic
text and returns schema-checked summary/action fields; local code computes immutable codepoint
offsets and sets risk/provenance/review state. A provider failure is recorded as a safe error and
never silently becomes fixture output. The bounded live smoke is recorded in
[`deepseek_live_smoke.md`](docs/evidence/deepseek_live_smoke.md); it is not a model-quality
evaluation or production compliance claim.

The Phase 7.1/8 delivery set includes the editable and rendered Technical Brief, attribution audit,
demo script/shot list, UX timing protocol, deployment checklist, launcher smoke evidence, and
synthetic browser screenshots. Phase 9 adds a Docker/Render production-readiness path and a
bounded prerecorded Voice fixture. Render enables only `VOICE_PROVIDER=fixture` and keeps
`LLM_PROVIDER=fixture`; the Docker image still does not install Voice dependencies or model
weights.
The original final recording is a local submission artifact; it is not tracked or uploaded to
GitHub. Its content QA remains a separate human-review gate.

For judge entry points, use [`JUDGE_ACCESS.md`](JUDGE_ACCESS.md). The final recording filename is
`新标签页 - Google Chrome 2026-08-28 11-37-05.mp4`; it is included only in the final submission ZIP,
not in the GitHub repository. The editable brief is [`docs/TECHNICAL_BRIEF.md`](docs/TECHNICAL_BRIEF.md),
and the rendered brief is [`deliverables/Nightingale_Technical_Brief.pdf`](deliverables/Nightingale_Technical_Brief.pdf).
The final candidate-brief audit is [`docs/FINAL_REQUIREMENTS_AUDIT.md`](docs/FINAL_REQUIREMENTS_AUDIT.md).
The demo password is supplied separately in the submission email.

The Voice section is intentionally not continuous ambient capture. It plays two small, prerecorded
synthetic WAV fixtures, displays prepared timestamped transcript segments, and labels confidence as
unavailable. The achieved status is: “Bounded prerecorded synthetic audio with prepared transcript
and segment provenance; no ASR inference, diarization, or microphone capture.”

## Bonus importance logic

The adaptive ranking path uses a closed structured feature signature derived from entry type,
item kind, source kind, action state, explicit risk, and a normalized topic category. It does not
use embeddings, external LLM calls, patient identifiers, names, quotes, or raw free text.

```text
final display priority = clamp(
  base priority + recency + explicit risk + unresolved action
  + clinician confirmation + bounded adaptive feedback,
  0, 100
)
```

Adaptive feedback is bounded to `[-12, +12]`, is clinic-scoped and idempotent, and is kept
separate from medical risk, source provenance, and clinician truth. Glance reads remain provider-
free and consume only the materialized projection. The UI labels this as “Ranking priority, not a
medical risk score”.

## Verification

Backend:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
Push-Location backend
& $pyExe -m ruff check --no-cache app tests migrations
& $pyExe -m ruff format --check --no-cache app tests migrations
& $pyExe -m mypy app tests
& $pyExe -m pytest
Pop-Location
```

At the final release-candidate application checkpoint, this suite reports **85 passed**. Reproducible coverage is **88%**
when run with `pytest --cov=app`; the percentage includes standalone benchmark/seed scripts that
are not exercised by the application suite.

The repository contains the required real-application tests `test_rbac_scope.py`,
`test_revision_history.py`, `test_highlight_provenance.py`, and `test_concurrent_edits.py`, plus
`test_redaction.py`, `test_ai_provider_boundary.py`, `test_ai_processing.py`, and
`test_materialized_glance.py`, `test_self_learning_importance.py`, `test_data_decay.py`, and
`test_voice.py`. They use HTTPX `AsyncClient` with `ASGITransport`; no old
`TestClient/httpx` warning is hidden. Migration tests use Alembic to create the database and
prove that seed does not call `Base.metadata.create_all()`.

Frontend unit/build checks:

```powershell
$pnpmCmd = 'C:\Users\JI YANCHEN\AppData\Roaming\npm\pnpm.cmd'
Push-Location frontend
& $pnpmCmd install --frozen-lockfile
& $pnpmCmd lint
& $pnpmCmd test
& $pnpmCmd type-check
& $pnpmCmd build
Pop-Location
```

Real browser checks:

```powershell
Push-Location frontend
& $pnpmCmd e2e
& $pnpmCmd e2e:voice
Pop-Location
```

`pnpm e2e` creates a temporary Alembic-migrated SQLite database, seeds synthetic data, starts
real Uvicorn and Vite processes on clean local ports, and runs 14 core checks at 1440x900 and
390x844. `pnpm e2e:voice` runs four isolated Voice fixture checks at the same viewports. The final
run therefore reports 18 browser checks. Scenario B
covers revisions, nested comments, keyboard mention selection, contextual assignment drawer
creation/completion, and a second browser receiving the metadata-only SSE invalidation. The
dedicated preview check verifies real internal 1440x900/390x844 iframe viewports, query
preservation, no recursive toolbar, and Escape close. The custom setup records only its own server
PIDs and teardown removes those processes, the temporary database, generated password, and
ignored `artifacts/gate-b/` screenshots.

Gate C warm-path benchmark:

```powershell
Push-Location backend
& $pyExe -m app.scripts.benchmark_warm_path
Pop-Location
```

This uses a fresh migrated file-backed SQLite database, 26 synthetic patients, 208 benchmark
entries/highlights, real Uvicorn TCP HTTP, 50 warm-up requests, 1,000 measured requests, and
10-way concurrency. The 2026-08-28 release-candidate run reports P50 44.283 ms, P95
56.053 ms, P99 81.509 ms, max 89.495 ms, and zero errors. The current evidence is
[`gate_c_warm_path.md`](docs/evidence/gate_c_warm_path.md). It is a local approximation, not a
hosted PostgreSQL production benchmark.

## Safety and repository boundary

- Only synthetic data is allowed. Do not add real patient data, credentials, API keys, access
  tokens, or identifying logs.
- The server is canonical for clinic and role authorization. Production requires secure cookies;
  credentialed browser writes are protected by the configured Origin allowlist.
- AI output is a suggestion. It cannot silently overwrite a human source or present an
  unsupported diagnosis as fact. Display priority, explicit risk, and clinician confirmation are
  separate fields.
- No external LLM key is committed or required. The optional DeepSeek path is explicitly selected,
  redaction-gated, and cost/network dependent; the fixture path remains deterministic by default.
  The Render synthetic evaluation uses managed PostgreSQL, HTTPS/TLS, and the bounded prerecorded
  Voice fixture; these are evaluation evidence, not clinical compliance evidence. The original
  final video is not uploaded to GitHub, and the test password is supplied separately in the
  submission email. The local Technical Brief PDF is delivery evidence, not hosted compliance
  evidence.
- Voice is prerecorded synthetic audio with a prepared transcript fixture. There is no microphone
  capture, local Whisper success claim, diarization, or production PHI audio path.
- The local redaction/provider boundary and materialized warm path/P95 are implemented and
  evidenced, but do not establish hosted production guarantees.
