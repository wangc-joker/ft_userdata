# LongV1ConfirmStrong Dry-run 与资金槽位最终建议

生成时间：2026-06-16  
目标：不继续大范围调参，只做 dry-run 准备、剔除 ZEC 验证、side-specific slot 方案验证。

## 1. 新增配置文件

### Long dry-run 配置

- A 版（推荐观察）：[config.dryrun.dualtrend.long_confirmstrong_roi5.A_bnb_doge_xrp.json](D:/test/ft_userdata/user_data/config.dryrun.dualtrend.long_confirmstrong_roi5.A_bnb_doge_xrp.json)
- B 版（含 ZEC 对照）：[config.dryrun.dualtrend.long_confirmstrong_roi5.B_bnb_doge_xrp_zec.json](D:/test/ft_userdata/user_data/config.dryrun.dualtrend.long_confirmstrong_roi5.B_bnb_doge_xrp_zec.json)

两版均为 `LongV1ConfirmStrongRoi5Strategy`，只启用 `long_pullback_restart`，ROI 5%，关闭 compression long、快速跌回退出、分批止盈、补仓和 DCA。dry-run 默认 `max_open_trades=1`。

### Side-specific 双 bot 配置

- Short bot: [config.dryrun.dualtrend.short_pullback.side_slots.max3.json](D:/test/ft_userdata/user_data/config.dryrun.dualtrend.short_pullback.side_slots.max3.json)
- Long bot: [config.dryrun.dualtrend.long_confirmstrong_roi5.side_slots.max1.json](D:/test/ft_userdata/user_data/config.dryrun.dualtrend.long_confirmstrong_roi5.side_slots.max1.json)

Freqtrade 单策略没有天然的 long/short 分侧仓位池。要实现 “Short 最大 3 仓，Long 最大 1 仓，Long 不挤占 Short 仓位”，最干净方案是双 bot、双配置、独立 dry-run wallet/资金预算。

## 2. 剔除 ZEC 回测结果

| 版本 | 样本 | Trades | 收益U | 收益% | PF | MaxDD% | Winrate% | Rejected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A no-ZEC | 全样本 | 7 | 38.96 | 3.90 | 4.36 | 0.77 | 71.43 | 0 |
| B with ZEC | 全样本 | 10 | 35.33 | 3.53 | 2.28 | 0.80 | 60.00 | 0 |
| A no-ZEC | 近期 | 2 | 2.39 | 0.24 | 1.31 | 0.77 | 50.00 | 0 |
| B with ZEC | 近期 | 2 | 2.39 | 0.24 | 1.31 | 0.77 | 50.00 | 0 |

剔除 ZEC 后，全样本从 10 笔降为 7 笔，但收益从 35.33U 提高到 38.96U，PF 从 2.28 提高到 4.36，MaxDD 从 0.80% 降到 0.77%。近期两版结果相同，因为近期没有 ZEC 交易。

## 3. 成本压力测试：no-ZEC A 版

| 压力 | Trades | 收益U | 收益% | PF | MaxDD% | Winrate% |
| --- | --- | --- | --- | --- | --- | --- |
| 基准 | 7 | 38.96 | 3.90 | 4.36 | 0.77 | 71.43 |
| 手续费1.5倍 | 7 | 38.75 | 3.88 | 4.29 | 0.78 | 71.43 |
| 手续费2倍 | 7 | 38.58 | 3.86 | 4.22 | 0.79 | 71.43 |
| 滑点0.05% | 7 | 37.55 | 3.75 | 4.14 | 逐笔模拟 | 71.43 |
| 滑点0.10% | 7 | 36.14 | 3.61 | 3.92 | 逐笔模拟 | 71.43 |

费用与滑点压力下仍保持正收益。手续费 2 倍后 PF 4.22；0.10% 双边滑点模拟后 PF 约 3.88。低频确认版对交易成本不敏感。

## 4. no-ZEC 拆解

### 全样本按年份

| Year | Trades | 收益U | PF |
| --- | --- | --- | --- |
| 31/12/2023 | 3 | 15.80 | 5.47 |
| 31/12/2024 | 2 | 20.67 | 0.00 |
| 31/12/2025 | 2 | 2.48 | 1.31 |

### 全样本按 pair

| Pair | Trades | 收益U | 收益% | PF | Winrate% |
| --- | --- | --- | --- | --- | --- |
| DOGE/USDT:USDT | 2 | 19.34 | 1.93 | 0.00 | 100.00 |
| BNB/USDT:USDT | 3 | 17.13 | 1.71 | 5.85 | 66.67 |
| XRP/USDT:USDT | 2 | 2.48 | 0.25 | 1.31 | 50.00 |

### 全样本按月份（仅有交易月份）

| Month | Trades | 收益U | PF |
| --- | --- | --- | --- |
| 28/02/2023 | 1 | -3.54 | 0.00 |
| 31/12/2023 | 2 | 19.34 | 0.00 |
| 29/02/2024 | 1 | 12.37 | 0.00 |
| 31/03/2024 | 1 | 8.29 | 0.00 |
| 31/07/2025 | 1 | 10.53 | 0.00 |
| 30/09/2025 | 1 | -8.05 | 0.00 |

### 近期按年份

| Year | Trades | 收益U | PF |
| --- | --- | --- | --- |
| 31/12/2025 | 2 | 2.39 | 1.31 |

### 近期按 pair

| Pair | Trades | 收益U | 收益% | PF | Winrate% |
| --- | --- | --- | --- | --- | --- |
| XRP/USDT:USDT | 2 | 2.39 | 0.24 | 1.31 | 50.00 |

### 近期按月份（仅有交易月份）

| Month | Trades | 收益U | PF |
| --- | --- | --- | --- |
| 31/07/2025 | 1 | 10.16 | 0.00 |
| 30/09/2025 | 1 | -7.77 | 0.00 |

## 5. Side-specific Slot 验证

| 方案 | 样本 | Short trades | Long trades | 总Trades | 收益U | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| 单策略合并 | 全样本 | 323 | 10 | 333 | 1202.49 | 共用 max_open_trades=3，long 会挤占 short |
| 双 bot 独立槽位 | 全样本 | 337 | 7 | 344 | 1046.01 | Short max3 + Long max1，收益为独立回测相加 |
| 单策略合并 | 近期 | 164 | 2 | 166 | 481.42 | 共用 max_open_trades=3 |
| 双 bot 独立槽位 | 近期 | 169 | 2 | 171 | 380.06 | Short max3 + Long max1，收益为独立回测相加 |

解释：单策略合并虽然收益提升，但它会改变 short 成交顺序，并减少 short 成交数。双 bot 方案下，long 不挤占 short 仓位，结果更符合“Short 3 仓 + Long 1 仓”的真实意图。

## 6. 最终建议

- Long 是否适合独立 dry-run：适合，但只建议 A 版 BNB/DOGE/XRP，`max_open_trades=1`，先观察信号质量和实盘挂单/滑点，不建议扩大仓位。
- 是否保留 ZEC：不建议保留。ZEC 在全样本拖累收益和 PF，剔除后结果更干净；近期没有额外贡献。
- 是否应该和 Short 合并：暂时不建议单策略硬合并。合并会让 long 挤占 short 资金槽位，导致结果解释不干净。
- 如果合并，是否必须独立资金槽位：必须。推荐用双 bot 方案实现 side-specific slots：short bot max3，long bot max1。这样 long 的观察不会污染 short 主策略的仓位分配。
