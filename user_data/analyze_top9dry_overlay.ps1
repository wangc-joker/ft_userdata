$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:8081"
$username = "Freqtrader"
$password = "Top9DryRun!2026"
$outputDir = "D:\test\ft_userdata\user_data\runtime_reports"
$outputPath = Join-Path $outputDir "top9_overlay_latest.json"

if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

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

function Get-TagStats {
    param(
        [array]$Trades
    )

    return @($Trades |
        Group-Object enter_tag |
        ForEach-Object {
            $profit = ($_.Group | Measure-Object profit_abs -Sum).Sum
            $wins = @($_.Group | Where-Object { [double]$_.profit_abs -gt 0 }).Count
            $count = $_.Count
            [pscustomobject]@{
                EnterTag = $_.Name
                Trades = $count
                ProfitUSDT = [math]::Round([double]$profit, 2)
                WinRatePct = if ($count -gt 0) { [math]::Round(($wins / $count) * 100, 2) } else { 0 }
            }
        } |
        Sort-Object ProfitUSDT -Descending)
}

$profit = Invoke-WithRetry "$baseUrl/api/v1/profit"
$status = @((Invoke-WithRetry "$baseUrl/api/v1/status"))
$trades = @((Invoke-WithRetry "$baseUrl/api/v1/trades"))
$config = Invoke-WithRetry "$baseUrl/api/v1/show_config"

$closedTrades = @($trades | Where-Object { $_.close_date })
$recentClosed = @($closedTrades | Sort-Object close_date -Descending | Select-Object -First 20)
$recent10 = @($closedTrades | Sort-Object close_date -Descending | Select-Object -First 10)
$recent20 = @($closedTrades | Sort-Object close_date -Descending | Select-Object -First 20)
$recent5 = @($closedTrades | Sort-Object close_date -Descending | Select-Object -First 5)

$recent10Profit = [double](($recent10 | Measure-Object profit_abs -Sum).Sum)
$recent20Profit = [double](($recent20 | Measure-Object profit_abs -Sum).Sum)
$recent10WinRate = if (@($recent10).Count -gt 0) {
    [math]::Round((@($recent10 | Where-Object { [double]$_.profit_abs -gt 0 }).Count / @($recent10).Count) * 100, 2)
} else { 0 }

$openCount = @($status).Count
$openProfit = if ($openCount -gt 0) {
    [math]::Round([double](($status | Measure-Object profit_abs -Sum).Sum), 4)
} else { 0 }
$openProfitPct = if ($openCount -gt 0) {
    [math]::Round([double](($status | Measure-Object profit_pct -Average).Average), 2)
} else { 0 }

$tagStats = Get-TagStats -Trades $recent20
$short1hStats = $tagStats | Where-Object { $_.EnterTag -eq "short_1h_center" } | Select-Object -First 1
$dogeRecent = @($recent20 | Where-Object { $_.pair -eq "DOGE/USDT:USDT" })
$dogeRecentProfit = [double](($dogeRecent | Measure-Object profit_abs -Sum).Sum)

$riskLevel = "GREEN"
$alerts = New-Object System.Collections.Generic.List[string]
$recommendations = New-Object System.Collections.Generic.List[string]

if ([double]$profit.max_drawdown -ge 0.12) {
    $riskLevel = "RED"
    $alerts.Add("账户最大回撤已经超过 12%，当前更接近高风险状态。")
}
elseif ([double]$profit.max_drawdown -ge 0.08) {
    $riskLevel = "YELLOW"
    $alerts.Add("账户最大回撤超过 8%，建议提高风险警惕。")
}

if (@($recent10).Count -ge 5 -and ($recent10Profit -lt -20 -or $recent10WinRate -lt 25)) {
    if ($riskLevel -eq "GREEN") {
        $riskLevel = "YELLOW"
    }
    $alerts.Add("最近 10 笔交易表现偏弱，短期执行质量下降。")
    $recommendations.Add("建议先观察，减少主动加风险，重点盯住 short_1h_center。")
}

if ($short1hStats -and $short1hStats.ProfitUSDT -lt 0) {
    if ($riskLevel -eq "GREEN") {
        $riskLevel = "YELLOW"
    }
    $alerts.Add("最近 20 笔里 short_1h_center 为负贡献。")
    $recommendations.Add("如果后续继续连亏，可以考虑临时停用 short_1h_center，再做对照。")
}
elseif ($short1hStats) {
    $recommendations.Add("最近 20 笔里 short_1h_center 仍有正贡献，当前不建议贸然关掉。")
}

if ($dogeRecent.Count -ge 3 -and $dogeRecentProfit -lt -10) {
    if ($riskLevel -eq "GREEN") {
        $riskLevel = "YELLOW"
    }
    $alerts.Add("DOGE 最近交易表现偏弱，容易放大组合波动。")
    $recommendations.Add("建议重点观察 DOGE，必要时单独降权或临时剔除。")
}

if ($openCount -eq 0) {
    $recommendations.Add("当前没有持仓，适合先观察下一轮信号质量，而不是主动追单。")
}
elseif ($openProfit -lt -15) {
    if ($riskLevel -eq "GREEN") {
        $riskLevel = "YELLOW"
    }
    $alerts.Add("当前持仓浮亏已经比较明显。")
    $recommendations.Add("建议优先看持仓是否集中在同一方向或同一币种。")
}
else {
    $recommendations.Add("当前持仓风险可控，重点观察是否出现连续同侧仓位。")
}

if ($alerts.Count -eq 0) {
    $alerts.Add("目前没有明显异常，系统处于可继续观察的状态。")
}

$report = [pscustomobject]@{
    generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    strategy = $config.strategy
    state = $config.state
    timeframe = $config.timeframe
    process_throttle_secs = 120
    account = [pscustomobject]@{
        trade_count = $profit.trade_count
        closed_trade_count = $profit.closed_trade_count
        winning_trades = $profit.winning_trades
        losing_trades = $profit.losing_trades
        winrate_pct = [math]::Round([double]$profit.winrate * 100, 2)
        realized_profit = [math]::Round([double]$profit.profit_closed_coin, 4)
        total_profit = [math]::Round([double]$profit.profit_all_coin, 4)
        max_drawdown_pct = [math]::Round([double]$profit.max_drawdown * 100, 2)
    }
    open_positions = [pscustomobject]@{
        count = $openCount
        total_profit = $openProfit
        average_profit_pct = $openProfitPct
        positions = @($status | Select-Object pair, is_short, amount, open_rate, current_rate, profit_pct, profit_abs)
    }
    recent_performance = [pscustomobject]@{
        recent_10_trades_profit = [math]::Round($recent10Profit, 2)
        recent_10_trades_winrate_pct = $recent10WinRate
        recent_20_trades_profit = [math]::Round($recent20Profit, 2)
        tag_stats = $tagStats
        recent_trades = @($recent5 | Select-Object pair, is_short, enter_tag, exit_reason, profit_pct, profit_abs, close_date)
    }
    overlay = [pscustomobject]@{
        risk_level = $riskLevel
        alerts = @($alerts)
        recommendations = @($recommendations)
    }
}

$report | ConvertTo-Json -Depth 6 | Set-Content -Path $outputPath -Encoding UTF8

Write-Host ""
Write-Host "Top9 动态分析" -ForegroundColor Cyan
Write-Host "------------------------------"
Write-Host ("风险等级     : {0}" -f $riskLevel)
Write-Host ("最近10笔盈亏 : {0} USDT" -f ([math]::Round($recent10Profit, 2)))
Write-Host ("最近10笔胜率 : {0}%" -f $recent10WinRate)
Write-Host ("最近20笔盈亏 : {0} USDT" -f ([math]::Round($recent20Profit, 2)))
Write-Host ("当前持仓数   : {0}" -f $openCount)
Write-Host ("持仓浮盈亏   : {0} USDT" -f $openProfit)
Write-Host ("最大回撤     : {0}%" -f ([math]::Round([double]$profit.max_drawdown * 100, 2)))

Write-Host ""
Write-Host "风险提示" -ForegroundColor Cyan
Write-Host "------------------------------"
foreach ($item in $alerts) {
    Write-Host ("- {0}" -f $item)
}

Write-Host ""
Write-Host "建议动作" -ForegroundColor Cyan
Write-Host "------------------------------"
foreach ($item in $recommendations) {
    Write-Host ("- {0}" -f $item)
}

Write-Host ""
Write-Host "最近20笔分支表现" -ForegroundColor Cyan
Write-Host "------------------------------"
if ($tagStats.Count -eq 0) {
    Write-Host "暂时还没有已平仓交易"
}
else {
    $tagStats | Format-Table EnterTag, Trades, ProfitUSDT, WinRatePct -AutoSize
}

Write-Host ""
Write-Host ("分析快照已写入: {0}" -f $outputPath)
