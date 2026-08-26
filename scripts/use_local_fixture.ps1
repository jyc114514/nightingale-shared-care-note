[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "demo_common.ps1")

[ordered]@{ llm_provider = "fixture" } |
  ConvertTo-Json |
  Set-Content -LiteralPath (Get-DemoLocalConfigPath) -Encoding UTF8
Write-Host "Local deterministic fixture selected."
Write-Host "The external DeepSeek key file, if any, was not changed."
