# NFI 实盘动态 Top40 302U 说明

这份文档说明的是一套“实盘用动态币池”方案。

目标：

- 策略保持不变：`NostalgiaForInfinityX7`
- 资金规模：`302 USDT`
- 最大持仓：`2`
- 币池数量：`40`
- 币池来源：Binance Futures 最新 `24h quoteVolume`
- 更新频率：每周更新一次

这套方案和回测的分工是：

- 回测：优先使用本地已有完整历史数据的固定 `Top40`
- 实盘：使用动态更新的 `Top40`

这样做的原因是：

- 回测需要完整历史数据和稳定可复现的币池
- 实盘更适合跟随当前成交量变化，及时纳入新活跃币种

**相关文件**

- 动态配置模板：
  [config.template.nfi.1y.302u.top40.dynamic.max2.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/config.template.nfi.1y.302u.top40.dynamic.max2.json)
- 动态生成配置：
  [config.backtest.nfi.1y.302u.top40.dynamic.max2.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/config.backtest.nfi.1y.302u.top40.dynamic.max2.json)
- 动态更新脚本：
  [update_nfi_dynamic_top40_302u.ps1](/D:/test/ft_userdata/update_nfi_dynamic_top40_302u.ps1)
- 双击运行脚本：
  [update_nfi_dynamic_top40_302u.cmd](/D:/test/ft_userdata/update_nfi_dynamic_top40_302u.cmd)
- 实盘模板配置：
  [config.live.nfi.dynamic.top40.302u.max2.json](/D:/test/ft_userdata/user_data/config.live.nfi.dynamic.top40.302u.max2.json)
- 实盘 runtime 配置：
  [config.live.nfi.dynamic.top40.302u.max2.runtime.json](/D:/test/ft_userdata/user_data/config.live.nfi.dynamic.top40.302u.max2.runtime.json)
- 实盘启动脚本：
  [start_nfi_dynamic_top40_302u_max2_live.ps1](/D:/test/ft_userdata/start_nfi_dynamic_top40_302u_max2_live.ps1)
- 双击启动：
  [start_nfi_dynamic_top40_302u_max2_live.cmd](/D:/test/ft_userdata/start_nfi_dynamic_top40_302u_max2_live.cmd)
- 状态查看脚本：
  [show_nfi_dynamic_top40_302u_max2_live_status.ps1](/D:/test/ft_userdata/show_nfi_dynamic_top40_302u_max2_live_status.ps1)
- 双击查看状态：
  [show_nfi_dynamic_top40_302u_max2_live_status.cmd](/D:/test/ft_userdata/show_nfi_dynamic_top40_302u_max2_live_status.cmd)
- 最新筛选结果：
  [pairs.dynamic.top40.302u.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/pairs.dynamic.top40.302u.json)
- 最新筛选报告：
  [pairs.dynamic.top40.302u.report.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/pairs.dynamic.top40.302u.report.json)

**配置含义**

当前动态配置包含这些核心参数：

- `dry_run_wallet = 302`
- `max_open_trades = 2`
- `trading_mode = futures`
- `margin_mode = isolated`
- `pairlists = StaticPairList`

这里的关键点是：

- 配置本体是固定格式
- 真正动态变化的是 `exchange.pair_whitelist`
- 每次运行更新脚本后，脚本会重新写入最新的 `40` 个币

**动态更新逻辑**

更新脚本会执行下面这些步骤：

1. 从 Binance Futures 拉取 `exchangeInfo`
2. 从 Binance Futures 拉取 `24hr ticker`
3. 使用 `quoteVolume` 按成交额降序排序
4. 按过滤规则剔除不想要的合约
5. 如果过滤后前面的结果不足 `40`，则继续向后顺延补足到 `40`
6. 将最终币池写入动态配置文件和报告文件

当前的补位规则是：

- 不是“只看最前面 40 个”
- 而是“按成交额排序，从前往后取，过滤不合格的，直到凑满 40 个”

**当前过滤规则**

脚本当前默认保留这些条件：

- 只保留 `USDT` 本位合约
- 只保留 `PERPETUAL`
- 只保留 `TRADING`
- 基础资产名只接受大写字母和数字

脚本当前默认排除这些条件：

- `*BULL`
- `*BEAR`
- `*UP`
- `*DOWN`
- `XAU`
- `XAG`
- `XAUT`
- `PAXG`
- `TSLA`

补充说明：

- 当前没有额外排除 `1000*` 合约
- 这是有意保留的，因为你之前保留的静态 `Top40` 里本来就包含这类币
- 如果后面你希望实盘也排除 `1000*`，可以继续在脚本里新增一条过滤条件

**每周自动更新怎么做**

目前脚本能力已经具备，自动化执行只差 Windows 任务计划程序。

推荐做法：

1. 每周固定时间运行：
   [update_nfi_dynamic_top40_302u.cmd](/D:/test/ft_userdata/update_nfi_dynamic_top40_302u.cmd)
2. 运行后自动刷新：
   - 动态配置文件
   - 最新 40 币名单
   - 报告文件

建议更新时间：

- 每周一北京时间早上
- 或者你准备重启/更新实盘 bot 之前先执行一次

**实盘使用建议**

如果你准备把这套方案接到真实实盘，建议按这个顺序操作：

1. 先运行动态更新脚本，生成最新 40 币名单
2. 检查：
   [pairs.dynamic.top40.302u.report.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/pairs.dynamic.top40.302u.report.json)
3. 启动：
   [start_nfi_dynamic_top40_302u_max2_live.cmd](/D:/test/ft_userdata/start_nfi_dynamic_top40_302u_max2_live.cmd)
4. 需要查看状态时，运行：
   [show_nfi_dynamic_top40_302u_max2_live_status.cmd](/D:/test/ft_userdata/show_nfi_dynamic_top40_302u_max2_live_status.cmd)

这样做的好处是：

- 你每次都知道这周实际跑的是哪 40 个币
- 如果某次筛到了你不想交易的新币，可以先人工拦一下

**和回测版的区别**

这套动态币池不适合直接拿来做长期回测，原因是：

- 动态币池里会混入新上市币种
- 本地可能没有完整历史数据
- 某些币可能缺杠杆档位或 funding/mark 数据

所以当前建议是：

- 回测使用本地固定币池：
  [config.backtest.nfi.1y.302u.top40.local.max2.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/config.backtest.nfi.1y.302u.top40.local.max2.json)
- 实盘使用动态币池：
  [config.backtest.nfi.1y.302u.top40.dynamic.max2.json](/D:/test/ft_userdata/user_data/tests/nfi_top_volume_3y_1000u/config.backtest.nfi.1y.302u.top40.dynamic.max2.json)

**当前状态**

目前已经完成：

- 动态更新脚本已可执行
- 动态配置已可自动生成
- 最新 `Top40` 币池已写入配置文件

目前已经补全：

- 独立的 `live` 模板配置
- 独立的 `runtime` 配置输出路径
- 启动脚本
- 状态查看脚本

启动脚本会自动做这几件事：

1. 先刷新动态 `Top40`
2. 将最新币池写入实盘配置
3. 从现有 runtime 配置复制交易所 key/secret
4. 生成新的实盘 runtime 配置
5. 启动 Docker 实盘 bot
