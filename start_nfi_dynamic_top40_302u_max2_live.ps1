[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$templateConfigPath = Join-Path $repoRoot "user_data\config.live.nfi.dynamic.top40.302u.max2.json"
$runtimeConfigPath = Join-Path $repoRoot "user_data\config.live.nfi.dynamic.top40.302u.max2.runtime.json"
$dynamicBacktestConfigPath = Join-Path $repoRoot "user_data\tests\nfi_top_volume_3y_1000u\config.backtest.nfi.1y.302u.top40.dynamic.max2.json"
$updateScriptPath = Join-Path $repoRoot "update_nfi_dynamic_top40_302u.ps1"
$secureConfigPath = "D:\work\secure\secret_bin.json"
$containerService = "freqtrade"
$baseUrl = "http://127.0.0.1:8084"
$liveDbPath = "/freqtrade/user_data/tradesv3_nfi_dynamic_top40_302u_max2_live.sqlite"

if (-not (Test-Path -LiteralPath $templateConfigPath -PathType Leaf)) {
    throw "Template config not found: $templateConfigPath"
}

if (-not (Test-Path -LiteralPath $dynamicBacktestConfigPath -PathType Leaf)) {
    throw "Dynamic backtest config not found: $dynamicBacktestConfigPath"
}

if (-not (Test-Path -LiteralPath $updateScriptPath -PathType Leaf)) {
    throw "Update script not found: $updateScriptPath"
}

if (-not (Test-Path -LiteralPath $secureConfigPath -PathType Leaf)) {
    throw "Secure API config not found: $secureConfigPath"
}

Write-Host "Refreshing dynamic top40 pairlist..." -ForegroundColor Cyan
& powershell -ExecutionPolicy Bypass -File $updateScriptPath

$dynamicConfig = Get-Content -Raw -LiteralPath $dynamicBacktestConfigPath | ConvertFrom-Json
$templateConfig = Get-Content -Raw -LiteralPath $templateConfigPath | ConvertFrom-Json
$sourceConfig = Get-Content -Raw -LiteralPath $secureConfigPath | ConvertFrom-Json

$apiKey = $sourceConfig.exchange.key
$apiSecret = $sourceConfig.exchange.secret

if ([string]::IsNullOrWhiteSpace($apiKey) -or [string]::IsNullOrWhiteSpace($apiSecret)) {
    throw "Secure API config does not contain exchange key/secret."
}

$templateConfig.exchange.key = $apiKey
$templateConfig.exchange.secret = $apiSecret
$templateConfig.exchange.pair_whitelist = @($dynamicConfig.exchange.pair_whitelist)

$apiUser = $templateConfig.api_server.username
$apiPassword = $templateConfig.api_server.password

[System.IO.File]::WriteAllText(
    $runtimeConfigPath,
    ($templateConfig | ConvertTo-Json -Depth 32),
    [System.Text.UTF8Encoding]::new($false)
)

$composeEnv = @{
    FREQTRADE_COMMAND = "trade"
    FREQTRADE_CONFIG = (Split-Path -Leaf $runtimeConfigPath)
    FREQTRADE_DB_URL = "sqlite:///$liveDbPath"
    FREQTRADE_STRATEGY = "NostalgiaForInfinityX7"
}

Push-Location $repoRoot
try {
    foreach ($entry in $composeEnv.GetEnumerator()) {
        Set-Item -Path ("Env:{0}" -f $entry.Key) -Value $entry.Value
    }

    Write-Host "Starting container..." -ForegroundColor Cyan
    docker compose up -d --force-recreate --remove-orphans $containerService | Out-Host

    $authText = "{0}:{1}" -f $apiUser, $apiPassword
    $authToken = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($authText))
    $headers = @{ Authorization = "Basic $authToken" }

    Write-Host "Waiting for bot API..." -ForegroundColor Cyan
    for ($i = 0; $i -lt 45; $i++) {
        try {
            Invoke-RestMethod -Uri "$baseUrl/api/v1/ping" | Out-Null
            break
        }
        catch {
            if ($i -eq 44) {
                throw "API did not become ready in time."
            }
            Start-Sleep -Seconds 2
        }
    }

    Invoke-RestMethod -Method Post -Headers $headers -Uri "$baseUrl/api/v1/start" | Out-Null
    $status = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/api/v1/status"
    $showConfig = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/api/v1/show_config"

    Write-Host ""
    Write-Host "NFI Dynamic Top40 302U live bot started." -ForegroundColor Green
    Write-Host ("Runtime config: {0}" -f $runtimeConfigPath)
    Write-Host ("Strategy      : {0}" -f $showConfig.strategy)
    Write-Host ("Runmode       : {0}" -f $showConfig.runmode)
    Write-Host ("State         : {0}" -f $showConfig.state)
    Write-Host ("Pairs loaded  : {0}" -f @($showConfig.exchange.pair_whitelist).Count)
    Write-Host ("Open trades   : {0}" -f @($status).Count)
}
finally {
    Pop-Location
}
