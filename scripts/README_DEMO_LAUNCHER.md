# One-click local demo launcher

The launcher is a Windows convenience wrapper around the existing manual setup. It uses only
synthetic data, runs Alembic before seeding, starts Uvicorn and Vite on localhost, waits for both
health checks, and opens the browser only after both services are ready.

## Double-click

- `Start Nightingale Demo.cmd` starts the English demo.
- `启动 Nightingale 中文演示.cmd` starts the Chinese chrome demo.
- `Stop Nightingale Demo.cmd` stops only the backend and frontend PIDs recorded by this repository.

On first run, the launcher asks for a local synthetic demo password without echoing it. Later
starts reuse the seeded database and tell the user to use the password chosen during first run.
The password and session secret are never written to `runtime.json` or launcher logs.

## Script options

```powershell
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_demo.ps1 `
  -DemoPassword 'local-only-password' -Language en -NoBrowser -Setup
```

Supported options include `-DemoPassword`, `-Language en|zh-CN`, `-NoBrowser`, `-Setup`,
`-TimeoutSeconds`, and the test-only `-RuntimeDirectory` override.

Runtime metadata and stdout/stderr are written under `artifacts/local-runtime/`, which is ignored
by Git. The stop script verifies both the recorded PID and its command line before using
`taskkill /T /F`; an unknown process owning port 8000 or 5173 is never killed.

Manual setup commands in the repository README remain supported and are the source of truth for
development workflows. The launcher does not deploy, contact an external provider, or use an LLM.
