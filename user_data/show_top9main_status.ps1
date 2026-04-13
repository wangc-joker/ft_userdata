$ErrorActionPreference = "Stop"

$containerName = "freqtrade-v2dry-top9"
$baseUrl = "http://127.0.0.1:8081"
$username = "Freqtrader"
$password = "Top9DryRun!2026"
$strategyName = "Top9RegimeMainStrategy"

$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${username}:${password}"))

$existingContainer = docker ps -a --filter "name=^$containerName$" --format "{{.ID}}"
if (-not $existingContainer) {
    Write-Host "Top9 dry-run container is not running." -ForegroundColor Yellow
    Write-Host "If you want the current live bot, use: .\show_top9main_live_status.cmd"
    exit 1
}

function Invoke-WithRetry {
    param(
        [string]$Uri
    )

    for ($i = 0; $i -lt 5; $i++) {
        try {
            $response = & docker exec $containerName sh -lc "curl -sS -H 'Authorization: Basic $auth' $Uri"
            if (-not $response) {
                throw "Empty response from $Uri"
            }
            return $response | ConvertFrom-Json
        }
        catch {
            if ($i -eq 4) {
                throw
            }
            Start-Sleep -Seconds 2
        }
    }
}

$profit = Invoke-WithRetry "$baseUrl/api/v1/profit"
$status = Invoke-WithRetry "$baseUrl/api/v1/status"
$trades = Invoke-WithRetry "$baseUrl/api/v1/trades"

$openCount = @($status).Count
$recentTrades = @($trades) | Sort-Object close_date -Descending | Select-Object -First 5

Write-Host ""
Write-Host "Top9 主版本模拟盘状态" -ForegroundColor Cyan
Write-Host "------------------------------"
Write-Host ("策略         : {0}" -f $strategyName)
Write-Host ("当前持仓数   : {0}" -f $openCount)
Write-Host ("总交易笔数   : {0}" -f $profit.trade_count)
Write-Host ("已平仓笔数   : {0}" -f $profit.closed_trade_count)
Write-Host ("盈利笔数     : {0}" -f $profit.winning_trades)
Write-Host ("亏损笔数     : {0}" -f $profit.losing_trades)
Write-Host ("胜率         : {0}%" -f ([math]::Round([double]$profit.winrate * 100, 2)))
Write-Host ("已实现盈亏   : {0} {1}" -f ([math]::Round([double]$profit.profit_closed_coin, 4)), $profit.profit_closed_coin_currency)
Write-Host ("总盈亏       : {0} {1}" -f ([math]::Round([double]$profit.profit_all_coin, 4)), $profit.profit_closed_coin_currency)
Write-Host ("最大回撤     : {0}%" -f ([math]::Round([double]$profit.max_drawdown * 100, 2)))

Write-Host ""
Write-Host "当前持仓" -ForegroundColor Cyan
Write-Host "------------------------------"
if ($openCount -eq 0) {
    Write-Host "当前没有持仓"
}
else {
    @($status) |
        Select-Object pair, is_short, amount, open_rate, current_rate, profit_pct, profit_abs |
        Format-Table -AutoSize
}

Write-Host ""
Write-Host "最近 5 笔交易" -ForegroundColor Cyan
Write-Host "------------------------------"
if (@($recentTrades).Count -eq 0) {
    Write-Host "暂时还没有已完成交易"
}
else {
    @($recentTrades) |
        Select-Object pair, is_short, enter_tag, exit_reason, profit_pct, profit_abs, close_date |
        Format-Table -AutoSize
}
