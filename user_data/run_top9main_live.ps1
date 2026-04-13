param(
    [string]$SecretsConfigPath
)

$ErrorActionPreference = "Stop"

if (-not $SecretsConfigPath) {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\run_top9main_live.ps1 D:\work\secure\secret_bin.json"
    exit 1
}

$startScript = Join-Path (Split-Path -Parent $PSScriptRoot) "start_top9main_live.ps1"
if (-not (Test-Path -LiteralPath $startScript -PathType Leaf)) {
    throw "Start script not found: $startScript"
}

& $startScript -SecretsConfigPath $SecretsConfigPath
