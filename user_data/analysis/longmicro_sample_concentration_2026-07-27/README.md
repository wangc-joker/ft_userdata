# LongMicro Sample Concentration

本目录是 2026-07-27 LongMicro 小样本与利润集中度审计的正式归档。输入来自修正后的五年 Micro 逐笔结果和执行成本压力结果，没有修改策略。

## 权威产物

- `sample_concentration_report.md`：完整结论。
- `sample_concentration_summary.csv`：主要统计汇总。
- `sample_bootstrap.csv`：固定 seed `20260727`、20 万次 bootstrap 结果。
- `sample_trade_leaveout.csv`：逐笔剔除结果。
- `sample_group_leaveout.csv`：Pair、年份和退出类型分组剔除结果。
- `sample_top20_micro_trades.csv`：Top20 Micro 交易去重证据。

## 结论

- 五年只有 7 笔、3 胜 4 负；Wilson 95% 胜率区间为 `15.82%-74.95%`。
- 七笔收益和 bootstrap 为正概率为 `89.16%`，但 95% 区间仍为 `-8.36% -> +40.68%`。
- 最佳单笔占净利润 `82.63%`；两笔 ROI 合计 `+107.53 USDT`，其余五笔合计 `-31.27 USDT`。
- BNB 5 笔 `+79.29 USDT`，BTC 2 笔 `-3.03 USDT`；不得从样本内结果反推 BNB-only 规则。
- Top20/max6 与 Positive13/max3 是完全相同的 7 个入场，不属于独立验证。

复现脚本：`user_data/analysis/dualtrend_longmicro_sample_concentration.py`。新样本出现前不再围绕这 7 笔搜索阈值、币种或退出参数。
