[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $PSScriptRoot
$startScript = Join-Path $scriptRoot "scripts\start_demo.ps1"
$stopScript = Join-Path $scriptRoot "scripts\stop_demo.ps1"
$runtimeRoot = Join-Path $scriptRoot "artifacts\local-runtime\smoke"
$runtimePath = Join-Path $runtimeRoot "runtime.json"
$launcherOutput = Join-Path $runtimeRoot "launcher.stdout.log"
$launcherError = Join-Path $runtimeRoot "launcher.stderr.log"
$password = "phase7-local-smoke-password"
$launcherProcess = $null

function Assert-Condition {
  param([bool]$Condition, [string]$Message)
  if (-not $Condition) { throw $Message }
}

function Get-PortOwners {
  param([int]$Port)
  return @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
}

function Wait-File {
  param([string]$Path, [int]$TimeoutSeconds)
  $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
  while ([DateTime]::UtcNow -lt $deadline) {
    if (Test-Path -LiteralPath $Path -PathType Leaf) { return $true }
    Start-Sleep -Milliseconds 250
  }
  return $false
}

function Stop-LauncherHost {
  if (-not $launcherProcess) { return }
  $process = Get-CimInstance Win32_Process -Filter "ProcessId = $($launcherProcess.Id)" -ErrorAction SilentlyContinue
  if ($process -and ([string]$process.CommandLine).ToLowerInvariant().Contains("start_demo.ps1")) {
    & taskkill.exe /PID $launcherProcess.Id /T /F *> $null
  }
}

if (Test-Path -LiteralPath $runtimeRoot) {
  Remove-Item -LiteralPath $runtimeRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null

try {
  $launcherProcess = Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-NoExit",
    "-File", $startScript,
    "-DemoPassword", $password,
    "-NoBrowser",
    "-Setup",
    "-TimeoutSeconds", "45",
    "-RuntimeDirectory", $runtimeRoot
  ) -WindowStyle Hidden -PassThru -RedirectStandardOutput $launcherOutput -RedirectStandardError $launcherError

  Assert-Condition (Wait-File -Path $runtimePath -TimeoutSeconds 60) "runtime.json was not created"
  Assert-Condition ((Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/health").StatusCode -eq 200) "backend health failed"
  Assert-Condition ((Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:5173/").StatusCode -eq 200) "frontend health failed"

  $runtimeText = Get-Content -Raw -LiteralPath $runtimePath
  Assert-Condition ($runtimeText -notmatch "(?i)password|secret|token|cookie") "runtime.json contains secret-like text"
  $logText = @(
    Get-ChildItem -LiteralPath $runtimeRoot -Filter "*.log" -File |
      ForEach-Object { Get-Content -Raw -LiteralPath $_.FullName -ErrorAction SilentlyContinue }
  ) -join "`n"
  Assert-Condition ($logText -notmatch [regex]::Escape($password)) "launcher logs contain the demo password"

  $secondOutput = powershell.exe -NoProfile -ExecutionPolicy Bypass -File $startScript -NoBrowser -TimeoutSeconds 10 -RuntimeDirectory $runtimeRoot 2>&1 | Out-String
  $secondExit = $LASTEXITCODE
  Assert-Condition ($secondExit -eq 0) "second start was not idempotent (exit=$secondExit; output=$secondOutput)"
  Assert-Condition ($secondOutput -match "already running") "second start did not report already-running state"

  $unknownCommand = ""
  $unknown = @(Get-CimInstance Win32_Process -Filter "ProcessId = $PID" -ErrorAction SilentlyContinue)
  if ($unknown.Count -gt 0) { $unknownCommand = [string]$unknown[0].CommandLine }
  Assert-Condition ((-not $unknownCommand.Contains("app.main:app")) -and (-not $unknownCommand.Contains("--port 5173"))) "unknown process ownership check is unsafe"

  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $stopScript -RuntimeDirectory $runtimeRoot
  Assert-Condition ($LASTEXITCODE -eq 0) "stop_demo.ps1 failed"
  Assert-Condition (-not (Test-Path -LiteralPath $runtimePath)) "runtime.json remained after safe stop"
  Assert-Condition ((@(Get-PortOwners -Port 8000)).Count -eq 0) "port 8000 remained occupied"
  Assert-Condition ((@(Get-PortOwners -Port 5173)).Count -eq 0) "port 5173 remained occupied"
  Stop-LauncherHost
  Write-Host "Launcher smoke passed."
}
finally {
  try {
    if (Test-Path -LiteralPath $runtimePath) {
      & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $stopScript -RuntimeDirectory $runtimeRoot *> $null
    }
  }
  finally {
    Stop-LauncherHost
    if (Test-Path -LiteralPath $runtimeRoot) {
      Remove-Item -LiteralPath $runtimeRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
}
