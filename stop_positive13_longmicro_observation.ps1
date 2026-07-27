[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$liveContainer = "freqtrade"
$containerName = "freqtrade-positive13-longmicro-observation"
$configName = "config.dryrun.dualtrend.longmicro.positive13.max3.json"
$strategyName = "DualTrendPyramidSecondAdd20LongMicroV1Strategy"

$liveIdBefore = docker --context desktop-linux ps --filter "name=^/$liveContainer$" --format "{{.ID}}"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect live container status."
}

$existing = docker --context desktop-linux ps -a --filter "name=^/$containerName$" --format "{{.Status}}"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect observation container status."
}
if ([string]::IsNullOrWhiteSpace($existing)) {
    Write-Host "Observation container does not exist: $containerName" -ForegroundColor Yellow
    return
}

$containerCommand = docker --context desktop-linux inspect $containerName --format "{{json .Config.Cmd}}"
if (
    $LASTEXITCODE -ne 0 -or
    $containerCommand -notmatch [regex]::Escape($configName) -or
    $containerCommand -notmatch [regex]::Escape($strategyName)
) {
    throw "Refusing to stop a container whose command does not match the LongMicro observation bot."
}

if ($existing -match '^Up ') {
    docker --context desktop-linux stop --timeout 30 $containerName | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to stop LongMicro observation container."
    }
    Write-Host "LongMicro observation container stopped." -ForegroundColor Green
}
else {
    Write-Host "LongMicro observation container is already stopped." -ForegroundColor Yellow
}

$liveIdAfter = docker --context desktop-linux ps --filter "name=^/$liveContainer$" --format "{{.ID}}"
if ($liveIdAfter -ne $liveIdBefore) {
    throw "Safety check failed: live container identity changed while stopping observation."
}
