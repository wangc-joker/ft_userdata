[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "user_data\analysis\dualtrend_signal_collision_shadow.py"
$databasePath = Join-Path $PSScriptRoot "user_data\analysis\signal_collision_shadow.sqlite"
$pidPath = Join-Path $PSScriptRoot "user_data\analysis\signal_collision_shadow.pid"

$running = $false
$processId = $null
if (Test-Path -LiteralPath $pidPath) {
    $processId = [int](Get-Content -Raw -LiteralPath $pidPath)
    $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
    $running = $null -ne $processInfo -and $processInfo.CommandLine -like "*dualtrend_signal_collision_shadow.py*"
}

Write-Host ""
Write-Host "LongMicro Signal Collision Shadow" -ForegroundColor Cyan
Write-Host "================================="
Write-Host ("Collector : {0}" -f $(if ($running) { "running (PID $processId)" } else { "stopped" }))
Write-Host ("Database  : {0}" -f $databasePath)
Write-Host ""
python $scriptPath --database $databasePath --summary
