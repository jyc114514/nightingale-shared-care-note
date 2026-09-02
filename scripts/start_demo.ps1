[CmdletBinding()]
param(
  [AllowEmptyString()]
  [string]$DemoPassword = "",
  [ValidateSet("en", "zh-CN")]
  [string]$Language = "en",
  [switch]$NoBrowser,
  [switch]$Setup,
  [int]$TimeoutSeconds = 45,
  [string]$RuntimeDirectory = "",
  [ValidateSet("auto", "fixture")]
  [string]$ProviderOverride = "auto"
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "demo_common.ps1")

$projectRoot = Get-DemoRoot
$backendRoot = Join-Path $projectRoot "backend"
$frontendRoot = Join-Path $projectRoot "frontend"
$runtimeRoot = Get-DemoRuntimeDirectory -RuntimeDirectory $RuntimeDirectory
$runtimePath = Join-Path $runtimeRoot "runtime.json"
$backendLog = Join-Path $runtimeRoot "backend.log"
$backendErrorLog = Join-Path $runtimeRoot "backend.error.log"
$frontendLog = Join-Path $runtimeRoot "frontend.log"
$frontendErrorLog = Join-Path $runtimeRoot "frontend.error.log"
$databasePath = Join-Path $runtimeRoot "nightingale-demo.sqlite"
$databaseUrl = Get-DemoDatabaseUrl -DatabasePath $databasePath
$browserUrl = "http://127.0.0.1:5173/?lang=$Language"
$backendProcess = $null
$frontendProcess = $null
$startedHere = @()
$localProviderConfig = $null
$deepseekKey = $null
$envNames = @(
  "APP_ENV",
  "DATABASE_URL",
  "SESSION_SECRET",
  "COOKIE_SECURE",
  "ALLOWED_ORIGINS",
  "DEMO_SEED_PASSWORD",
  "DEMO_SEED_ENABLED",
  "VITE_API_BASE_URL",
  "LLM_PROVIDER",
  "DEEPSEEK_API_KEY",
  "DEEPSEEK_BASE_URL",
  "DEEPSEEK_MODEL",
  "DEEPSEEK_TIMEOUT_SECONDS",
  "DEEPSEEK_MAX_TOKENS",
  "VOICE_PROVIDER",
  "VOICE_MODEL",
  "VOICE_DEVICE",
  "VOICE_COMPUTE_TYPE",
  "VOICE_MODEL_CACHE_DIR"
)
$oldEnvironment = @{}

function Restore-DemoEnvironment {
  foreach ($name in $envNames) {
    if ($oldEnvironment.ContainsKey($name) -and $null -ne $oldEnvironment[$name]) {
      Set-Item -Path ("Env:" + $name) -Value $oldEnvironment[$name]
    }
    else {
      Remove-Item -Path ("Env:" + $name) -ErrorAction SilentlyContinue
    }
  }
}

function Stop-StartedChildren {
  foreach ($child in @($startedHere)) {
    if ($child.ProcessId -and (Test-DemoOwnedProcess -ProcessId $child.ProcessId -ProjectRoot $projectRoot -Kind $child.Kind)) {
      Stop-DemoProcessTree -ProcessId $child.ProcessId
    }
  }
}

function Fail-DemoStart {
  param([string]$Message)

  Write-Host ""
  Write-Host "Nightingale demo could not start." -ForegroundColor Red
  Write-Host $Message -ForegroundColor Yellow
  if ($startedHere.Count -gt 0) {
    Stop-StartedChildren
  }
  if (Test-Path -LiteralPath $runtimePath -PathType Leaf) {
    Remove-Item -LiteralPath $runtimePath -Force -ErrorAction SilentlyContinue
  }
  Write-Host "Check logs: $runtimeRoot"
  if (Test-Path -LiteralPath $backendErrorLog -PathType Leaf) {
    Write-Host "--- backend error tail ---"
    Get-DemoLogTail -Path $backendErrorLog | ForEach-Object { Write-Host $_ }
  }
  if (Test-Path -LiteralPath $frontendErrorLog -PathType Leaf) {
    Write-Host "--- frontend error tail ---"
    Get-DemoLogTail -Path $frontendErrorLog | ForEach-Object { Write-Host $_ }
  }
  Restore-DemoEnvironment
  exit 1
}

try {
  New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null

  $pythonExecutable = Resolve-DemoPython -ProjectRoot $projectRoot
  $pnpmExecutable = Resolve-DemoPnpm -ProjectRoot $projectRoot
  $nodeExecutable = Resolve-DemoNode
  $localProviderConfig = Get-DemoLocalConfig
  if ($ProviderOverride -eq "fixture") {
    $localProviderConfig = [pscustomobject]@{
      Provider = "fixture"
      KeyFilePath = ""
      Model = "deepseek-v4-flash"
    }
  }

  if (Test-Path -LiteralPath $runtimePath -PathType Leaf) {
    try {
      $existingRuntime = Get-Content -Raw -LiteralPath $runtimePath | ConvertFrom-Json
      $backendOwned = Test-DemoOwnedProcess -ProcessId ([int]$existingRuntime.backend_pid) -ProjectRoot $projectRoot -Kind backend
      $frontendOwned = Test-DemoOwnedProcess -ProcessId ([int]$existingRuntime.frontend_pid) -ProjectRoot $projectRoot -Kind frontend
      if ($backendOwned -and $frontendOwned) {
        $backendReady = Wait-DemoHttp -Url "http://127.0.0.1:8000/health" -TimeoutSeconds 5
        $frontendReady = Wait-DemoHttp -Url "http://127.0.0.1:5173/" -TimeoutSeconds 5
        if ($backendReady -and $frontendReady) {
          Write-Host "Nightingale is already running."
          Write-Host "Browser: $browserUrl"
          if (-not $NoBrowser) {
            Start-Process -FilePath $browserUrl | Out-Null
          }
          Restore-DemoEnvironment
          exit 0
        }
      }
    }
    catch {
      # A stale or malformed runtime file is safe to replace only after its recorded PIDs fail ownership checks.
    }
    Remove-Item -LiteralPath $runtimePath -Force -ErrorAction SilentlyContinue
  }

  foreach ($port in @(8000, 5173)) {
    $owners = @(Get-DemoPortOwner -Port $port)
    $responding = $false
    if ($port -eq 8000) {
      $responding = Test-DemoHttp -Url "http://127.0.0.1:8000/health"
    }
    else {
      $responding = Test-DemoHttp -Url "http://127.0.0.1:5173/"
    }
    if ($owners.Count -gt 0 -or $responding) {
      Fail-DemoStart "Port $port is already owned by PID(s) $($owners -join ', '). The launcher will not kill unknown processes."
    }
  }

  foreach ($log in @($backendLog, $backendErrorLog, $frontendLog, $frontendErrorLog)) {
    Set-Content -LiteralPath $log -Value "" -Encoding UTF8
  }

  foreach ($name in $envNames) {
    $existingEnvironment = Get-Item -Path ("Env:" + $name) -ErrorAction SilentlyContinue
    if ($existingEnvironment) {
      $oldEnvironment[$name] = $existingEnvironment.Value
    }
    else {
      $oldEnvironment[$name] = $null
    }
  }
  $env:APP_ENV = "development"
  $env:DATABASE_URL = $databaseUrl
  $env:SESSION_SECRET = Get-DemoSessionSecret
  $env:COOKIE_SECURE = "false"
  $env:ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
  $env:DEMO_SEED_ENABLED = "false"
  $env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
  $env:LLM_PROVIDER = $localProviderConfig.Provider
  $env:DEEPSEEK_BASE_URL = "https://api.deepseek.com"
  $env:DEEPSEEK_MODEL = $localProviderConfig.Model
  $env:DEEPSEEK_TIMEOUT_SECONDS = "20"
  $env:DEEPSEEK_MAX_TOKENS = "600"
  $env:VOICE_PROVIDER = "fixture"
  $env:VOICE_MODEL = "turbo"
  $env:VOICE_DEVICE = "cuda"
  $env:VOICE_COMPUTE_TYPE = "float16"
  $env:VOICE_MODEL_CACHE_DIR = Join-Path $runtimeRoot "voice-model-cache"
  Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
  if ($localProviderConfig.Provider -eq "deepseek") {
    $deepseekKey = Read-DemoDeepSeekKey -KeyFilePath $localProviderConfig.KeyFilePath
    $env:DEEPSEEK_API_KEY = $deepseekKey
  }

  $pipCheckOutput = & $pythonExecutable -m pip check 2>&1
  if ($LASTEXITCODE -ne 0) {
    if (-not $Setup) {
      Fail-DemoStart "Backend dependencies are incomplete. Rerun with -Setup to install backend\requirements.lock."
    }
    $uvExecutable = Resolve-DemoUv
    if (-not $uvExecutable) {
      Fail-DemoStart "pip check failed and uv was not found for lockfile installation."
    }
    & $uvExecutable pip install --python $pythonExecutable --requirement (Join-Path $backendRoot "requirements.lock")
    if ($LASTEXITCODE -ne 0) {
      Fail-DemoStart "Backend lockfile installation failed."
    }
  }

  if (-not (Test-Path -LiteralPath (Join-Path $frontendRoot "node_modules") -PathType Container)) {
    & $pnpmExecutable install --frozen-lockfile --dir $frontendRoot
    if ($LASTEXITCODE -ne 0) {
      Fail-DemoStart "Frontend frozen install failed."
    }
  }
  elseif ($Setup) {
    & $pnpmExecutable install --frozen-lockfile --dir $frontendRoot
    if ($LASTEXITCODE -ne 0) {
      Fail-DemoStart "Frontend setup failed."
    }
  }

  Push-Location $backendRoot
  try {
    & $pythonExecutable -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
      Fail-DemoStart "Alembic migration failed."
    }
  }
  finally {
    Pop-Location
  }

  $seeded = Test-DemoSeeded -PythonExecutable $pythonExecutable -DatabasePath $databasePath
  if (-not $seeded) {
    if ([string]::IsNullOrWhiteSpace($DemoPassword)) {
      $securePassword = Read-Host "Enter a local synthetic demo password" -AsSecureString
      $DemoPassword = ConvertTo-DemoPlainPassword -SecurePassword $securePassword
    }
    if ([string]::IsNullOrWhiteSpace($DemoPassword)) {
      Fail-DemoStart "A local synthetic demo password is required for first-run seed."
    }
    $env:DEMO_SEED_PASSWORD = $DemoPassword
    Push-Location $backendRoot
    try {
      & $pythonExecutable -m app.scripts.seed_demo
      if ($LASTEXITCODE -ne 0) {
        Fail-DemoStart "Synthetic seed failed."
      }
    }
    finally {
      Pop-Location
      Remove-Item Env:DEMO_SEED_PASSWORD -ErrorAction SilentlyContinue
      $DemoPassword = ""
    }
  }

  $backendProcess = Start-Process -FilePath $pythonExecutable -ArgumentList @(
    "-m", "uvicorn", "app.main:app", "--app-dir", ('"{0}"' -f $backendRoot), "--host", "127.0.0.1", "--port", "8000"
  ) -WorkingDirectory $backendRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $backendLog -RedirectStandardError $backendErrorLog
  $startedHere += [pscustomobject]@{ ProcessId = $backendProcess.Id; Kind = "backend" }
  Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
  $deepseekKey = $null

  $viteExecutable = Join-Path $frontendRoot "node_modules\vite\bin\vite.js"
  $frontendProcess = Start-Process -FilePath $nodeExecutable -ArgumentList @(
    ('"{0}"' -f $viteExecutable), "--host", "127.0.0.1", "--port", "5173"
  ) -WorkingDirectory $frontendRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendErrorLog
  $startedHere += [pscustomobject]@{ ProcessId = $frontendProcess.Id; Kind = "frontend" }

  $runtime = [ordered]@{
    schema_version = 1
    project_root = $projectRoot
    backend_pid = $backendProcess.Id
    frontend_pid = $frontendProcess.Id
    backend_port = 8000
    frontend_port = 5173
    database_path = $databasePath
    llm_provider = $localProviderConfig.Provider
    llm_model = $localProviderConfig.Model
    voice_provider = $env:VOICE_PROVIDER
    voice_model = $env:VOICE_MODEL
    browser_url = $browserUrl
    started_at = [DateTime]::UtcNow.ToString("o")
    backend_log = $backendLog
    frontend_log = $frontendLog
  }
  $runtime | ConvertTo-Json | Set-Content -LiteralPath $runtimePath -Encoding UTF8

  if (-not (Wait-DemoHttp -Url "http://127.0.0.1:8000/health" -TimeoutSeconds $TimeoutSeconds)) {
    Fail-DemoStart "Backend health check timed out."
  }
  if (-not (Wait-DemoHttp -Url "http://127.0.0.1:5173/" -TimeoutSeconds $TimeoutSeconds)) {
    Fail-DemoStart "Frontend health check timed out."
  }

  Restore-DemoEnvironment
  Write-Host ""
  Write-Host "Nightingale demo is running." -ForegroundColor Green
  Write-Host "Backend running: http://127.0.0.1:8000/health"
  Write-Host "Frontend running: http://127.0.0.1:5173/"
  Write-Host "Browser: $browserUrl"
  Write-Host "Demo users: staff.a@clinic-a.test, clinician.a@clinic-a.test, sarah.patient@clinic-a.test"
  Write-Host "Use the first-run local password; the launcher never displays it."
  Write-Host "Stop: Stop Nightingale Demo.cmd"
  Write-Host "Logs: $runtimeRoot"
  Write-Host "Synthetic data only."
  if (-not $NoBrowser) {
    Start-Process -FilePath $browserUrl | Out-Null
  }
}
catch {
  Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
  Fail-DemoStart $_.Exception.Message
}
finally {
  Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
  $deepseekKey = $null
  if ($DemoPassword) {
    $DemoPassword = ""
  }
}
