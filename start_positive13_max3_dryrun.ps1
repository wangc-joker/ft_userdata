[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$liveContainer = "freqtrade"
$containerName = "freqtrade-positive13-dryrun"
$configName = "config.dryrun.dualtrend.combined.top50.positive13.max3.json"
$configPath = Join-Path $repoRoot "user_data\$configName"
$image = "freqtradeorg/freqtrade:stable"
$baseUrl = "http://127.0.0.1:8085"

if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Dry-run config not found: $configPath"
}

$config = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
if ($config.dry_run -ne $true) {
    throw "Safety check failed: dry_run must be true."
}
if ([int]$config.api_server.listen_port -ne 8085) {
    throw "Safety check failed: dry-run API must use port 8085."
}

$liveIdBefore = docker ps --filter "name=^/$liveContainer$" --format "{{.ID}}"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($liveIdBefore)) {
    throw "Live container '$liveContainer' is not running. Refusing to start the dry-run bot."
}

$existing = docker ps -a --filter "name=^/$containerName$" --format "{{.Status}}"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect dry-run container status."
}

if ([string]::IsNullOrWhiteSpace($existing)) {
    Write-Host "Creating isolated Positive13 dry-run container..." -ForegroundColor Cyan
    docker run -d `
        --name $containerName `
        --restart unless-stopped `
        --cpus 1.0 `
        --memory 1536m `
        --stop-timeout 30 `
        -p "127.0.0.1:8085:8085" `
        -v "${repoRoot}\user_data:/freqtrade/user_data" `
        $image `
        trade `
        --logfile /freqtrade/user_data/logs/freqtrade-positive13-dryrun.log `
        --db-url sqlite:////freqtrade/user_data/tradesv3-positive13-dryrun.sqlite `
        --config "/freqtrade/user_data/$configName" `
        --strategy-path /freqtrade/user_data/strategies `
        --strategy DualTrendCombinedShortPullbackShapeV1Strategy | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create dry-run container."
    }
}
elseif ($existing -notmatch '^Up ') {
    Write-Host "Starting existing Positive13 dry-run container..." -ForegroundColor Cyan
    docker start $containerName | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start existing dry-run container."
    }
}
else {
    Write-Host "Positive13 dry-run container is already running." -ForegroundColor Yellow
}

$liveIdAfter = docker ps --filter "name=^/$liveContainer$" --format "{{.ID}}"
if ($liveIdAfter -ne $liveIdBefore) {
    throw "Safety check failed: live container identity changed during dry-run startup."
}

$authText = "{0}:{1}" -f $config.api_server.username, $config.api_server.password
$authToken = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($authText))
$headers = @{ Authorization = "Basic $authToken" }

Write-Host "Waiting for the dry-run API..." -ForegroundColor Cyan
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
    docker logs $containerName --tail 50 | Out-Host
    throw "Dry-run API did not become ready in time. The live container was not changed."
}

$showConfig = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/api/v1/show_config" -TimeoutSec 10
$whitelist = Invoke-RestMethod -Headers $headers -Uri "$baseUrl/api/v1/whitelist" -TimeoutSec 10
if ($showConfig.runmode -notmatch "dry_run") {
    throw "Safety check failed: API reports runmode '$($showConfig.runmode)'."
}

Write-Host ""
Write-Host "Positive13 Max3 dry-run started safely." -ForegroundColor Green
Write-Host ("Container      : {0}" -f $containerName)
Write-Host ("Strategy       : {0}" -f $showConfig.strategy)
Write-Host ("Run mode       : {0}" -f $showConfig.runmode)
Write-Host ("State          : {0}" -f $showConfig.state)
Write-Host ("Pairs          : {0}" -f $whitelist.length)
Write-Host ("Virtual wallet : {0} USDT" -f $config.dry_run_wallet)
Write-Host "Resource limit : 1 CPU / 1.5 GiB"
Write-Host "Live container : unchanged and running" -ForegroundColor Green
