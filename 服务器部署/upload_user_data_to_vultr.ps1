param(
    [Parameter(Mandatory = $true)][string]$ServerIp,
    [Parameter(Mandatory = $true)][string]$ServerUser,
    [Parameter(Mandatory = $true)][string]$LocalUserDataPath,
    [string]$RemotePath = "/root/user_data.tar.gz"
)

# 说明：
# 1. 在 Windows 11 PowerShell 中运行本脚本。
# 2. 依赖系统自带 OpenSSH（scp.exe）。
# 3. 该脚本会把你的本地 user_data 目录打包成 user_data.tar.gz，然后上传到服务器。

if (-not (Test-Path $LocalUserDataPath)) {
    Write-Error "本地目录不存在: $LocalUserDataPath"
    exit 1
}

$LocalUserDataPath = (Resolve-Path $LocalUserDataPath).Path
$ParentDir = Split-Path $LocalUserDataPath -Parent
$FolderName = Split-Path $LocalUserDataPath -Leaf
$TarFile = Join-Path $env:TEMP "user_data.tar.gz"

if (Test-Path $TarFile) {
    Remove-Item $TarFile -Force
}

Write-Host "正在打包 $LocalUserDataPath ..."
tar -czf $TarFile -C $ParentDir $FolderName
if ($LASTEXITCODE -ne 0) {
    Write-Error "打包失败"
    exit 1
}

Write-Host "上传到 $ServerUser@$ServerIp:$RemotePath ..."
scp $TarFile "$ServerUser@$ServerIp`:$RemotePath"
if ($LASTEXITCODE -ne 0) {
    Write-Error "上传失败"
    exit 1
}

Write-Host "上传完成。接下来在服务器执行："
Write-Host "sudo bash deploy_freqtrade_vultr.sh --bot-name ftbot --strategy-class 你的策略类名 --config-file config.json --import-tar $RemotePath"
