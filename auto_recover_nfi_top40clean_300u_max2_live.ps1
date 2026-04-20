[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$clashExePath = "D:\software\Clash.for.Windows-0.20.15-win\Clash for Windows.exe"
$dockerDesktopExePath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
$startScriptPath = Join-Path $repoRoot "start_nfi_top40clean_300u_max2_live.ps1"
$logPath = Join-Path $repoRoot "user_data\logs\auto_recover_nfi_top40clean_300u_max2_live.log"
$baseUrl = "http://127.0.0.1:8084"
$apiUser = "Freqtrader"
$apiPassword = "NfiTop40Live!2026"

function Write-Log {
    param(
        [string]$Message
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[{0}] {1}" -f $timestamp, $Message
    Write-Host $line
    Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
}

function Test-DockerReady {
    try {
        & docker version *> $null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

function Test-BotRunning {
    try {
        $auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $apiUser, $apiPassword)))
        $headers = @{ Authorization = "Basic $auth" }
        $config = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/api/v1/show_config" -TimeoutSec 5
        return ($config.state -eq "running")
    }
    catch {
        return $false
    }
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $logPath) | Out-Null
Write-Log "Auto recovery started."

if (Test-BotRunning) {
    Write-Log "Bot is already running. No action needed."
    exit 0
}

if (-not (Test-Path -LiteralPath $clashExePath -PathType Leaf)) {
    throw "Clash executable not found: $clashExePath"
}

if (-not (Get-Process | Where-Object { $_.ProcessName -like "Clash*" })) {
    Write-Log "Starting Clash for Windows."
    Start-Process -FilePath $clashExePath | Out-Null
    Start-Sleep -Seconds 12
}
else {
    Write-Log "Clash for Windows is already running."
}

if (-not (Test-DockerReady)) {
    if (-not (Test-Path -LiteralPath $dockerDesktopExePath -PathType Leaf)) {
        throw "Docker Desktop executable not found: $dockerDesktopExePath"
    }

    if (-not (Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue)) {
        Write-Log "Starting Docker Desktop."
        Start-Process -FilePath $dockerDesktopExePath | Out-Null
    }
    else {
        Write-Log "Docker Desktop process is already running."
    }

    Write-Log "Waiting for Docker engine to become ready."
    $dockerReady = $false
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 5
        if (Test-DockerReady) {
            $dockerReady = $true
            break
        }
    }

    if (-not $dockerReady) {
        throw "Docker engine did not become ready in time."
    }
}
else {
    Write-Log "Docker engine is already ready."
}

if (Test-BotRunning) {
    Write-Log "Bot became available during recovery checks. No restart needed."
    exit 0
}

if (-not (Test-Path -LiteralPath $startScriptPath -PathType Leaf)) {
    throw "Start script not found: $startScriptPath"
}

Write-Log "Starting freqtrade live bot."
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $startScriptPath 2>&1 |
    Tee-Object -FilePath $logPath -Append | Out-Host

Start-Sleep -Seconds 5

if (Test-BotRunning) {
    Write-Log "Recovery completed successfully."
    exit 0
}

throw "Recovery script finished, but the bot is not in running state."
