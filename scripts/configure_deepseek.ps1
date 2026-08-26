[CmdletBinding()]
param([string]$KeyFilePath = "")

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "demo_common.ps1")

$configPath = Get-DemoLocalConfigPath
if ([string]::IsNullOrWhiteSpace($KeyFilePath)) {
  $KeyFilePath = Read-Host "Path to the external DeepSeek API key file"
}

try {
  if ([string]::IsNullOrWhiteSpace($KeyFilePath) -or -not (Test-Path -LiteralPath $KeyFilePath -PathType Leaf)) {
    throw "The selected key file does not exist or is not a file."
  }
  $resolvedPath = (Resolve-Path -LiteralPath $KeyFilePath -ErrorAction Stop).Path
  $key = [IO.File]::ReadAllText($resolvedPath)
  if ([string]::IsNullOrWhiteSpace($key)) {
    throw "The selected key file is empty."
  }
  $key = $null
  [ordered]@{
    llm_provider = "deepseek"
    deepseek_key_file = $resolvedPath
    deepseek_model = "deepseek-v4-flash"
  } | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding UTF8
  Write-Host "DeepSeek key file configured."
  Write-Host "The key remains outside the repository and is never printed or copied."
}
catch {
  Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
  throw $_.Exception.Message
}
finally {
  $key = $null
}
