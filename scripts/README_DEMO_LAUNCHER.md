# One-click local demo launcher

The launcher is a Windows convenience wrapper around the existing manual setup. It uses only
synthetic data, runs Alembic before seeding, starts Uvicorn and Vite on localhost, waits for both
health checks, and opens the browser only after both services are ready.

## Double-click

- `Start Nightingale Demo.cmd` starts the English demo.
- `启动 Nightingale 中文演示.cmd` starts the Chinese chrome demo.
- `Stop Nightingale Demo.cmd` stops only the backend and frontend PIDs recorded by this repository.
- `Configure DeepSeek.cmd` stores an external key-file path in ignored `.nightingale-local.json`.
- `Use Local Fixture.cmd` selects the deterministic local provider without touching the external key file.

On first run, the launcher asks for a local synthetic demo password without echoing it. Later
starts reuse the seeded database and tell the user to use the password chosen during first run.
The password and session secret are never written to `runtime.json` or launcher logs.

## Optional DeepSeek adapter

The launcher remains fixture-first. Use `Configure DeepSeek.cmd` only when a local external key
file is already available. The configuration stores only `llm_provider`, `deepseek_key_file`, and
`deepseek_model`; it never copies or prints the key. On the next start, the launcher reads the key
into the backend child-process environment, clears its temporary parent variable before starting
Vite, and records only the safe provider/model in runtime metadata. The browser never receives the
key or key-file path.

The adapter calls `https://api.deepseek.com/chat/completions` with `deepseek-v4-flash`, JSON output,
disabled thinking, bounded tokens, and only the server-redacted synthetic interaction text. A live
failure stays a provider failure; it never falls back to the fixture silently. `Use Local Fixture.cmd`
restores the default path and does not delete the external key file.

## Script options

```powershell
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_demo.ps1 `
  -DemoPassword 'local-only-password' -Language en -NoBrowser -Setup
```

Supported options include `-DemoPassword`, `-Language en|zh-CN`, `-NoBrowser`, `-Setup`,
`-TimeoutSeconds`, the test-only `-RuntimeDirectory` override, and the test-only
`-ProviderOverride fixture` switch.

Runtime metadata and stdout/stderr are written under `artifacts/local-runtime/`, which is ignored
by Git. The stop script verifies both the recorded PID and its command line before using
`taskkill /T /F`; an unknown process owning port 8000 or 5173 is never killed.

Manual setup commands in the repository README remain supported and are the source of truth for
development workflows. The launcher does not deploy or contact an external provider unless the user
explicitly configures the optional DeepSeek key file.
