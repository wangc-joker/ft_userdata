"""
NFIAIWrapperStrategy - NFI + AI 优化版策略 v0.2.0

v0.2.0 更新（基于 Battle/v2 方案）：
- 三层防线架构：硬风控 → AI 辅助 → NFI 原版
- 硬风控不可绕过：-8% 最大亏损 / -3%+24h / -1.5%+48h / 低效单 72h
- AI 双 target：future_return + future_drawdown
- AI 坏单退出需要高周期（4h）EMA 趋势确认
- 入场过滤区分 NFI 强信号和弱信号
- custom_stoploss() 只做盈利保护，不承担强制退出
- 小亏损保护真正生效（需 AI 确认）
- 修复 _get_holding_bars() 使用 trade.closed_date 的 bug

基于文档设计：
- NFIAIWrapperStrategy_最终修改方案_v2.md
- NFIAIWrapperStrategy_Battle修改方案.md

AI 角色：仅过滤，不生成信号
关闭 AI：移除 config 中的 freqai.enabled 即可回退到纯 NFI + 硬风控 行为
"""

import logging
from functools import reduce

import talib.abstract as ta
import pandas as pd
from pandas import DataFrame

# 继承 NFI X7 原版，保持核心逻辑不变
from NostalgiaForInfinityX7 import NostalgiaForInfinityX7


log = logging.getLogger(__name__)


class NFIAIWrapperStrategy(NostalgiaForInfinityX7):
    """
    NFI + AI Wrapper 策略

    层级架构：
    1. NFI 原版 (5m) - 买入/卖出信号生成
    2. FreqAI 过滤层 (1h/4h) - 入场过滤、坏单识别
    3. 模块化风控层 - 动态止损/止盈、时间止损、盈利保护
    """

    # ============================================================
    # FreqAI 配置
    # ============================================================

    # freqai.feature_parameters 中配置了 include_timeframes: ["5m", "1h", "4h"]
    # 本策略自动利用这些多周期数据进行特征工程

    # ============================================================
    # 第一层：硬风控参数（不可绕过，不依赖 AI）
    # ============================================================

    # 最大亏损硬退出 — 第一版先用 -8%，回测验证后再考虑 -5%
    max_drawdown_threshold = -0.08  # -8%

    # 严重亏损 + 24h 退出
    loss_time_exit_bars_1 = 288   # 288 * 5m = 24h
    loss_time_profit_1 = -0.03    # 亏损超过 -3%

    # 中等亏损 + 48h 退出
    loss_time_exit_bars_2 = 576   # 576 * 5m = 48h
    loss_time_profit_2 = -0.015   # 亏损超过 -1.5%

    # 低效单 + 72h 退出（持仓很久却没有多少利润）
    stale_time_exit_bars = 864    # 864 * 5m = 72h
    stale_profit_threshold = 0.005  # 72h 还没赚到 0.5%，退出

    # ============================================================
    # 第二层：AI 辅助参数（需要 AI + 高周期双重确认）
    # ============================================================

    # AI 坏单退出最低观察期（避免刚开仓就被 AI 误杀）
    ai_exit_min_bars = 144  # 12h

    # AI 认为反弹空间不足的阈值
    ai_bad_return_max = 0.008   # 预测窗口最高收益低于 0.8%

    # AI 认为回撤风险过大的阈值
    ai_bad_drawdown_max = -0.025  # 预测窗口最大回撤低于 -2.5%

    # ============================================================
    # 第三层：小亏损保护参数
    # ============================================================

    small_loss_exit_threshold = -0.02  # -2%

    # ============================================================
    # 盈利保护参数
    # ============================================================

    profit_protection_trigger = 0.03  # 浮盈超过 3% 才启动保护
    profit_promise_ratio = 0.5         # 锁定 50% 浮盈

    # ============================================================
    # FreqAI 特征工程 - 展开特征（按周期展开）
    # ============================================================

    def feature_engineering_expand_all(self, dataframe: DataFrame, period: int, metadata: dict, **kwargs) -> DataFrame:
        """
        展开特征：每对 (timeframe, indicator_period) 都会调用一次。

        放入不需要先验知识的基础技术指标。
        FreqAI 会自动将这些特征按 include_timeframes, include_shifted_candles 等展开。
        """
        # 动量指标
        dataframe["%-rsi-period"] = ta.RSI(dataframe, timeperiod=period)
        dataframe["%-mfi-period"] = ta.MFI(dataframe, timeperiod=period)
        dataframe["%-adx-period"] = ta.ADX(dataframe, timeperiod=period)
        dataframe["%-cci-period"] = ta.CCI(dataframe, timeperiod=period)
        dataframe["%-roc-period"] = ta.ROC(dataframe, timeperiod=period)
        dataframe["%-willr-period"] = ta.WILLR(dataframe, timeperiod=period)

        # 随机指标
        try:
            stoch = ta.STOCHRSI(dataframe, timeperiod=period)
            dataframe["%-fastd-period"] = stoch["fastd"]
            dataframe["%-fastk-period"] = stoch["fastk"]
        except Exception:
            dataframe["%-fastd-period"] = 50.0
            dataframe["%-fastk-period"] = 50.0

        # 价格位置指标
        dataframe["%-ema_diff-period"] = (
            dataframe["close"] - ta.EMA(dataframe, timeperiod=period)
        ) / dataframe["close"].replace(0, float("nan"))

        # 布林带位置
        bb = ta.BBANDS(dataframe, timeperiod=period)
        bbp = (dataframe["close"] - bb["lowerband"]) / (
            bb["upperband"] - bb["lowerband"]
        ).replace(0, float("nan"))
        dataframe["%-bb_position-period"] = bbp

        # ATR 波动率
        dataframe["%-atr-period"] = ta.ATR(dataframe, timeperiod=period)
        dataframe["%-atr_pct-period"] = (
            ta.ATR(dataframe, timeperiod=period) / dataframe["close"].replace(0, float("nan"))
        )

        return dataframe

    # ============================================================
    # FreqAI 特征工程 - 标准特征（不展开）
    # ============================================================

    def feature_engineering_standard(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        非展开特征：每个 pair/timeframe 只调用一次。

        放入已有的 NFI 风控列和市场状态特征。
        """
        # NFI 保护状态
        for col in ["protections_long_global", "protections_short_global", "num_empty_288"]:
            if col in dataframe.columns:
                dataframe["%-" + col] = dataframe[col].fillna(0).astype(float)

        # 时间特征（帮助模型学习日内周期）
        dataframe["%-hour_of_day"] = dataframe["date"].dt.hour
        dataframe["%-day_of_week"] = dataframe["date"].dt.dayofweek

        return dataframe

    # ============================================================
    # FreqAI 标签定义
    # ============================================================

    def set_freqai_targets(self, dataframe: DataFrame, metadata: dict, **kwargs) -> DataFrame:
        """
        FreqAI 训练标签：
        1. 未来窗口最大上涨空间（&-s_future_return）
        2. 未来窗口最大回撤风险（&-s_future_drawdown）

        target 使用未来数据作为标签是正常的，只要不作为 feature 输入就不是特征泄露。
        """
        label_period = self.freqai_info.get("feature_parameters", {}).get(
            "label_period_candles", 48
        )

        future_high = dataframe["high"].rolling(window=label_period).max().shift(-label_period)
        future_low = dataframe["low"].rolling(window=label_period).min().shift(-label_period)

        dataframe["&-s_future_return"] = (future_high / dataframe["close"]) - 1
        dataframe["&-s_future_drawdown"] = (future_low / dataframe["close"]) - 1

        return dataframe

    # ============================================================
    # 指标管线（加入 FreqAI 入口）
    # ============================================================

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        """
        1. 先调用父类计算 NFI 原始指标
        2. 如果启用 FreqAI，再调用 self.freqai.start() 生成 AI 特征和预测
        """
        # NFI 原始指标
        df = super().populate_indicators(df, metadata)

        # FreqAI 特征和预测
        if self.config.get("freqai", {}).get("enabled", False):
            df = self.freqai.start(df, metadata, self)

        return df

    # ============================================================
    # 入场管线（叠加 AI 过滤）
    # ============================================================

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        """
        使用父类的入场信号，AI 仅做过滤。
        """
        # 先调用父类获取 NFI 入场信号
        df = super().populate_entry_trend(df, metadata)

        # 如果未启用 FreqAI，直接返回
        if not self.config.get("freqai", {}).get("enabled", False):
            return df

        # AI 入场过滤（LONG）
        df = self._apply_ai_entry_filter(df)

        return df

    def _apply_ai_entry_filter(self, df: DataFrame) -> DataFrame:
        """
        对 NFI 入场信号进行 AI 过滤。

        只过滤 LONG 入场（short 暂不处理）。
        如果 AI 预测未来上涨空间不足，则取消入场。
        """
        long_mask = df["enter_long"] == 1
        if not long_mask.any():
            return df

        for idx in df.index[long_mask]:
            if not self._ai_entry_ok(df, idx):
                df.loc[idx, "enter_long"] = 0
                df.loc[idx, "enter_tag"] = ""
                log.debug(
                    "AI filtered entry: pair=%s bar=%s",
                    df.loc[idx, "pair"] if "pair" in df.columns else "?",
                    idx,
                )

        return df

    # ============================================================
    # 坏单提前退出（AI 驱动）
    # ============================================================

    def custom_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> str | bool:
        """
        三层退出体系：
        第一层 硬风控（不可绕过）
        第二层 AI 辅助（需要确认）
        第三层 NFI 原版（正常止盈）
        """

        holding_bars = self._get_holding_bars(trade, current_time)

        # ============================================================
        # 第一层：硬风控，不依赖 AI，不可绕过
        # ============================================================

        # 1. 最大亏损硬退出
        if current_profit <= self.max_drawdown_threshold:
            log.info(
                f"Hard max drawdown exit: {pair} profit={current_profit:.4f} "
                f"threshold={self.max_drawdown_threshold}"
            )
            return "hard_max_drawdown_exit"

        # 2. 严重亏损 + 24h 退出
        if (
            current_profit <= self.loss_time_profit_1
            and holding_bars >= self.loss_time_exit_bars_1
        ):
            log.info(
                f"Hard time loss (24h): {pair} profit={current_profit:.4f} "
                f"bars={holding_bars}"
            )
            return "hard_time_loss_24h"

        # 3. 中等亏损 + 48h 退出
        if (
            current_profit <= self.loss_time_profit_2
            and holding_bars >= self.loss_time_exit_bars_2
        ):
            log.info(
                f"Hard time loss (48h): {pair} profit={current_profit:.4f} "
                f"bars={holding_bars}"
            )
            return "hard_time_loss_48h"

        # 4. 低效单 + 72h 退出
        if (
            current_profit < self.stale_profit_threshold
            and holding_bars >= self.stale_time_exit_bars
        ):
            log.info(
                f"Stale trade exit (72h): {pair} profit={current_profit:.4f} "
                f"bars={holding_bars}"
            )
            return "stale_trade_72h"

        # ============================================================
        # 第二层：AI 辅助退出（需要 AI + 高周期双重确认）
        # ============================================================

        if self.config.get("freqai", {}).get("enabled", False):
            ai_exit = self._ai_bad_trade_exit(
                pair, trade, current_time, current_rate, current_profit
            )
            if ai_exit:
                log.info(
                    f"AI bad trade exit: {pair} profit={current_profit:.4f} "
                    f"reason={ai_exit}"
                )
                return ai_exit

        # ============================================================
        # 第三层：小亏损保护（需要确认才触发）
        # ============================================================

        loss_exit = self._small_loss_exit(pair, trade, current_time, current_profit)
        if loss_exit:
            log.info(f"Small loss exit: {pair} profit={current_profit:.4f}")
            return loss_exit

        # ============================================================
        # 第四层：NFI 原版退出逻辑
        # ============================================================

        parent_exit = super().custom_exit(
            pair, trade, current_time, current_rate, current_profit, **kwargs
        )
        if parent_exit:
            return parent_exit

        return False

    def _ai_bad_trade_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
    ) -> str | bool:
        """
        AI 坏单提前退出：
        只在 AI（5m）和高周期（4h）同时确认弱势时触发。

        条件：
        1. 当前亏损
        2. 持仓超过最低观察期
        3. AI 预测反弹空间不足
        4. AI 预测回撤风险较大
        5. 高周期趋势确认弱势（关键！）
        """
        if current_profit >= 0:
            return False

        holding_bars = self._get_holding_bars(trade, current_time)
        if holding_bars < self.ai_exit_min_bars:
            return False

        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return False

        last = df.iloc[-1]
        do_predict = self._safe_float(last.get("do_predict"), 0.0)
        if int(do_predict) != 1:
            return False

        pred_return, pred_drawdown = self._get_prediction_values(last)
        if pred_return is None or pred_drawdown is None:
            return False

        # AI 必须同时认为反弹空间不足且回撤风险较大
        if pred_return >= self.ai_bad_return_max:
            return False
        if pred_drawdown >= self.ai_bad_drawdown_max:
            return False

        # 高周期弱势确认
        if not self._htf_weak_confirm(pair):
            return False

        return "ai_bad_trade_exit"

    def _htf_weak_confirm(self, pair: str) -> bool:
        """
        高周期（4h）弱势确认。
        检查 4h EMA 趋势方向，确认弱势后才允许 AI 退出。
        无数据 / 异常时返回 False，避免误杀。
        """
        try:
            df_4h, _ = self.dp.get_analyzed_dataframe(pair, "4h")
            if df_4h is None or df_4h.empty:
                return False

            last = df_4h.iloc[-1]
            close = self._safe_float(last.get("close"))
            if close is None:
                return False

            ema_50 = self._safe_float(last.get("ema_50"))
            ema_200 = self._safe_float(last.get("ema_200"))

            weak_by_50 = ema_50 is not None and close < ema_50
            weak_by_200 = ema_200 is not None and close < ema_200

            return weak_by_50 or weak_by_200
        except Exception:
            return False

    def _small_loss_exit(
        self,
        pair: str,
        trade,
        current_time,
        current_profit: float,
    ) -> str | bool:
        """
        小亏损保护：
        亏损达到 -2% 且持仓较久，且 AI 确认反弹空间不足时退出。
        保守策略：不单独退出，需要 AI 确认才触发。
        """
        if current_profit > self.small_loss_exit_threshold:
            return False

        holding_bars = self._get_holding_bars(trade, current_time)
        if holding_bars < 144:  # 持仓不足 12h，不处理
            return False

        # AI 启用时必须 AI 确认
        if self.config.get("freqai", {}).get("enabled", False):
            df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if df is None or df.empty:
                return False

            last = df.iloc[-1]
            do_predict = self._safe_float(last.get("do_predict"), 0.0)
            if int(do_predict) != 1:
                return False

            pred_return, pred_drawdown = self._get_prediction_values(last)
            if pred_return is None or pred_drawdown is None:
                return False

            if pred_return < 0.008 and pred_drawdown < -0.02:
                if self._htf_weak_confirm(pair):
                    return "small_loss_ai_exit"

            return False

        # 无 AI 时不单独触发，交给硬风控处理
        return False

    def _get_holding_bars(self, trade, current_time=None) -> int:
        """
        计算当前持仓已经经历的 K 线数量。
        必须传入 current_time，否则无法正确计算持仓中交易的时间。
        """
        if not trade or not trade.is_open:
            return 0

        if current_time is None:
            return 0

        timeframe_minutes = self._timeframe_to_minutes(self.timeframe)
        if timeframe_minutes <= 0:
            return 0

        open_time = getattr(trade, "open_date_utc", None) or getattr(trade, "open_date", None)
        if open_time is None:
            return 0

        # 统一去掉 tzinfo，避免 offset-naive / offset-aware 对比报错
        if hasattr(open_time, "tzinfo") and open_time.tzinfo is not None:
            open_time = open_time.replace(tzinfo=None)
        if hasattr(current_time, "tzinfo") and current_time.tzinfo is not None:
            current_time = current_time.replace(tzinfo=None)

        elapsed_minutes = (current_time - open_time).total_seconds() / 60
        return max(int(elapsed_minutes / timeframe_minutes), 0)

    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """
        将 timeframe 字符串转换为分钟数。
        """
        multipliers = {"m": 1, "h": 60, "d": 1440, "w": 10080}
        if not timeframe:
            return 5
        unit = timeframe[-1].lower()
        value = int(timeframe[:-1]) if timeframe[:-1].isdigit() else 5
        return value * multipliers.get(unit, 1)

    # ============================================================
    # 动态止损（AI + 盈利保护）
    # ============================================================

    def custom_stoploss(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> float:
        """
        只负责盈利保护。
        最大亏损、时间止损、坏单退出全部放到 custom_exit() 中。
        """
        parent_sl = super().custom_stoploss(
            pair, trade, current_time, current_rate, current_profit, **kwargs
        )
        if parent_sl is not None and parent_sl != -0.99:
            return parent_sl

        # 浮盈超过 3% 后才启动盈利保护，避免过早扫掉趋势单
        if current_profit >= self.profit_protection_trigger:
            protected_profit = current_profit * self.profit_promise_ratio
            stoploss_distance = current_profit - protected_profit
            return -max(stoploss_distance, 0.005)

        return -0.99

    # ============================================================
    # FreqAI 辅助方法
    # ============================================================

    def _pred_return_column(self) -> str:
        """FreqAI 预测列名：未来上涨空间。"""
        return "&-s_future_return"

    def _pred_drawdown_column(self) -> str:
        """FreqAI 预测列名：未来回撤风险。"""
        return "&-s_future_drawdown"

    def _safe_float(self, val, default=None):
        """安全转换为 float，处理 None / NaN / 非法值。"""
        try:
            if val is None:
                return default
            val = float(val)
            if val != val:  # NaN check
                return default
            return val
        except (TypeError, ValueError):
            return default

    def _get_prediction_values(self, row):
        """从 DataFrame 行中读取两个 AI 预测值。"""
        pred_return = self._safe_float(row.get(self._pred_return_column()))
        pred_drawdown = self._safe_float(row.get(self._pred_drawdown_column()))
        return pred_return, pred_drawdown

    def _get_ai_threshold(self) -> float:
        """
        动态阈值：训练集均值 - 1.0 * 标准差。
        如果无法获取训练数据统计，返回保守默认值。
        """
        dk = getattr(self.freqai, "dk", None)
        if dk is None or dk.data is None:
            return 0.005  # 保守默认 0.5%

        col = self._pred_return_column()
        mean = float(dk.data.get(col + "_mean", 0.01))
        std = float(dk.data.get(col + "_std", 0.02))

        # 阈值 = 均值 - 1.0 * 标准差，最低为 0
        return max(mean - 1.0 * std, 0.0)

    def _is_weak_entry(self, entry_tag: str | None) -> bool:
        """判断是否是 NFI 弱信号（放宽/扩展/AI候选）。"""
        if not entry_tag:
            return False
        tag = str(entry_tag).lower()
        weak_keywords = ["weak", "expanded", "loosened", "ai_candidate"]
        return any(k in tag for k in weak_keywords)

    def _ai_entry_ok(self, df: DataFrame, idx) -> bool:
        """
        判断指定索引处的 NFI 入场信号是否通过 AI 过滤。

        原则：
        - 强信号：只在明显危险时拦截
        - 弱信号：必须 AI 明确看好才放行
        - AI 不确定（do_predict != 1）：强信号放行，弱信号拒绝
        """
        row = df.loc[idx]
        entry_tag = row.get("enter_tag", "")
        is_weak = self._is_weak_entry(entry_tag)

        do_predict = self._safe_float(row.get("do_predict"), 0.0)

        # AI 不确定时：强信号放行，弱信号拒绝
        if int(do_predict) != 1:
            return not is_weak

        pred_return, pred_drawdown = self._get_prediction_values(row)

        # 没有预测值时：强信号放行，弱信号拒绝
        if pred_return is None or pred_drawdown is None:
            return not is_weak

        if is_weak:
            # 弱信号：必须明确看好（高收益 + 低回撤）
            return (
                pred_return > 0.012
                and pred_drawdown > -0.025
            )

        # 强信号：只在明显危险时拦截
        if pred_drawdown < -0.04 and pred_return < 0.006:
            return False

        return True

    # ============================================================
    # confirm_trade_entry（可选的入场前额外检查）
    # ============================================================

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> bool:
        """
        入场前确认：

        1. 先调用父类确认逻辑
        2. 可在此添加额外的入场前检查
        """
        parent_ok = super().confirm_trade_entry(
            pair, order_type, amount, rate, time_in_force, current_time, entry_tag, side, **kwargs
        )
        if not parent_ok:
            return False

        # 可选：在此添加入场前额外检查
        # 例如：仓位数量检查、钱包余额检查等

        return True

    # ============================================================
    # 版本
    # ============================================================

    def version(self) -> str:
        return "nfi-ai-wrapper-v0.2.0"