# SecondAdd15 盈利单二次加仓实验

## 结论

本轮有效候选是 `DualTrendPyramidSecondAdd15V1Strategy`。

它在 `DualTrendPyramidCloseFloor07V1Strategy` 的基础上，只做一件事：允许 `short_pullback_restart` 盈利单在已有第一腿加仓后，再出现同方向信号时做第二腿加仓。第一腿仍是初始仓位 `25%`，第二腿降为初始仓位 `15%`，第二腿触发窗口提高到 `1.8% - 3.5%` 浮盈。

这个版本没有修改入场逻辑、没有改币池、没有改 `max_open_trades`、没有改止损或止盈主逻辑。

## 回测对照

### 3 年 `20230618-20260618`

- CloseFloor07: `195.02% / PF 2.658 / MaxDD(account) 4.82% / Win 51.27% / 314 trades`
- SecondAdd15: `198.33% / PF 2.677 / MaxDD(account) 4.82% / Win 51.27% / 314 trades`
- 增量：`+3.31%`，PF 小幅提升，账户回撤不变。

### 近 1 年 `20250618-20260618`

- CloseFloor07: `67.56% / PF 3.379 / MaxDD(account) 4.75% / Win 56.1% / 123 trades`
- SecondAdd15: `68.01% / PF 3.396 / MaxDD(account) 4.75% / Win 56.1% / 123 trades`

### 压力期 `20260301-20260531`

- CloseFloor07: `4.82% / PF 2.957 / MaxDD(account) 1.75% / Win 40.0% / 15 trades`
- SecondAdd15: `5.12% / PF 3.087 / MaxDD(account) 1.75% / Win 46.67% / 15 trades`

### 真实 5 年 `20210618-20260618`

- CloseFloor07: `250.64% / PF 2.383 / MaxDD(account) 4.82% / Win 51.36% / 477 trades`
- SecondAdd15: `252.37% / PF 2.386 / MaxDD(account) 4.81% / Win 51.36% / 477 trades`
- 增量：`+1.73%`。

## 加仓行为

- 3 年 SecondAdd15 的二次加仓交易数：`11`。
- 5 年 SecondAdd15 的二次加仓交易数：`20`。
- 3 年 `short_pullback_restart` 收益从 `107.17%` 提到 `110.01%`。
- 5 年 `short_pullback_restart` 收益从 `151.23%` 提到 `152.91%`。

## 判断

- 第二腿加仓是有效的，但属于“小幅增强”，不是收益结构的大改造。
- 它没有放大压力期回撤，5 年也略微跑赢 CloseFloor07，因此可以保留为当前加仓主候选。
- `SecondAdd12` 和 `SecondAdd12Confirm` 没有提供额外优势，已从策略代码中删除。
- 这条线下一步更值得研究的是“第二腿触发后的坏加仓识别”，而不是继续提高第二腿仓位。

## 输出文件

- 汇总：`user_data/analysis/pyramid_second_add_2026-07-13/second_add15_summary.csv`
- 逐笔差异：`user_data/analysis/pyramid_second_add_2026-07-13/second_add15_trade_delta.csv`
- pair 差异：`user_data/analysis/pyramid_second_add_2026-07-13/second_add15_pair_delta.csv`
