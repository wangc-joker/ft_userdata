[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$stakeAmount = 20
$pairs = @(
    "BTC/USDT:USDT",
    "SOL/USDT:USDT",
    "TRX/USDT:USDT",
    "ADA/USDT:USDT",
    "BNB/USDT:USDT",
    "ZEC/USDT:USDT",
    "ETH/USDT:USDT",
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT"
)

function Get-BinanceSymbol {
    param([string]$Pair)
    return ($Pair -replace '/', '') -replace ':USDT$', ''
}

function Get-ConfiguredLeverage {
    param([string]$Pair)
    if ($Pair -eq "BTC/USDT:USDT") {
        return 8
    }
    if ($Pair -eq "ETH/USDT:USDT") {
        return 2
    }
    return 1
}

try {
    $exchangeInfo = Invoke-RestMethod -Uri "https://fapi.binance.com/fapi/v1/exchangeInfo"
}
catch {
    Write-Host "Unable to query Binance futures exchangeInfo." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    exit 1
}

$symbolMap = @{}
foreach ($symbol in $exchangeInfo.symbols) {
    $symbolMap[$symbol.symbol] = $symbol
}

Write-Host ""
Write-Host "Minimum order check" -ForegroundColor Cyan
Write-Host "------------------------------"
Write-Host ("Assumed stake amount: {0} USDT" -f $stakeAmount)
Write-Host ""

foreach ($pair in $pairs) {
    $symbolName = Get-BinanceSymbol -Pair $pair
    $symbol = $symbolMap[$symbolName]
    if (-not $symbol) {
        Write-Host ("{0} : not returned by Binance exchangeInfo" -f $pair)
        continue
    }

    $lotSize = $symbol.filters | Where-Object filterType -eq "LOT_SIZE" | Select-Object -First 1
    $notional = $symbol.filters | Where-Object filterType -eq "MIN_NOTIONAL" | Select-Object -First 1
    $minQty = if ($lotSize) { [double]$lotSize.minQty } else { $null }
    $stepSize = if ($lotSize) { [double]$lotSize.stepSize } else { $null }
    $minNotional = if ($notional) { [double]$notional.notional } else { $null }
    $leverage = Get-ConfiguredLeverage -Pair $pair
    $effectiveNotional = $stakeAmount * $leverage
    $ok = $true
    if ($minNotional -ne $null -and $effectiveNotional -lt $minNotional) {
        $ok = $false
    }

    $statusText = if ($ok) { "OK" } else { "Too small" }
    Write-Host ("{0} : leverage={1} effectiveNotional={2} minQty={3} stepSize={4} minNotional={5} => {6}" -f $pair, $leverage, $effectiveNotional, $minQty, $stepSize, $minNotional, $statusText)
}
