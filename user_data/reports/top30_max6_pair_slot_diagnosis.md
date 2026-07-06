# Top30 max6 Pair / Slot Diagnosis

生成时间：2026-06-30

## 分析对象

- 策略：`DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy`
- 方案：`Top30 + max_open_trades=6`
- 三年样本：`2023-06-18 -> 2026-05-08`
- 近一年样本：`2025-06-18 -> 2026-05-08`
- 参考基准：此前已验证的 `Positive13 + max_open_trades=3`

## 1. 核心结论

1. `Top30 + max6` 的收益提升是真实的：三年 `141.04%`，近一年 `36.85%`，都高于 `Positive13 + max3`。
2. 但它不是靠“30 个币一起发力”得到的，而是靠少数强贡献币 + 更宽槽位把更多单接住。
3. 三年样本里，开仓时已有 `3` 仓及以上的额外槽位单共有 `41` 笔，贡献利润 `158.70 USDT`。
4. 近一年样本里，额外槽位单共有 `25` 笔，贡献利润 `61.24 USDT`。
5. 真正多赚的钱仍集中在核心强币和少数新增有效币上，很多新增币只是挂名在池子里。

## 2. Pair 贡献

### 三年样本：主要正贡献

- `ETH/USDT:USDT`: `228.35 USDT`, `33` trades
- `BNB/USDT:USDT`: `218.50 USDT`, `22` trades
- `XRP/USDT:USDT`: `200.40 USDT`, `40` trades
- `BTC/USDT:USDT`: `189.64 USDT`, `38` trades
- `ADA/USDT:USDT`: `156.37 USDT`, `33` trades
- `ZEC/USDT:USDT`: `153.05 USDT`, `14` trades
- `DOGE/USDT:USDT`: `143.19 USDT`, `26` trades
- `TRX/USDT:USDT`: `90.93 USDT`, `34` trades

### 三年样本：主要拖累

- `SUI/USDT:USDT`: `-28.63 USDT`, `23` trades
- `LINK/USDT:USDT`: `-10.23 USDT`, `26` trades
- `FIL/USDT:USDT`: `-10.16 USDT`, `1` trades
- `SOL/USDT:USDT`: `-9.87 USDT`, `29` trades
- `APE/USDT:USDT`: `-8.51 USDT`, `1` trades
- `LTC/USDT:USDT`: `-7.56 USDT`, `3` trades
- `LDO/USDT:USDT`: `-7.41 USDT`, `2` trades
- `BCH/USDT:USDT`: `-0.23 USDT`, `2` trades

三年样本零成交币：`HYPE/USDT:USDT, AAVE/USDT:USDT, ONDO/USDT:USDT, WLD/USDT:USDT, DASH/USDT:USDT, UNI/USDT:USDT, ARB/USDT:USDT, APT/USDT:USDT, ICP/USDT:USDT, CRV/USDT:USDT`

### 近一年样本：主要正贡献

- `BNB/USDT:USDT`: `92.31 USDT`, `10` trades
- `ETH/USDT:USDT`: `64.24 USDT`, `13` trades
- `TRX/USDT:USDT`: `57.74 USDT`, `13` trades
- `TAO/USDT:USDT`: `44.47 USDT`, `11` trades
- `XRP/USDT:USDT`: `39.64 USDT`, `17` trades
- `ZEC/USDT:USDT`: `24.67 USDT`, `2` trades
- `BTC/USDT:USDT`: `24.28 USDT`, `12` trades
- `NEAR/USDT:USDT`: `21.66 USDT`, `15` trades

### 近一年样本：主要拖累

- `SOL/USDT:USDT`: `-23.04 USDT`, `11` trades
- `SUI/USDT:USDT`: `-15.58 USDT`, `9` trades
- `BCH/USDT:USDT`: `-0.15 USDT`, `1` trades
- `LTC/USDT:USDT`: `-0.01 USDT`, `1` trades

近一年样本零成交币：`HYPE/USDT:USDT, AVAX/USDT:USDT, FIL/USDT:USDT, AAVE/USDT:USDT, APE/USDT:USDT, DOT/USDT:USDT, ONDO/USDT:USDT, WLD/USDT:USDT, DASH/USDT:USDT, UNI/USDT:USDT, ARB/USDT:USDT, APT/USDT:USDT, ICP/USDT:USDT, CRV/USDT:USDT, LDO/USDT:USDT`

观察：

- `ETH/BNB/XRP/BTC/ADA/ZEC/DOGE` 依然是核心利润柱子。
- `TRX` 在大池子里确实新增了有效正贡献。
- 很多新增币长期接近 `0 trade`，说明它们没有真正进入策略主战场。
- `SOL/SUI/LINK` 依然是老拖累项，新增币没有自动解决这个问题。

## 3. 槽位竞争

### 三年样本

- 时间上，组合处于 `>=3` 仓状态约 `4.70%`。
- 处于 `>=5` 仓状态约 `0.42%`。
- 刚好满 `6` 仓状态约 `0.04%`。
- 开仓时已有 `3` 仓及以上的额外槽位单：`41` 笔，胜率 `53.66%`，利润 `158.70 USDT`。

### 近一年样本

- 时间上，组合处于 `>=3` 仓状态约 `7.16%`。
- 处于 `>=5` 仓状态约 `1.24%`。
- 刚好满 `6` 仓状态约 `0.15%`。
- 开仓时已有 `3` 仓及以上的额外槽位单：`25` 笔，胜率 `60.00%`，利润 `61.24 USDT`。

判断：

- 额外槽位不是纯噪音，因为它们整体仍然贡献正收益。
- 但这些额外利润并没有分散来自很多新增币，而是集中在少数真正能打的 pair 上。
- 所以 `max6` 的主要价值是“别让好机会被卡在门外”，不是“更多币自动带来更多 alpha”。

### 额外槽位利润集中在哪些 pair

三年样本：

- `BNB/USDT:USDT`: `3` extra-slot trades, `88.74 USDT`
- `BTC/USDT:USDT`: `6` extra-slot trades, `71.72 USDT`
- `DOGE/USDT:USDT`: `3` extra-slot trades, `28.73 USDT`
- `LINK/USDT:USDT`: `2` extra-slot trades, `18.36 USDT`
- `NEAR/USDT:USDT`: `3` extra-slot trades, `14.14 USDT`
- `ZEC/USDT:USDT`: `1` extra-slot trades, `0.06 USDT`
- `TAO/USDT:USDT`: `1` extra-slot trades, `0.00 USDT`
- `SUI/USDT:USDT`: `3` extra-slot trades, `-0.14 USDT`

近一年样本：

- `BNB/USDT:USDT`: `2` extra-slot trades, `49.50 USDT`
- `LINK/USDT:USDT`: `1` extra-slot trades, `11.58 USDT`
- `NEAR/USDT:USDT`: `3` extra-slot trades, `7.98 USDT`
- `BTC/USDT:USDT`: `5` extra-slot trades, `5.87 USDT`
- `SOL/USDT:USDT`: `2` extra-slot trades, `1.89 USDT`
- `ETH/USDT:USDT`: `2` extra-slot trades, `0.11 USDT`
- `ZEC/USDT:USDT`: `1` extra-slot trades, `0.03 USDT`
- `TAO/USDT:USDT`: `1` extra-slot trades, `0.00 USDT`

观察：

- 三年额外槽位利润主要集中在 `BNB/BTC/DOGE/LINK/NEAR` 这些币上。
- 近一年额外槽位利润更集中，主要还是 `BNB/LINK/NEAR/BTC`。
- 这再次说明：槽位放大有价值，但新增价值不是均匀来自整个 30 币池。

## 4. 最值得继续看的方向

1. 保留 `Top30 + max6` 作为容量支线，但不要直接当最终主线。
2. 从 30 币池里删掉长期零成交或持续负贡献的币，做一个 `Top18-24 + max6`。
3. 重点保留：共享核心强币，以及 `TRX` 这种在大池里确实新增正贡献的币。
4. 重点审查：`SOL/SUI/LINK` 这些老拖累，以及 `FIL/APE/LDO/LTC` 这类新增但没有证明自己价值的币。

## 5. Top24 + max6 候选回测

基于上面的拆解，先做了一版偏保守的 `Top24 + max6`：

- 删除了长期零成交的 `HYPE/AAVE/ONDO/WLD/DASH/UNI`
- 保留核心强币
- 保留 `TRX`
- 暂时保留 `PAXG`
- 对 `SOL/SUI/LINK` 这些老拖累先不单独手工裁掉，先看“只删无效币”后的自然结果

### 三年样本

区间：

`2023-06-18 -> 2026-05-08`

| 方案 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| Positive13 + max3 | 313 | 131.59% / 1315.886 | 2.13 | 5.77% | 49.5% |
| Top30 + max6 | 381 | 141.04% / 1410.411 | 2.03 | 5.18% | 47.2% |
| Top24 + max6 | 383 | 149.07% / 1490.680 | 2.08 | 5.14% | 47.3% |

结论：

- 相比 `Top30 + max6`：
  - 收益继续提升：`141.04% -> 149.07%`
  - PF 回升：`2.03 -> 2.08`
  - MaxDD 小幅继续改善：`5.18% -> 5.14%`
  - 胜率基本持平：`47.2% -> 47.3%`

这说明：

- 之前那批长期不出手的币，确实不是“备胎 alpha”；
- 删掉之后并没有伤容量，反而净化了组合。

### 近一年样本

区间：

`2025-06-18 -> 2026-05-08`

| 方案 | Trades | Profit | PF | MaxDD | Winrate |
|---|---:|---:|---:|---:|---:|
| Positive13 + max3 | 114 | 34.84% / 348.423 | 2.30 | 4.84% | 54.4% |
| Top30 + max6 | 140 | 36.85% / 368.527 | 2.18 | 4.43% | 52.1% |
| Top24 + max6 | 141 | 41.51% / 415.131 | 2.32 | 4.43% | 51.8% |

结论：

- 相比 `Top30 + max6`：
  - 收益明显提升：`36.85% -> 41.51%`
  - PF 也提升：`2.18 -> 2.32`
  - MaxDD 持平：`4.43%`
  - 胜率略低一点：`52.1% -> 51.8%`

但整体看：

- `Top24 + max6` 已经不只是“总收益更高”；
- 它连 PF 都重新抬回到和 `Positive13 + max3` 接近甚至略高的水平。

### 当前阶段结论更新

到这一步，路线已经比前一轮清楚很多：

1. `Top30 + max6` 证明了“容量放大”是有效的；
2. `Top24 + max6` 进一步证明：
   - 不是币越多越好；
   - 删除长期无效币后，可以同时提升收益与质量；
3. 当前最值得继续推进的容量主候选，已经从 `Top30 + max6` 切换到：

`Top24 + max6`

## 当前建议

下一步最合理的是：

1. 以 `Top24 + max6` 作为新候选主线；
2. 再做一轮更细的 pair 剪枝：
   - 优先复核 `SOL/SUI/LINK`
   - 以及 `APE/LTC/LDO/BCH/AVAX` 这类弱贡献币
3. 尝试做一个 `Top18-20 + max6`，验证是否还能继续提升 PF，同时不伤收益。

## 输出文件

- Pair 贡献明细：`D:\test\ft_userdata\user_data\analysis\top30_max6_pair_contribution.csv`
- 槽位竞争明细：`D:\test\ft_userdata\user_data\analysis\top30_max6_slot_competition.csv`
- 额外槽位 pair 明细：`D:\test\ft_userdata\user_data\analysis\top30_max6_extra_slot_pairs.csv`
