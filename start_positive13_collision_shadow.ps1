[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "user_data\analysis\dualtrend_signal_collision_shadow.py"
$configPath = Join-Path $PSScriptRoot "user_data\config.dryrun.dualtrend.longmicro.positive13.max3.json"
$databasePath = Join-Path $PSScriptRoot "user_data\analysis\signal_collision_shadow.sqlite"
$pidPath = Join-Path $PSScriptRoot "user_data\analysis\signal_collision_shadow.pid"
$stdoutPath = Join-Path $PSScriptRoot "user_data\logs\signal_collision_shadow.stdout.log"
$stderrPath = Join-Path $PSScriptRoot "user_data\logs\signal_collision_shadow.stderr.log"

if (Test-Path -LiteralPath $pidPath) {
    $existingId = [int](Get-Content -Raw -LiteralPath $pidPath)
    $existing = Get-Process -Id $existingId -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        Write-Host "Collision shadow collector is already running (PID $existingId)." -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -LiteralPath $pidPath -Force
}

$python = (Get-Command python -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $stdoutPath) | Out-Null
$arguments = @(
    $scriptPath,
    "--watch",
    "--interval", "300",
    "--limit", "500",
    "--config", $configPath,
    "--database", $databasePath
)
$containerName = "freqtrade-positive13-longmicro-observation"
$containerStartedAt = docker --context desktop-linux inspect $containerName --format "{{.State.StartedAt}}" 2>$null
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($containerStartedAt)) {
    $arguments += @("--since", $containerStartedAt.Trim())
}
$process = Start-Process `
    -FilePath $python `
    -ArgumentList $arguments `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath `
    -PassThru
$process.Id | Set-Content -LiteralPath $pidPath -Encoding ascii

Start-Sleep -Seconds 2
if ($process.HasExited) {
    Remove-Item -LiteralPath $pidPath -Force -ErrorAction SilentlyContinue
    Write-Host "Collision shadow collector failed to start." -ForegroundColor Red
    if (Test-Path -LiteralPath $stderrPath) {
        Get-Content -LiteralPath $stderrPath -Tail 20
    }
    exit 1
}

Write-Host "Collision shadow collector started (PID $($process.Id))." -ForegroundColor Green
Write-Host "Database: $databasePath"
