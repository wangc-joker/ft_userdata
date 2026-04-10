$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:8080"
$username = "Freqtrader"
$password = "V2DryRun!2026"
$credentialText = "{0}:{1}" -f $username, $password
$token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($credentialText))
$headers = @{ Authorization = "Basic $token" }

try {
    $status = Invoke-RestMethod -Headers $headers -Uri ($baseUrl + "/api/v1/status")
    $profit = Invoke-RestMethod -Headers $headers -Uri ($baseUrl + "/api/v1/profit")
    $trades = Invoke-RestMethod -Headers $headers -Uri ($baseUrl + "/api/v1/trades")
}
catch {
    Write-Host "无法连接到 V2 模拟盘 API：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请先确认容器仍在运行：docker ps"
    exit 1
}

$openCount = @($status).Count
$tradeCount = [int]$profit.trade_count
$closedTradeCount = [int]$profit.closed_trade_count
$winningTrades = [int]$profit.winning_trades
$losingTrades = [int]$profit.losing_trades

Write-Host "V2 模拟盘状态" -ForegroundColor Cyan
Write-Host "=============================="
Write-Host ("运行开始: {0}" -f $profit.bot_start_date)
Write-Host ("当前持仓数: {0}" -f $openCount)
Write-Host ("总交易笔数: {0}" -f $tradeCount)
Write-Host ("已平仓笔数: {0}" -f $closedTradeCount)
Write-Host ("盈利笔数: {0}" -f $winningTrades)
Write-Host ("亏损笔数: {0}" -f $losingTrades)
Write-Host ("胜率: {0}%" -f ([math]::Round([double]$profit.winrate * 100, 2)))
Write-Host ("已实现盈亏: {0} USDT" -f ([math]::Round([double]$profit.profit_closed_coin, 4)))
Write-Host ("总盈亏(含持仓): {0} USDT" -f ([math]::Round([double]$profit.profit_all_coin, 4)))
Write-Host ("最大回撤: {0} USDT" -f ([math]::Round([double]$profit.max_drawdown_abs, 4)))
Write-Host ""

if ($openCount -gt 0) {
    Write-Host "当前持仓" -ForegroundColor Cyan
    Write-Host "=============================="
    foreach ($item in $status) {
        if ($item.is_short) {
            $side = "空头"
        }
        else {
            $side = "多头"
        }

        Write-Host ("交易对: {0}" -f $item.pair)
        Write-Host ("方向: {0}" -f $side)
        Write-Host ("标签: {0}" -f $item.enter_tag)
        Write-Host ("开仓时间: {0}" -f $item.open_date)
        Write-Host ("开仓价格: {0}" -f $item.open_rate)
        Write-Host ("当前盈亏: {0} USDT / {1}%" -f ([math]::Round([double]$item.profit_abs, 4)), ([math]::Round([double]$item.profit_pct, 2)))
        Write-Host "------------------------------"
    }
}
else {
    Write-Host "当前没有持仓。"
}

if ([int]$trades.total_trades -gt 0) {
    Write-Host ""
    Write-Host "最近 5 笔交易" -ForegroundColor Cyan
    Write-Host "=============================="
    @($trades.trades) | Select-Object -First 5 | ForEach-Object {
        if ($_.is_short) {
            $side = "空头"
        }
        else {
            $side = "多头"
        }

        Write-Host ("{0} | {1} | {2} | 盈亏 {3} USDT" -f $_.pair, $side, $_.close_date, ([math]::Round([double]$_.profit_abs, 4)))
    }
}
