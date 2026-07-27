[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$liveContainer = "freqtrade"
$containerName = "freqtrade-positive13-longmicro-observation"
$configName = "config.dryrun.dualtrend.longmicro.positive13.max3.json"
$configPath = Join-Path $repoRoot "user_data\$configName"
$strategyName = "DualTrendPyramidSecondAdd20LongMicroV1Strategy"
$databaseUrl = "sqlite:////freqtrade/user_data/tradesv3-positive13-longmicro-observation.sqlite"
$image = "freqtradeorg/freqtrade:stable"
$baseUrl = "http://127.0.0.1:8086"
$pythonWarnings = "ignore:Downcasting object dtype arrays on:FutureWarning:freqtrade.strategy.strategy_helper"

docker --context desktop-linux info *> $null
if ($LASTEXITCODE -ne 0) {
    $dockerDesktop = Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe"
    if (-not (Test-Path -LiteralPath $dockerDesktop -PathType Leaf)) {
        throw "Docker Desktop is not running and was not found at: $dockerDesktop"
    }
    Write-Host "Starting Docker Desktop..." -ForegroundColor Cyan
    Start-Process -FilePath $dockerDesktop -WindowStyle Hidden
    $dockerReady = $false
    for ($i = 0; $i -lt 90; $i++) {
        docker --context desktop-linux info *> $null
        if ($LASTEXITCODE -eq 0) {
            $dockerReady = $true
            break
        }
        Start-Sleep -Seconds 2
    }
    if (-not $dockerReady) {
        throw "Docker Desktop did not become ready within 180 seconds."
    }
}

if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Observation config not found: $configPath"
}

$config = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
if ($config.dry_run -ne $true) {
    throw "Safety check failed: dry_run must be true."
}
if ([int]$config.api_server.listen_port -ne 8086) {
    throw "Safety check failed: observation API must use port 8086."
}
if ($config.strategy -ne $strategyName) {
    throw "Safety check failed: config strategy must be $strategyName."
}
if ([int]$config.max_open_trades -ne 3 -or [double]$config.dry_run_wallet -ne 1000) {
    throw "Safety check failed: expected max_open_trades=3 and dry_run_wallet=1000."
}
if ($config.db_url -ne $databaseUrl) {
    throw "Safety check failed: observation database URL changed."
}

$liveIdBefore = docker --context desktop-linux ps --filter "name=^/$liveContainer$" --format "{{.ID}}"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect live container status."
}
$liveWasRunning = -not [string]::IsNullOrWhiteSpace($liveIdBefore)

$portOwner = docker --context desktop-linux ps --format "{{.Names}}|{{.Ports}}" |
    Select-String -Pattern "127.0.0.1:8086->" |
    Where-Object { $_ -notmatch "^$containerName\|" }
if ($portOwner) {
    throw "Safety check failed: localhost port 8086 is already used by another container."
}

$existing = docker --context desktop-linux ps -a --filter "name=^/$containerName$" --format "{{.Status}}"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect observation container status."
}

if ([string]::IsNullOrWhiteSpace($existing)) {
    Write-Host "Creating isolated LongMicro observation container..." -ForegroundColor Cyan
    docker --context desktop-linux run -d `
        --name $containerName `
        --restart unless-stopped `
        --cpus 1.0 `
        --memory 1536m `
        --stop-timeout 30 `
        -e "PYTHONWARNINGS=$pythonWarnings" `
        -p "127.0.0.1:8086:8086" `
        -v "${repoRoot}\user_data:/freqtrade/user_data" `
        $image `
        trade `
        --logfile /freqtrade/user_data/logs/freqtrade-positive13-longmicro-observation.log `
        --db-url $databaseUrl `
        --config "/freqtrade/user_data/$configName" `
        --strategy-path /freqtrade/user_data/strategies `
        --strategy $strategyName | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create LongMicro observation container."
    }
}
else {
    $containerCommand = docker --context desktop-linux inspect $containerName --format "{{json .Config.Cmd}}"
    if (
        $LASTEXITCODE -ne 0 -or
        $containerCommand -notmatch [regex]::Escape($configName) -or
        $containerCommand -notmatch [regex]::Escape($strategyName) -or
        $containerCommand -notmatch [regex]::Escape($databaseUrl)
    ) {
        throw "Existing observation container command does not match the protected config, strategy, and database."
    }
    if ($existing -notmatch '^Up ') {
        Write-Host "Starting existing LongMicro observation container..." -ForegroundColor Cyan
        docker --context desktop-linux start $containerName | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to start existing LongMicro observation container."
        }
    }
    else {
        Write-Host "LongMicro observation container is already running." -ForegroundColor Yellow
    }
}

$liveIdAfter = docker --context desktop-linux ps --filter "name=^/$liveContainer$" --format "{{.ID}}"
if ($liveIdAfter -ne $liveIdBefore) {
    throw "Safety check failed: live container identity changed during observation startup."
}

$authText = "{0}:{1}" -f $config.api_server.username, $config.api_server.password
$authToken = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($authText))
$headers = @{ Authorization = "Basic $authToken" }

Write-Host "Waiting for the LongMicro observation API..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        Invoke-RestMethod -Uri "$baseUrl/api/v1/ping" -TimeoutSec 3 | Out-Null
        $ready = $true
        break
    }
    catch {
        Start-Sleep -Seconds 2
    }
}
if (-not $ready) {
    docker --context desktop-linux logs $containerName --tail 50 | Out-Host
    throw "Observation API did not become ready in time. The live container was not changed."
}

$showConfig = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/api/v1/show_config" -TimeoutSec 10
$whitelist = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/api/v1/whitelist" -TimeoutSec 10
if ($showConfig.runmode -notmatch "dry_run") {
    throw "Safety check failed: API reports runmode '$($showConfig.runmode)'."
}
if ($showConfig.strategy -ne $strategyName) {
    throw "Safety check failed: API reports strategy '$($showConfig.strategy)'."
}
if ([int]$showConfig.max_open_trades -ne 3 -or [int]$whitelist.length -ne 13) {
    throw "Safety check failed: API reports an unexpected slot or pair count."
}

Write-Host ""
Write-Host "LongMicro Positive13 observation started safely." -ForegroundColor Green
Write-Host ("Container      : {0}" -f $containerName)
Write-Host ("Strategy       : {0}" -f $showConfig.strategy)
Write-Host ("Run mode       : {0}" -f $showConfig.runmode)
Write-Host ("State          : {0}" -f $showConfig.state)
Write-Host ("Pairs          : {0}" -f $whitelist.length)
Write-Host ("Virtual wallet : {0} USDT" -f $config.dry_run_wallet)
Write-Host "API            : http://127.0.0.1:8086"
Write-Host "Resource limit : 1 CPU / 1.5 GiB"
$liveState = if ($liveWasRunning) { "unchanged and running" } else { "unchanged and stopped" }
Write-Host ("Live container : {0}" -f $liveState) -ForegroundColor Green
