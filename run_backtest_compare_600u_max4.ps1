# NFI vs FreqAI 回测对比脚本
# 600U 资金，最大开仓 4，30 币种，半年数据

$ErrorActionPreference = "Continue"
$StartTime = Get-Date

# 设置路径
$FtUserdata = "d:\test\ft_userdata"
$NFIRoot = "d:\test\NostalgiaForInfinity"
$NFIAlphaRoot = "d:\test\nfi-alpha-strategy\strategies"
$ResultsDir = "$FtUserdata\user_data\backtest_results\compare_600u_max4"

# 创建结果目录
if (!(Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null
}
New-Item -ItemType Directory -Path "$ResultsDir\nfi_baseline" -Force | Out-Null
New-Item -ItemType Directory -Path "$ResultsDir\freqai_nfi" -Force | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NFI vs FreqAI 回测对比 - 600U Max4" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始时间: $StartTime"
Write-Host ""

# 回测参数
$Timerange = "20231101-20260501"  # 半年数据

# 1. 回测 NFI 基础版
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host "[1/2] 开始回测: NFI 基础版 (NostalgiaForInfinityX7)" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$NFIConfig = "$FtUserdata\user_data\config.backtest.nfi.baseline.600u.max4.halfyear.json"
$NFIResultFile = "$ResultsDir\nfi_baseline\trades.json"

Set-Location $NFIRoot
& python freqtrade backtesting `
    --config $NFIConfig `
    --strategy NostalgiaForInfinityX7 `
    --timerange $Timerange `
    --backtest-result-mode summary `
    --export trades `
    --export-filename $NFIResultFile 2>&1 | Tee-Object -Variable nfiOutput

Write-Host "NFI 基础版回测完成" -ForegroundColor Green

# 2. 回测 FreqAI 版本
Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host "[2/2] 开始回测: FreqAI 版本 (NFIFreqAIFilterStrategy)" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$FreqAIConfig = "$FtUserdata\user_data\config.backtest.freqai.nfi.600u.max4.halfyear.json"
$FreqAIResultFile = "$ResultsDir\freqai_nfi\trades.json"

Set-Location $NFIAlphaRoot
& python -m freqtrade backtesting `
    --config $FreqAIConfig `
    --strategy NFIFreqAIFilterStrategy `
    --timerange $Timerange `
    --backtest-result-mode summary `
    --export trades `
    --export-filename $FreqAIResultFile 2>&1 | Tee-Object -Variable freqaiOutput

Write-Host "FreqAI 版本回测完成" -ForegroundColor Green

# 3. 保存原始输出
$global:nfiOutput | Out-File -FilePath "$ResultsDir\nfi_baseline_output.log" -Encoding UTF8
$global:freqaiOutput | Out-File -FilePath "$ResultsDir\freqai_nfi_output.log" -Encoding UTF8

# 4. 生成对比报告
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "回测完成，结果已保存" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "结果目录: $ResultsDir"
Write-Host ""
Write-Host "请查看以下文件获取详细结果:" -ForegroundColor Yellow
Write-Host "  - $ResultsDir\nfi_baseline_output.log (NFI基础版)"
Write-Host "  - $ResultsDir\freqai_nfi_output.log (FreqAI版)"
Write-Host "  - $ResultsDir\comparison_report.md (对比报告)"
Write-Host ""
Write-Host "总耗时: $(((Get-Date) - $StartTime).TotalMinutes.ToString('F1')) 分钟"