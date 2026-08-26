Set-StrictMode -Version Latest

$script:DemoRoot = Split-Path -Parent $PSScriptRoot

function Get-DemoRoot {
  return $script:DemoRoot
}

function Get-DemoLocalConfigPath {
  return Join-Path $script:DemoRoot ".nightingale-local.json"
}

function Get-DemoLocalConfig {
  $configPath = Get-DemoLocalConfigPath
  if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    return [pscustomobject]@{
      Provider = "fixture"
      KeyFilePath = ""
      Model = "deepseek-v4-flash"
    }
  }
  try {
    $config = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
  }
  catch {
    throw "The local Nightingale provider configuration is invalid."
  }
  if ($null -eq $config) {
    throw "The local Nightingale provider configuration is invalid."
  }
  $allowedProperties = @("llm_provider", "deepseek_key_file", "deepseek_model")
  $unknownProperties = @($config.PSObject.Properties.Name | Where-Object { $_ -notin $allowedProperties })
  if ($unknownProperties.Count -gt 0) {
    throw "The local Nightingale provider configuration contains unsupported settings."
  }
  $provider = ([string]$config.llm_provider).Trim().ToLowerInvariant()
  if ([string]::IsNullOrWhiteSpace($provider)) {
    $provider = "fixture"
  }
  if ($provider -eq "fixture") {
    return [pscustomobject]@{
      Provider = "fixture"
      KeyFilePath = ""
      Model = "deepseek-v4-flash"
    }
  }
  if ($provider -ne "deepseek") {
    throw "The local Nightingale provider must be fixture or deepseek."
  }
  $keyFilePath = ([string]$config.deepseek_key_file).Trim()
  if ([string]::IsNullOrWhiteSpace($keyFilePath)) {
    throw "DeepSeek is selected but no local key file is configured."
  }
  $model = ([string]$config.deepseek_model).Trim()
  if ([string]::IsNullOrWhiteSpace($model)) {
    $model = "deepseek-v4-flash"
  }
  if ($model -ne "deepseek-v4-flash") {
    throw "The local Nightingale DeepSeek model must be deepseek-v4-flash."
  }
  return [pscustomobject]@{
    Provider = "deepseek"
    KeyFilePath = $keyFilePath
    Model = $model
  }
}

function Read-DemoDeepSeekKey {
  param([string]$KeyFilePath)

  if ([string]::IsNullOrWhiteSpace($KeyFilePath) -or -not (Test-Path -LiteralPath $KeyFilePath -PathType Leaf)) {
    throw "The configured DeepSeek key file is unavailable."
  }
  try {
    $key = [IO.File]::ReadAllText($KeyFilePath)
  }
  catch {
    throw "The configured DeepSeek key file cannot be read."
  }
  if ([string]::IsNullOrWhiteSpace($key)) {
    throw "The configured DeepSeek key file is empty."
  }
  return $key.Trim()
}

function Get-DemoRuntimeDirectory {
  param([string]$RuntimeDirectory)

  if ([string]::IsNullOrWhiteSpace($RuntimeDirectory)) {
    return Join-Path $script:DemoRoot "artifacts\local-runtime"
  }
  return [IO.Path]::GetFullPath($RuntimeDirectory)
}

function Resolve-DemoPython {
  param([string]$ProjectRoot)

  $candidates = @(
    "C:\Users\JI YANCHEN\Desktop\ai_trading_playground\ai_env\python.exe",
    (Join-Path $ProjectRoot ".venv\Scripts\python.exe")
  )
  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
      return $candidate
    }
  }
  $command = Get-Command python.exe -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }
  throw "Python was not found. Install Python or configure the existing ai_env path, then rerun the launcher."
}

function Resolve-DemoPnpm {
  param([string]$ProjectRoot)

  $candidates = @(
    "C:\Users\JI YANCHEN\AppData\Roaming\npm\pnpm.cmd",
    (Join-Path $ProjectRoot "node_modules\.bin\pnpm.cmd")
  )
  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
      return $candidate
    }
  }
  $command = Get-Command pnpm.cmd -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }
  throw "pnpm was not found. Install pnpm or add pnpm.cmd to PATH, then rerun the launcher."
}

function Resolve-DemoNode {
  $command = Get-Command node.exe -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }
  $candidate = "C:\Program Files\nodejs\node.exe"
  if (Test-Path -LiteralPath $candidate -PathType Leaf) {
    return $candidate
  }
  throw "Node.js was not found. Install Node.js, then rerun the launcher."
}

function Resolve-DemoUv {
  $candidate = "C:\Users\JI YANCHEN\.local\bin\uv.exe"
  if (Test-Path -LiteralPath $candidate -PathType Leaf) {
    return $candidate
  }
  $command = Get-Command uv.exe -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }
  return $null
}

function Get-DemoDatabaseUrl {
  param([string]$DatabasePath)

  $normalized = ([IO.Path]::GetFullPath($DatabasePath)).Replace("\", "/")
  return "sqlite:///$normalized"
}

function Get-DemoSessionSecret {
  $bytes = New-Object byte[] 32
  $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
  try {
    $generator.GetBytes($bytes)
    return [Convert]::ToBase64String($bytes)
  }
  finally {
    $generator.Dispose()
  }
}

function Test-DemoSeeded {
  param(
    [string]$PythonExecutable,
    [string]$DatabasePath
  )

  if (-not (Test-Path -LiteralPath $DatabasePath -PathType Leaf)) {
    return $false
  }
  $code = @"
import sqlite3, sys
path = sys.argv[1]
try:
    with sqlite3.connect(path) as connection:
        users = connection.execute('select count(*) from users').fetchone()[0]
        patients = connection.execute('select count(*) from patients').fetchone()[0]
    raise SystemExit(0 if users >= 5 and patients >= 2 else 1)
except (sqlite3.Error, OSError):
    raise SystemExit(1)
"@
  & $PythonExecutable -c $code $DatabasePath *> $null
  return ($LASTEXITCODE -eq 0)
}

function Get-DemoProcess {
  param([int]$ProcessId)

  if ($ProcessId -le 0) {
    return $null
  }
  $cimProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
  if ($cimProcess) {
    return $cimProcess
  }
  try {
    $nativeProcess = Get-Process -Id $ProcessId -ErrorAction Stop
    return [pscustomobject]@{
      ProcessId = $nativeProcess.Id
      CommandLine = ""
      ExecutablePath = $nativeProcess.Path
    }
  }
  catch {
    return $null
  }
}

function Test-DemoOwnedProcess {
  param(
    [int]$ProcessId,
    [string]$ProjectRoot,
    [ValidateSet("backend", "frontend")]
    [string]$Kind
  )

  $process = Get-DemoProcess -ProcessId $ProcessId
  if (-not $process) {
    return $false
  }
  $commandLine = ([string]$process.CommandLine).ToLowerInvariant().Replace("/", "\")
  $normalizedRoot = ([IO.Path]::GetFullPath($ProjectRoot)).TrimEnd("\").ToLowerInvariant()
  $port = 5173
  if ($Kind -eq "backend") {
    $port = 8000
    if ($commandLine.Contains($normalizedRoot)) {
      return $commandLine.Contains("uvicorn") -and $commandLine.Contains("app.main:app") -and $commandLine.Contains("--port 8000")
    }
    $expectedExecutable = Resolve-DemoPython -ProjectRoot $ProjectRoot
  }
  else {
    if ($commandLine.Contains($normalizedRoot)) {
      return ($commandLine.Contains("vite") -or $commandLine.Contains("pnpm")) -and $commandLine.Contains("--port 5173")
    }
    $expectedExecutable = Resolve-DemoNode
  }
  $actualExecutable = ([string]$process.ExecutablePath).ToLowerInvariant().Replace("/", "\")
  $normalizedExecutable = ([IO.Path]::GetFullPath($expectedExecutable)).ToLowerInvariant().Replace("/", "\")
  if ([string]::IsNullOrWhiteSpace($actualExecutable) -or $actualExecutable -ne $normalizedExecutable) {
    return $false
  }
  if ($port -eq 8000) {
    return Test-DemoHttp -Url "http://127.0.0.1:8000/health"
  }
  return Test-DemoHttp -Url "http://127.0.0.1:5173/"
}

function Get-DemoPortOwner {
  param([int]$Port)

  return @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
}

function Wait-DemoHttp {
  param(
    [string]$Url,
    [int]$TimeoutSeconds
  )

  $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
  while ([DateTime]::UtcNow -lt $deadline) {
    try {
      $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
      if ($response.StatusCode -eq 200) {
        return $true
      }
    }
    catch {
      # The child process may still be starting.
    }
    Start-Sleep -Milliseconds 250
  }
  return $false
}

function Test-DemoHttp {
  param([string]$Url)

  try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
    return ($response.StatusCode -eq 200)
  }
  catch {
    return $false
  }
}

function Stop-DemoProcessTree {
  param([int]$ProcessId)

  if ($ProcessId -le 0) {
    return
  }
  & taskkill.exe /PID $ProcessId /T /F *> $null
}

function Get-DemoLogTail {
  param([string]$Path)

  if (Test-Path -LiteralPath $Path -PathType Leaf) {
    return @(Get-Content -LiteralPath $Path -Tail 30 -ErrorAction SilentlyContinue)
  }
  return @("No log file was created: $Path")
}

function ConvertTo-DemoPlainPassword {
  param([Security.SecureString]$SecurePassword)

  $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword)
  try {
    return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
  }
  finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
  }
}
