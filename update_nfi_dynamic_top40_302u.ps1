$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$repoRoot = $PSScriptRoot
$testRoot = Join-Path $repoRoot "user_data\tests\nfi_top_volume_3y_1000u"
$templatePath = Join-Path $testRoot "config.template.nfi.1y.302u.top40.dynamic.max2.json"
$outputConfigPath = Join-Path $testRoot "config.backtest.nfi.1y.302u.top40.dynamic.max2.json"
$pairsPath = Join-Path $testRoot "pairs.dynamic.top40.302u.json"
$reportPath = Join-Path $testRoot "pairs.dynamic.top40.302u.report.json"

$targetCount = 40
$quoteAsset = "USDT"
$excludedSuffixes = @("BULL", "BEAR", "UP", "DOWN")
$excludedBaseAssets = @("XAU", "XAG", "XAUT", "PAXG", "TSLA")

function Get-Json {
    param([string]$Uri)
    Invoke-RestMethod -Uri $Uri -Method Get -TimeoutSec 60
}

function Test-EligibleSymbol {
    param(
        [string]$Symbol,
        [string]$BaseAsset,
        [string]$Status,
        [string]$ContractType,
        [string]$QuoteAsset
    )

    if ($QuoteAsset -ne "USDT") { return $false }
    if ($Status -ne "TRADING") { return $false }
    if ($ContractType -ne "PERPETUAL") { return $false }
    if ([string]::IsNullOrWhiteSpace($BaseAsset)) { return $false }
    if ($BaseAsset -notmatch '^[A-Z0-9]+$') { return $false }
    if ($excludedBaseAssets -contains $BaseAsset) { return $false }

    foreach ($suffix in $excludedSuffixes) {
        if ($BaseAsset.EndsWith($suffix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $false
        }
    }

    return $true
}

if (-not (Test-Path -LiteralPath $templatePath -PathType Leaf)) {
    throw "Template config not found: $templatePath"
}

$exchangeInfo = Get-Json "https://fapi.binance.com/fapi/v1/exchangeInfo"
$tickers = Get-Json "https://fapi.binance.com/fapi/v1/ticker/24hr"

$symbolMeta = @{}
foreach ($s in $exchangeInfo.symbols) {
    $symbolMeta[$s.symbol] = $s
}

$rankedItems = foreach ($ticker in $tickers) {
    $meta = $symbolMeta[$ticker.symbol]
    if (-not $meta) { continue }

    if (-not (Test-EligibleSymbol `
        -Symbol $ticker.symbol `
        -BaseAsset $meta.baseAsset `
        -Status $meta.status `
        -ContractType $meta.contractType `
        -QuoteAsset $meta.quoteAsset)) {
        continue
    }

    [pscustomobject]@{
        symbol = $ticker.symbol
        baseAsset = $meta.baseAsset
        pair = "{0}/{1}:{1}" -f $meta.baseAsset, $quoteAsset
        quoteVolume = [double]$ticker.quoteVolume
        volume = [double]$ticker.volume
    }
}

$ranked = $rankedItems | Sort-Object quoteVolume -Descending

$selected = @($ranked | Select-Object -First $targetCount)

if ($selected.Count -lt $targetCount) {
    throw "Only found $($selected.Count) eligible symbols after filtering, fewer than target $targetCount."
}

$config = Get-Content -Raw -LiteralPath $templatePath | ConvertFrom-Json
$config.exchange.pair_whitelist = @($selected.pair)

[System.IO.File]::WriteAllText(
    $outputConfigPath,
    ($config | ConvertTo-Json -Depth 32),
    [System.Text.UTF8Encoding]::new($false)
)

[System.IO.File]::WriteAllText(
    $pairsPath,
    (@($selected.pair) | ConvertTo-Json -Depth 4),
    [System.Text.UTF8Encoding]::new($false)
)

$report = [pscustomobject]@{
    generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
    source = "Binance Futures 24h ticker quoteVolume"
    target_count = $targetCount
    selected_count = $selected.Count
    filter = [pscustomobject]@{
        quote_asset = $quoteAsset
        contract_type = "PERPETUAL"
        status = "TRADING"
        excluded_suffixes = $excludedSuffixes
        excluded_base_assets = $excludedBaseAssets
        fill_strategy = "Sort by quoteVolume descending and take first eligible 40."
    }
    pairs = @($selected)
}

[System.IO.File]::WriteAllText(
    $reportPath,
    ($report | ConvertTo-Json -Depth 16),
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host ""
Write-Host "Dynamic Top40 config updated." -ForegroundColor Green
Write-Host ("Config : {0}" -f $outputConfigPath)
Write-Host ("Pairs  : {0}" -f $pairsPath)
Write-Host ("Report : {0}" -f $reportPath)
Write-Host ""
Write-Host "Selected pairs:" -ForegroundColor Cyan
@($selected.pair) | ForEach-Object { Write-Host $_ }
