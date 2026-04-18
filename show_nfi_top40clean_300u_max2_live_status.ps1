$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$baseUrl = "http://127.0.0.1:8084"
$username = "Freqtrader"
$password = "NfiTop40Live!2026"

$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${username}:${password}"))
$headers = @{ Authorization = "Basic $auth" }

function Invoke-WithRetry {
    param(
        [string]$Uri
    )

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

$config = Invoke-WithRetry "$baseUrl/api/v1/show_config"
$profit = Invoke-WithRetry "$baseUrl/api/v1/profit"
$status = Invoke-WithRetry "$baseUrl/api/v1/status"
$trades = Invoke-WithRetry "$baseUrl/api/v1/trades"
$balance = Invoke-WithRetry "$baseUrl/api/v1/balance"

$openCount = @($status).Count
$recentTrades = @($trades) | Sort-Object close_date -Descending | Select-Object -First 5
$currencies = @($balance.currencies) | Select-Object currency, free, used, balance, bot_owned, est_stake

Write-Host ""
Write-Host "NFI Top40 Clean 300U Max2 实盘状态" -ForegroundColor Cyan
Write-Host "----------------------------------------"
Write-Host ("Bot 名称      : {0}" -f $config.bot_name)
Write-Host ("策略         : {0}" -f $config.strategy)
Write-Host ("运行模式      : {0}" -f $config.runmode)
Write-Host ("状态         : {0}" -f $config.state)
Write-Host ("当前持仓数    : {0}" -f $openCount)
Write-Host ("总交易笔数    : {0}" -f $profit.trade_count)
Write-Host ("已平仓笔数    : {0}" -f $profit.closed_trade_count)
Write-Host ("已实现盈亏    : {0} USDT" -f ([math]::Round([double]$profit.profit_closed_coin, 4)))
Write-Host ("总盈亏       : {0} USDT" -f ([math]::Round([double]$profit.profit_all_coin, 4)))

Write-Host ""
Write-Host "账户余额" -ForegroundColor Cyan
Write-Host "----------------------------------------"
Write-Host ("总权益       : {0} {1}" -f ([math]::Round([double]$balance.total, 6)), $balance.stake)
Write-Host ("Bot 归属权益  : {0} {1}" -f ([math]::Round([double]$balance.total_bot, 6)), $balance.stake)
if (@($currencies).Count -gt 0) {
    $currencies | Format-Table -AutoSize
}
else {
    Write-Host "未返回余额明细"
}

Write-Host ""
Write-Host "当前持仓" -ForegroundColor Cyan
Write-Host "----------------------------------------"
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
Write-Host "----------------------------------------"
if (@($recentTrades).Count -eq 0) {
    Write-Host "暂时还没有已完成交易"
}
else {
    @($recentTrades) |
        Select-Object pair, is_short, enter_tag, exit_reason, profit_pct, profit_abs, close_date |
        Format-Table -AutoSize
}

Write-Host ""
Read-Host "按回车键关闭"
