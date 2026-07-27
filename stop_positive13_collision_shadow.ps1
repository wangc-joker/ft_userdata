[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$pidPath = Join-Path $PSScriptRoot "user_data\analysis\signal_collision_shadow.pid"
$scriptName = "dualtrend_signal_collision_shadow.py"

if (-not (Test-Path -LiteralPath $pidPath)) {
    Write-Host "Collision shadow collector is not running." -ForegroundColor Yellow
    exit 0
}

$processId = [int](Get-Content -Raw -LiteralPath $pidPath)
$processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
if ($null -eq $processInfo) {
    Remove-Item -LiteralPath $pidPath -Force
    Write-Host "Removed stale collision shadow PID file." -ForegroundColor Yellow
    exit 0
}
if ($processInfo.CommandLine -notlike "*$scriptName*") {
    throw "PID $processId does not belong to the collision shadow collector."
}

Stop-Process -Id $processId -Force
Remove-Item -LiteralPath $pidPath -Force
Write-Host "Collision shadow collector stopped." -ForegroundColor Green
