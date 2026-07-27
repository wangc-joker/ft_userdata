param(
    [ValidateSet("daily", "weekly", "full")]
    [string]$Mode = "full",
    [string]$Date,
    [string]$StartDate,
    [string]$EndDate
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$database = Join-Path $repoRoot "user_data\tradesv3-positive13-longmicro-observation.sqlite"
$monitor = Join-Path $repoRoot "user_data\analysis\dryrun_monitor.py"

if (-not (Test-Path -LiteralPath $monitor -PathType Leaf)) {
    throw "Dry-run monitor not found: $monitor"
}
if (-not (Test-Path -LiteralPath $database -PathType Leaf)) {
    throw "Observation database not found. Start the observation bot first: start_positive13_longmicro_observation.cmd"
}

$arguments = @(
    "--context", "desktop-linux",
    "compose", "run", "--rm",
    "--entrypoint", "python",
    "freqtrade",
    "/freqtrade/user_data/analysis/dryrun_monitor.py",
    "--mode", $Mode,
    "--db-path", "/freqtrade/user_data/tradesv3-positive13-longmicro-observation.sqlite",
    "--config", "/freqtrade/user_data/config.dryrun.dualtrend.longmicro.positive13.max3.json",
    "--analysis-dir", "/freqtrade/user_data/analysis/longmicro_observation",
    "--output-dir", "/freqtrade/user_data/reports/longmicro_observation",
    "--recommendation-path", "/freqtrade/user_data/reports/longmicro_observation/longmicro_observation_recommendation.md"
)
if ($Date) { $arguments += @("--date", $Date) }
if ($StartDate) { $arguments += @("--start-date", $StartDate) }
if ($EndDate) { $arguments += @("--end-date", $EndDate) }

& docker @arguments
if ($LASTEXITCODE -ne 0) {
    throw "LongMicro observation report generation failed."
}
