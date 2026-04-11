param(
    [string]$SecretsConfigPath
)

$ErrorActionPreference = "Stop"

if (-not $SecretsConfigPath) {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\run_top9main_live.ps1 D:\work\secure\secret_bin.json"
    exit 1
}

$startScript = Join-Path $PSScriptRoot "start_top9main_live.ps1"
if (-not (Test-Path -LiteralPath $startScript -PathType Leaf)) {
    throw "Start script not found: $startScript"
}

& $startScript -SecretsConfigPath $SecretsConfigPath

$baseUrl = "http://127.0.0.1:8084"
$username = "Freqtrader"
$password = "Top9MainLive!2026"
$credentialText = "{0}:{1}" -f $username, $password
$token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($credentialText))
$headers = @{ Authorization = "Basic $token" }

function Invoke-RestWithRetry {
    param(
        [string]$Method,
        [string]$Uri,
        [int]$RetryCount = 30,
        [int]$DelaySeconds = 2
    )

    for ($i = 0; $i -lt $RetryCount; $i++) {
        try {
            return Invoke-RestMethod -Method $Method -Headers $headers -Uri $Uri
        }
        catch {
            if ($i -eq ($RetryCount - 1)) {
                throw
            }
            Start-Sleep -Seconds $DelaySeconds
        }
    }
}

Write-Host "Waiting for bot API..." -ForegroundColor Cyan
for ($i = 0; $i -lt 30; $i++) {
    try {
        Invoke-RestMethod -Uri "$baseUrl/api/v1/ping" | Out-Null
        break
    }
    catch {
        if ($i -eq 29) {
            throw "API did not become ready in time."
        }
        Start-Sleep -Seconds 2
    }
}

Invoke-RestWithRetry -Method Post -Uri "$baseUrl/api/v1/start" | Out-Null

Write-Host ""
Write-Host "Top9 main live bot started." -ForegroundColor Cyan
Write-Host "Use .\show_top9main_live_status.ps1 to inspect trades."
Write-Host "Use .\check_top9main_min_stakes.ps1 to check minimum order requirements."
