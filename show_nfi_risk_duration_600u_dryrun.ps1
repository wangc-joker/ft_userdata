[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$containerName = "freqtrade-dryrun"

Write-Host ""
Write-Host "NFIRiskDuration 600U Dry-Run Status" -ForegroundColor Cyan
Write-Host "====================================="

# Helper: run docker and capture output safely (stdout + stderr as strings)
function Get-DockerOutput($cmd) {
    $result = docker $cmd 2>&1 | ForEach-Object {
        if ($_ -is [System.Management.Automation.ErrorRecord]) {
            $_.ToString()
        } else {
            $_
        }
    }
    return $result
}

# 1. Container status
Write-Host ""
Write-Host "Container Status" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$container = Get-DockerOutput @("ps", "--filter", "name=$containerName", "--format", "{{.ID}}|{{.Status}}|{{.Ports}}")
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($container)) {
    Write-Host "Container '$containerName' is NOT running." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}
$parts = $container -split "\|"
Write-Host ("Container ID : {0}" -f $parts[0])
Write-Host ("Status       : {0}" -f $parts[1])
Write-Host ("Ports        : {0}" -f $parts[2])

# 2. Config summary
Write-Host ""
Write-Host "Config" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$configPath = Join-Path $PSScriptRoot "user_data\config.dryrun.nfi-risk-duration.600u.top30.max4.json"
if (Test-Path -LiteralPath $configPath -PathType Leaf) {
    $config = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
    Write-Host ("Bot Name       : {0}" -f $config.bot_name)
    Write-Host ("Strategy       : {0}" -f $config.strategy)
    Write-Host ("Wallet         : {0} USDT" -f $config.dry_run_wallet)
    Write-Host ("Max Open       : {0}" -f $config.max_open_trades)
    Write-Host ("Pairs          : {0}" -f @($config.exchange.pair_whitelist).Count)
    Write-Host ("Trading Mode   : {0} / {1}" -f $config.trading_mode, $config.margin_mode)
}
else {
    Write-Host "Config file not found at: $configPath" -ForegroundColor Red
}

# 3. Recent logs - color-coded
Write-Host ""
Write-Host "Recent Activity (last 30 log lines)" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$logs = Get-DockerOutput @("logs", $containerName, "--tail", "30")
$logs | ForEach-Object {
    $line = $_
    if ($line -match "ERROR|CRITICAL|Traceback") {
        Write-Host $_ -ForegroundColor Red
    }
    elseif ($line -match "WARNING") {
        Write-Host $_ -ForegroundColor Yellow
    }
    elseif ($line -match "Enter Long|Enter Short|Buy|Sell|Exit|Order filled|New trade|profit_abs|custom_exit") {
        Write-Host $_ -ForegroundColor Green
    }
    else {
        Write-Host $_
    }
}

# 4. Trade activity summary from full logs
Write-Host ""
Write-Host "Trade Activity Summary" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$allLogs = Get-DockerOutput @("logs", $containerName)
$buyCount  = @($allLogs | Select-String -Pattern "Enter Long|Enter Short|New trade" -SimpleMatch).Count
$exitCount = @($allLogs | Select-String -Pattern "Exit Signal|Exit " -SimpleMatch).Count
$warnCount = @($allLogs | Select-String -Pattern "WARNING" -SimpleMatch).Count
$errCount  = @($allLogs | Select-String -Pattern "ERROR|CRITICAL|Traceback" -SimpleMatch).Count

Write-Host ("Enter signals    : {0}" -f $buyCount)
Write-Host ("Exit signals     : {0}" -f $exitCount)
Write-Host ("Warnings         : {0}" -f $warnCount)
Write-Host ("Errors           : {0}" -f $errCount)

# 5. Show latest heartbeat from logs
Write-Host ""
Write-Host "Latest Heartbeat" -ForegroundColor Cyan
Write-Host "----------------------------------------"
$hbLine = $allLogs | Select-String -Pattern "Bot heartbeat" -SimpleMatch | Select-Object -Last 1
if ($hbLine) {
    $hbLine
} else {
    Write-Host "(waiting for first heartbeat...)" -ForegroundColor DarkYellow
}

# 6. Data download status
Write-Host ""
Write-Host "Data Download Status" -ForegroundColor Cyan
Write-Host "----------------------------------------"
if ($allLogs -match "ExchangeNotAvailable") {
    $retryCount = @($allLogs | Select-String -Pattern "Retrying still for" -SimpleMatch).Count
    Write-Host "Binance Futures API: connecting (retries: $retryCount)..." -ForegroundColor Yellow
    Write-Host "The bot is downloading historical data and will start trading once ready." -ForegroundColor DarkYellow
} elseif ($allLogs -match "Entry|Enter|Signal|trade") {
    Write-Host "Data ready - bot is analyzing signals." -ForegroundColor Green
} else {
    Write-Host "Bot is initializing..." -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Quick commands:" -ForegroundColor DarkYellow
Write-Host "  View live log : docker logs $containerName -f --tail 20" -ForegroundColor DarkYellow
Write-Host "  Stop dry-run  : docker rm -f $containerName" -ForegroundColor DarkYellow
Write-Host ""
