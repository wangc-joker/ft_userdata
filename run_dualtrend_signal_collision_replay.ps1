[CmdletBinding()]
param(
    [string]$Timerange = "20210729-20260618",
    [string]$OutputDirectory = "user_data/analysis/signal_collision_audit_2026-07-24/five_year"
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$config = "/freqtrade/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json"
$strategyPath = "/freqtrade/user_data/strategies"
$hostOutput = Join-Path $PSScriptRoot ($OutputDirectory -replace "/", "\")
$containerOutput = "/freqtrade/" + ($OutputDirectory -replace "\\", "/")
New-Item -ItemType Directory -Force -Path $hostOutput | Out-Null

Write-Host "Running constrained max3 signal export..." -ForegroundColor Cyan
docker --context desktop-linux compose run --rm freqtrade backtesting `
    --config $config `
    --strategy-path $strategyPath `
    --strategy DualTrendPyramidSecondAdd20LongMicroV1Strategy `
    --timeframe 1h `
    --timeframe-detail 5m `
    --timerange $Timerange `
    --max-open-trades 3 `
    --enable-protections `
    --cache none `
    --export signals `
    --export-directory "$containerOutput/max3_signals"
if ($LASTEXITCODE -ne 0) { throw "Constrained max3 backtest failed." }

Write-Host "Running fixed-stake max100 counterfactual..." -ForegroundColor Cyan
docker --context desktop-linux compose run --rm freqtrade backtesting `
    --config $config `
    --strategy-path $strategyPath `
    --strategy DualTrendPyramidSecondAdd20LongMicroCollisionReplayV1Strategy `
    --timeframe 1h `
    --timeframe-detail 5m `
    --timerange $Timerange `
    --max-open-trades 100 `
    --stake-amount 1000 `
    --dry-run-wallet 1000000 `
    --cache none `
    --export trades `
    --export-directory "$containerOutput/max100_counterfactual"
if ($LASTEXITCODE -ne 0) { throw "Counterfactual max100 backtest failed." }

$max3 = Get-ChildItem -LiteralPath $hostOutput -Filter "max3_signals-*.zip" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
$max100 = Get-ChildItem -LiteralPath $hostOutput -Filter "max100_counterfactual-*.zip" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $max3 -or $null -eq $max100) {
    throw "Unable to locate replay archives in $hostOutput"
}

Write-Host "Building collision audit..." -ForegroundColor Cyan
docker --context desktop-linux compose run --rm --entrypoint python freqtrade `
    /freqtrade/user_data/analysis/dualtrend_signal_collision_replay.py `
    --constrained-zip "/freqtrade/$OutputDirectory/$($max3.Name)" `
    --counterfactual-zip "/freqtrade/$OutputDirectory/$($max100.Name)" `
    --output-dir "$containerOutput/report" `
    --title "DualTrend Positive13 five-year signal collision replay"
if ($LASTEXITCODE -ne 0) { throw "Collision report generation failed." }

Write-Host "Collision replay complete: $hostOutput\report\collision_replay.md" -ForegroundColor Green
