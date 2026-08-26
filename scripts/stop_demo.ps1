[CmdletBinding()]
param([string]$RuntimeDirectory = "")

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "demo_common.ps1")

$projectRoot = Get-DemoRoot
$runtimeRoot = Get-DemoRuntimeDirectory -RuntimeDirectory $RuntimeDirectory
$runtimePath = Join-Path $runtimeRoot "runtime.json"

if (-not (Test-Path -LiteralPath $runtimePath -PathType Leaf)) {
  Write-Host "Nightingale demo is not running."
  exit 0
}

try {
  $runtime = Get-Content -Raw -LiteralPath $runtimePath | ConvertFrom-Json
}
catch {
  Write-Host "runtime.json is invalid; no process was stopped." -ForegroundColor Red
  exit 1
}

$failed = $false
foreach ($item in @(
  [pscustomobject]@{ Name = "backend"; Pid = [int]$runtime.backend_pid },
  [pscustomobject]@{ Name = "frontend"; Pid = [int]$runtime.frontend_pid }
)) {
  $process = Get-DemoProcess -ProcessId $item.Pid
  if (-not $process) {
    Write-Host "$($item.Name) PID $($item.Pid) is already stopped."
    continue
  }
  if (-not (Test-DemoOwnedProcess -ProcessId $item.Pid -ProjectRoot $projectRoot -Kind $item.Name)) {
    Write-Host "PID $($item.Pid) does not match this repository's $($item.Name) command; it was not stopped." -ForegroundColor Red
    $failed = $true
    continue
  }
  Stop-DemoProcessTree -ProcessId $item.Pid
  Write-Host "Stopped $($item.Name) PID $($item.Pid)."
}

if ($failed) {
  Write-Host "Runtime metadata was kept for manual inspection." -ForegroundColor Yellow
  exit 1
}

Start-Sleep -Milliseconds 500
$remaining = @((Get-DemoPortOwner -Port 8000) + (Get-DemoPortOwner -Port 5173) | Select-Object -Unique)
if ($remaining.Count -gt 0) {
  Write-Host "An unknown process still owns port(s); it was not killed." -ForegroundColor Yellow
}
Remove-Item -LiteralPath $runtimePath -Force
Write-Host "Nightingale demo stopped safely."
