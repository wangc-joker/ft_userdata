[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:8084"
$username = "Freqtrader"
$password = "Top9MainLive!2026"
$strategyName = "Top9RegimeMainStrategy"
$credentialText = "{0}:{1}" -f $username, $password
$token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($credentialText))
$headers = @{ Authorization = "Basic $token" }

function Invoke-WithRetry {
    param([string]$Uri)

    for ($i = 0; $i -lt 5; $i++) {
        try {
            return Invoke-RestMethod -Headers $headers -Uri $Uri
        }
        catch {
            if ($i -eq 4) {
                throw
            }
            Start-Sleep -Seconds 2
        }
    }
}

try {
    $profit = Invoke-WithRetry "$baseUrl/api/v1/profit"
    $status = Invoke-WithRetry "$baseUrl/api/v1/status"
    $trades = Invoke-WithRetry "$baseUrl/api/v1/trades"
}
catch {
    Write-Host "Unable to connect to the Top9 main live API." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    Write-Host ""
    Write-Host "If it is not running yet, start it with: start_top9main_live.ps1 <secrets path>"
    exit 1
}

$openCount = @($status).Count
$recentTrades = @($trades) | Sort-Object close_date -Descending | Select-Object -First 5

Write-Host ""
Write-Host "Top9 main live status" -ForegroundColor Cyan
Write-Host "------------------------------"
Write-Host ("Strategy     : {0}" -f $strategyName)
Write-Host ("Open trades  : {0}" -f $openCount)
Write-Host ("Total trades  : {0}" -f $profit.trade_count)
Write-Host ("Closed trades : {0}" -f $profit.closed_trade_count)
Write-Host ("Winning       : {0}" -f $profit.winning_trades)
Write-Host ("Losing        : {0}" -f $profit.losing_trades)
Write-Host ("Winrate       : {0}%" -f ([math]::Round([double]$profit.winrate * 100, 2)))
Write-Host ("Closed PnL    : {0} {1}" -f ([math]::Round([double]$profit.profit_closed_coin, 4)), $profit.profit_closed_coin_currency)
Write-Host ("Total PnL     : {0} {1}" -f ([math]::Round([double]$profit.profit_all_coin, 4)), $profit.profit_closed_coin_currency)
Write-Host ("Max drawdown  : {0}%" -f ([math]::Round([double]$profit.max_drawdown * 100, 2)))

Write-Host ""
Write-Host "Open trades" -ForegroundColor Cyan
Write-Host "------------------------------"
if ($openCount -eq 0) {
    Write-Host "No open trades"
}
else {
    @($status) |
        Select-Object pair, is_short, leverage, amount, open_rate, current_rate, profit_pct, profit_abs |
        Format-Table -AutoSize
}

Write-Host ""
Write-Host "Recent 5 trades" -ForegroundColor Cyan
Write-Host "------------------------------"
if (@($recentTrades).Count -eq 0) {
    Write-Host "No completed trades yet"
}
else {
    @($recentTrades) |
        Select-Object pair, is_short, leverage, enter_tag, exit_reason, profit_pct, profit_abs, close_date |
        Format-Table -AutoSize
}
