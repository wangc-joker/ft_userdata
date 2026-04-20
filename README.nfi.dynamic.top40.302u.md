# NFI Dynamic Top40 302U

这套配置基于 `NostalgiaForInfinityX7`，只新增配置文件，不修改旧策略和旧配置。

目标：

- 总资金 `302 USDT`
- 最大持仓 `2`
- 币池 `40`
- 币池来源为 Binance Futures `24h quoteVolume`
- 每次更新时按过滤后的成交额排序取前 `40`
- 若过滤后前部样本不足 `40`，则自动继续顺延补满到 `40`

主要文件：

- 配置模板：
  [config.template.nfi.1y.302u.top40.dynamic.max2.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/config.template.nfi.1y.302u.top40.dynamic.max2.json)
- 动态生成配置：
  [config.backtest.nfi.1y.302u.top40.dynamic.max2.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/config.backtest.nfi.1y.302u.top40.dynamic.max2.json)
- 更新脚本：
  [update_nfi_dynamic_top40_302u.ps1](/D:/test/ft_userdata/update_nfi_dynamic_top40_302u.ps1)
- 双击运行：
  [update_nfi_dynamic_top40_302u.cmd](/D:/test/ft_userdata/update_nfi_dynamic_top40_302u.cmd)

当前默认过滤规则：

- 只保留 `USDT` 本位永续合约
- 只保留 `TRADING`
- 去掉 `*BULL` `*BEAR` `*UP` `*DOWN`
- 去掉明显非目标基础资产：`XAU` `XAG` `XAUT` `PAXG` `TSLA`

说明：

- 当前规则没有额外排除 `1000*` 合约，因为你目前保留的 `Top40` 静态配置里本身包含 `1000SHIB`
- 如果你后面希望把 `1000*` 也排掉，可以继续在更新脚本里加一条规则
- “每周自动更新一次” 这部分已经具备脚本能力；在 Windows 任务计划程序里把这个脚本设成每周执行即可
