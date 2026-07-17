# Repository Guide

## DualTrend

开始分析、修改或回测 DualTrend 前，必须先读：

- [`CURRENT_DUALTREND.md`](CURRENT_DUALTREND.md)

该文件是 DualTrend 当前状态的唯一权威入口。仓库中的日期型报告、实验记录和旧配置用于保留研究过程；如果它们对“当前主候选”的描述与该文件冲突，以 `CURRENT_DUALTREND.md` 为准。

不要仅根据配置文件里的 `strategy` 字段、启动脚本名称或某一份旧回测报告判断当前研究主线。回测命令可能显式覆盖配置策略，dry-run 入口也可能暂未升级到研究主候选。

## Other Strategy Families

`user_data/strategies/README.md` 主要记录 Top9 等其他策略族的目录规则。不同策略族的“当前主线”互不覆盖。
