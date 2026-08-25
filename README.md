# Nightingale

Nightingale is a synthetic-data prototype for a clinic-scoped, longitudinal care-note
collaboration product. The repository is currently at **Phase 0: reproducible scaffold**.
Phase 0 intentionally proves the application boundary and developer workflow; it does not
implement clinical workflows.

## Current scope

Implemented in this phase:

- FastAPI backend with a fixed, non-sensitive `GET /health` endpoint.
- React/TypeScript/Vite shell showing the project name, Phase 0 status, and backend health.
- Locked backend and frontend dependencies, test/lint/type-check/build commands, and local Git.
- Synthetic-data and secret-safe repository defaults.

Deferred to later gates: authentication and server-side RBAC, patient/timeline data, Glance
View/Top Card, comments, revisions, provenance, AI processing, redaction-provider boundary,
performance measurement, self-learning importance, data decay, and voice capture. Nothing in
the Phase 0 shell should be interpreted as a clinical, security, or performance claim.

The repository-root `requirements.txt` is the challenge brief, **not** a pip requirements
file. Never run `pip install -r requirements.txt`.

## Verified Python environment

All backend commands use the existing confirmed Conda environment, not system Python and not
a project-created virtual environment:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
& $pyExe --version
& $pyExe -m pip check
```

The verified interpreter is Python 3.10.20 and the environment had a clean `pip check` before
and after the Phase 0 additions. The project plan targets Python 3.12; this phase preserves the
existing environment as required by the Phase 0 prompt and pins dependencies compatible with it.
See [docs/ENVIRONMENT_REPORT.md](docs/ENVIRONMENT_REPORT.md) for the package delta and evidence.

## Backend

Install or reconcile only the lockfile-pinned Phase 0 packages in the confirmed environment:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
$uvExe = 'C:\Users\JI YANCHEN\.local\bin\uv.exe'
$env:UV_CACHE_DIR = Join-Path $PWD '.uv-cache'
& $uvExe pip install --python $pyExe --requirement backend\requirements.lock
```

Start the API from the backend directory:

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
Push-Location backend
& $pyExe -m uvicorn app.main:app --reload --port 8000
Pop-Location
```

Backend checks (the `--no-cache` flags avoid an environment-specific cache-directory issue):

```powershell
$pyExe = 'C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe'
Push-Location backend
& $pyExe -m ruff check --no-cache app tests
& $pyExe -m ruff format --check --no-cache app tests
& $pyExe -m mypy app tests
& $pyExe -m pytest
Pop-Location
```

## Frontend

The frontend uses the project-local pnpm lockfile. The current machine's PowerShell execution
policy blocks the `pnpm.ps1` shim, so the reproducible command uses the existing `pnpm.cmd`
path directly:

```powershell
$pnpmCmd = 'C:\Users\JI YANCHEN\AppData\Roaming\npm\pnpm.cmd'
Push-Location frontend
& $pnpmCmd install
& $pnpmCmd lint
& $pnpmCmd test
& $pnpmCmd type-check
& $pnpmCmd build
Pop-Location
```

Run the frontend with the backend in a second terminal:

```powershell
$pnpmCmd = 'C:\Users\JI YANCHEN\AppData\Roaming\npm\pnpm.cmd'
Push-Location frontend
& $pnpmCmd dev
Pop-Location
```

Open the printed Vite URL. The shell calls `http://localhost:8000/health` by default; set
`VITE_API_BASE_URL` only when a later local setup needs a different backend address.

## Safety and repository rules

- Only synthetic data belongs in this repository. Do not add real patient data, credentials,
  API keys, access tokens, or identifying logs.
- `.env` and `.env.*` are ignored; `.env.example` contains placeholders only.
- No Docker, external LLM, external account, deployment, or remote Git repository is required
  or configured by Phase 0.
- The local Git repository has no remote. Do not push or publish it without separate approval.
