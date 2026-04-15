param(
    [Parameter(Mandatory = $true)]
    [string]$SecretsConfigPath
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$templateConfigPath = Join-Path $repoRoot "user_data\config.live.futures.top9.testlive.json"
$runtimeConfigPath = Join-Path $repoRoot "user_data\config.live.futures.top9.testlive.runtime.json"
$containerService = "freqtrade"
$baseUrl = "http://127.0.0.1:8084"
$apiUser = "Freqtrader"
$apiPassword = "Top9TestLive!2026"
$liveDbPath = "/freqtrade/user_data/tradesv3-top9-main-test-live.sqlite"

function Get-SecretValue {
    param(
        [Parameter(Mandatory = $true)]
        $Object,
        [Parameter(Mandatory = $true)]
        [string[]]$Names
    )

    foreach ($name in $Names) {
        $prop = $Object.PSObject.Properties[$name]
        if ($prop -and $null -ne $prop.Value -and "$($prop.Value)".Trim() -ne "") {
            return $prop.Value
        }
    }

    return $null
}

if (-not (Test-Path -LiteralPath $SecretsConfigPath -PathType Leaf)) {
    throw "Secrets file not found: $SecretsConfigPath"
}

if (-not (Test-Path -LiteralPath $templateConfigPath -PathType Leaf)) {
    throw "Template config not found: $templateConfigPath"
}

$secrets = Get-Content -Raw -LiteralPath $SecretsConfigPath | ConvertFrom-Json
$exchangeNode = $secrets.exchange

$apiKey = Get-SecretValue -Object $secrets -Names @("key", "apiKey", "api_key")
if (-not $apiKey -and $exchangeNode) {
    $apiKey = Get-SecretValue -Object $exchangeNode -Names @("key", "apiKey", "api_key")
}
if (-not $apiKey -and $secrets.binance) {
    $apiKey = Get-SecretValue -Object $secrets.binance -Names @("key", "apiKey", "api_key")
}

$apiSecret = Get-SecretValue -Object $secrets -Names @("secret", "apiSecret", "api_secret")
if (-not $apiSecret -and $exchangeNode) {
    $apiSecret = Get-SecretValue -Object $exchangeNode -Names @("secret", "apiSecret", "api_secret")
}
if (-not $apiSecret -and $secrets.binance) {
    $apiSecret = Get-SecretValue -Object $secrets.binance -Names @("secret", "apiSecret", "api_secret")
}

if (-not $apiKey -or -not $apiSecret) {
    throw "Secret file must provide exchange key/secret, either at top level or under exchange/binance."
}

$config = Get-Content -Raw -LiteralPath $templateConfigPath | ConvertFrom-Json
$config.exchange.skip_pair_validation = $true
$config.exchange.skip_open_order_update = $true
$config.exchange.key = $apiKey
$config.exchange.secret = $apiSecret
$config.exchange.ccxt_config = [pscustomobject]@{
    enableRateLimit = $true
    options = [pscustomobject]@{
        adjustForTimeDifference = $true
        recvWindow = 60000
        fetchCurrencies = $false
    }
}
$config.exchange.ccxt_async_config = [pscustomobject]@{
    enableRateLimit = $true
    options = [pscustomobject]@{
        adjustForTimeDifference = $true
        recvWindow = 60000
        fetchCurrencies = $false
    }
}
$config.max_open_trades = 3
$config.stake_amount = 20
$config.available_capital = 60
if (-not $config.internals) {
    $config | Add-Member -NotePropertyName internals -NotePropertyValue ([pscustomobject]@{})
}
$config.internals.process_throttle_secs = 60

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
    FREQTRADE_STRATEGY = "Top9RegimeMainTestLiveStrategy"
    FREQTRADE_STRATEGY_PATH = "/freqtrade/user_data/strategies/run"
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

    Invoke-RestMethod -Method Post -Headers $headers -Uri "$baseUrl/api/v1/start" | Out-Null

    Write-Host ""
    Write-Host "Top9 test-live bot started." -ForegroundColor Green
    Write-Host ("Runtime config: {0}" -f $runtimeConfigPath)
    Write-Host ("Secrets file  : {0}" -f $SecretsConfigPath)
}
finally {
    Pop-Location
}
