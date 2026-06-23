[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$containerName = "freqtrade-positive13-dryrun"
$configPath = Join-Path $PSScriptRoot "user_data\config.dryrun.dualtrend.combined.top50.positive13.max3.json"
$baseUrl = "http://127.0.0.1:8085"

Write-Host ""
Write-Host "Positive13 Max3 Dry-Run Status" -ForegroundColor Cyan
Write-Host "================================"

$container = docker ps --filter "name=^/$containerName$" --format "{{.ID}}|{{.Status}}|{{.Ports}}"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($container)) {
    Write-Host "Container is not running: $containerName" -ForegroundColor Red
    Write-Host "Start it with: start_positive13_max3_dryrun.cmd"
    exit 1
}

$parts = $container -split '\|'
Write-Host ("Container ID    : {0}" -f $parts[0])
Write-Host ("Container state : {0}" -f $parts[1])
Write-Host ("API port        : {0}" -f $parts[2])

$resource = docker stats $containerName --no-stream --format "CPU={{.CPUPerc}}|MEM={{.MemUsage}}|NET={{.NetIO}}"
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($resource)) {
    $resourceParts = $resource -split '\|'
    Write-Host ("Resource        : {0}, {1}, {2}" -f $resourceParts[0], $resourceParts[1], $resourceParts[2])
}

if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Dry-run config not found: $configPath"
}
$configFile = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
$authText = "{0}:{1}" -f $configFile.api_server.username, $configFile.api_server.password
$authToken = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($authText))
$headers = @{ Authorization = "Basic $authToken" }

function Invoke-BotApi {
    param([string]$Path)
    for ($i = 0; $i -lt 5; $i++) {
        try {
            return Invoke-RestMethod -Headers $headers -Uri "$baseUrl$Path" -TimeoutSec 10
        }
        catch {
            if ($i -eq 4) { throw }
            Start-Sleep -Seconds 2
        }
    }
}

try {
    $botConfig = Invoke-BotApi "/api/v1/show_config"
    $whitelist = Invoke-BotApi "/api/v1/whitelist"
    $profit = Invoke-BotApi "/api/v1/profit"
    $statusResponse = Invoke-BotApi "/api/v1/status"
    $status = if ($null -eq $statusResponse) { @() } else { @($statusResponse) }
    $tradeResponse = Invoke-BotApi "/api/v1/trades?limit=20"
}
catch {
    Write-Host ""
    Write-Host "API is not ready. Recent logs:" -ForegroundColor Yellow
    docker logs $containerName --tail 40 | Out-Host
    throw
}

$trades = if ($null -ne $tradeResponse.trades) { @($tradeResponse.trades) } else { @($tradeResponse) }
$recentTrades = $trades | Where-Object { -not $_.is_open } | Sort-Object close_date -Descending | Select-Object -First 10

Write-Host ""
Write-Host "Bot" -ForegroundColor Cyan
Write-Host "--------------------------------"
Write-Host ("Bot name        : {0}" -f $botConfig.bot_name)
Write-Host ("Strategy        : {0}" -f $botConfig.strategy)
Write-Host ("Run mode        : {0}" -f $botConfig.runmode)
Write-Host ("State           : {0}" -f $botConfig.state)
Write-Host ("Pairs           : {0}" -f $whitelist.length)
Write-Host ("Max open trades : {0}" -f $botConfig.max_open_trades)
Write-Host ("Virtual wallet  : {0} USDT" -f $configFile.dry_run_wallet)

Write-Host ""
Write-Host "Performance" -ForegroundColor Cyan
Write-Host "--------------------------------"
Write-Host ("Open trades     : {0}" -f $status.Count)
Write-Host ("Total trades    : {0}" -f $profit.trade_count)
Write-Host ("Closed trades   : {0}" -f $profit.closed_trade_count)
Write-Host ("Closed profit   : {0} USDT" -f ([math]::Round([double]$profit.profit_closed_coin, 4)))
Write-Host ("Total profit    : {0} USDT" -f ([math]::Round([double]$profit.profit_all_coin, 4)))
$estimatedEquity = [double]$configFile.dry_run_wallet + [double]$profit.profit_all_coin
Write-Host ("Est. equity     : {0} USDT" -f ([math]::Round($estimatedEquity, 4)))

Write-Host ""
Write-Host "Open Simulated Positions" -ForegroundColor Cyan
Write-Host "--------------------------------"
if ($status.Count -eq 0) {
    Write-Host "No open simulated positions."
}
else {
    $status |
        Select-Object pair, is_short, enter_tag, open_rate, current_rate, profit_pct, profit_abs, open_date |
        Format-Table -AutoSize
}

Write-Host ""
Write-Host "Recent Closed Simulated Trades" -ForegroundColor Cyan
Write-Host "--------------------------------"
if (@($recentTrades).Count -eq 0) {
    Write-Host "No completed simulated trades yet."
}
else {
    $recentTrades |
        Select-Object pair, is_short, enter_tag, exit_reason, profit_pct, profit_abs, close_date |
        Format-Table -AutoSize
}

Write-Host ""
Write-Host "Recent Warnings / Errors" -ForegroundColor Cyan
Write-Host "--------------------------------"
$previousErrorAction = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$logLines = docker logs $containerName --tail 150 2>&1 | ForEach-Object { $_.ToString() }
$ErrorActionPreference = $previousErrorAction
$alerts = $logLines |
    Select-String -Pattern " WARNING | ERROR | CRITICAL |Traceback" |
    Where-Object { $_ -notmatch "urllib3\.connectionpool|freqtrade\.rpc\.fiat_convert|api\.coingecko\.com" }
if (@($alerts).Count -eq 0) {
    Write-Host "No recent warnings or errors." -ForegroundColor Green
}
else {
    $alerts | Select-Object -Last 10 | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
}
