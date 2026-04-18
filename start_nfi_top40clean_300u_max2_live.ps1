[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$templateConfigPath = Join-Path $repoRoot "user_data\config.live.nfi.top40clean.300u.max2.json"
$runtimeConfigPath = Join-Path $repoRoot "user_data\config.live.nfi.top40clean.300u.max2.runtime.json"
$sourceRuntimePath = Join-Path $repoRoot "user_data\config.live.futures.top9.testlive.runtime.json"
$containerService = "freqtrade"
$baseUrl = "http://127.0.0.1:8084"
$apiUser = "Freqtrader"
$apiPassword = "NfiTop40Live!2026"
$liveDbPath = "/freqtrade/user_data/tradesv3_nfi_top40clean_300u_max2_live.sqlite"

if (-not (Test-Path -LiteralPath $templateConfigPath -PathType Leaf)) {
    throw "Template config not found: $templateConfigPath"
}

if (-not (Test-Path -LiteralPath $sourceRuntimePath -PathType Leaf)) {
    throw "Source runtime config not found: $sourceRuntimePath"
}

$sourceConfig = Get-Content -Raw -LiteralPath $sourceRuntimePath | ConvertFrom-Json
$apiKey = $sourceConfig.exchange.key
$apiSecret = $sourceConfig.exchange.secret

if ([string]::IsNullOrWhiteSpace($apiKey) -or [string]::IsNullOrWhiteSpace($apiSecret)) {
    throw "Source runtime config does not contain exchange key/secret."
}

$config = Get-Content -Raw -LiteralPath $templateConfigPath | ConvertFrom-Json
$config.exchange.key = $apiKey
$config.exchange.secret = $apiSecret

$configJson = $config | ConvertTo-Json -Depth 32
[System.IO.File]::WriteAllText(
    $runtimeConfigPath,
    $configJson,
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
    Write-Host "NFI Top40 clean live bot started." -ForegroundColor Green
    Write-Host ("Runtime config: {0}" -f $runtimeConfigPath)
    Write-Host ("Strategy      : {0}" -f $showConfig.strategy)
    Write-Host ("Runmode       : {0}" -f $showConfig.runmode)
    Write-Host ("State         : {0}" -f $showConfig.state)
    Write-Host ("Open trades   : {0}" -f @($status).Count)
}
finally {
    Pop-Location
}
