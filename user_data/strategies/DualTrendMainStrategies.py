from __future__ import annotations

from datetime import timezone
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import informative, stoploss_from_absolute

from DualTrendCombinedLongDailyCenterShortV1Strategy import (
    DualTrendCombinedLongDailyCenterShortV1Strategy,
)


class _DualTrendCombinedGlobalFilterBase(DualTrendCombinedLongDailyCenterShortV1Strategy):
    """
    Global validation variants for the combined strategy.

    Goal:
    - do not special-case individual pairs
    - improve entry quality with market-wide filters
    - reduce low-quality long 1d breakouts and weak short pullbacks
    """

    use_short_daily_center_filter = False
    short_filter_mode = "strict_all"
    use_long_strong_confirm = False
    use_long_btc_trend_filter = False
    long_filter_mode = "none"
    use_short_pullback_shape_filter = False
    short_pullback_max_width_pct = 0.035
    use_short_pullback_depth_guard = False
    short_pullback_breakdown_depth_min = 0.0
    use_short_compression_flush_guard = False
    short_compression_prev3h_reject = -0.010
    short_compression_prev6h_reject = -0.015
    short_compression_atr_pct_percentile_reject = 0.45
    use_short_compression_close_quality_guard = False
    short_compression_close_quality_max_close_position = 0.30
    use_short_compression_close_quality_oversold_guard = False
    short_compression_oversold_prev3h_reject = -0.004
    short_compression_oversold_prev6h_reject = -0.008
    use_long_center_streak_filter = False
    long_center_streak_min = 3

    long_daily_rsi = 58

    @staticmethod
    def _add_legacy_center(dataframe: DataFrame, suffix: str = "") -> DataFrame:
        typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0
        center = typical_price.rolling(5).mean()
        dataframe[f"legacy_market_center{suffix}"] = center
        dataframe[f"legacy_center_up{suffix}"] = center > center.shift(3)
        dataframe[f"legacy_center_down{suffix}"] = center < center.shift(3)
        return dataframe

    @staticmethod
    def _rolling_percentile(series: pd.Series, window: int, min_periods: int | None = None) -> pd.Series:
        if min_periods is None:
            min_periods = max(20, window // 3)

        def _pct(values) -> float:
            s = pd.Series(values)
            return float(s.rank(pct=True).iloc[-1])

        return series.rolling(window, min_periods=min_periods).apply(_pct, raw=False)

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators_1d(dataframe, metadata).copy()
        return self._add_legacy_center(dataframe).copy()

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata).copy()
        dataframe = self._add_legacy_center(dataframe).copy()
        dataframe["ema20_1h"] = dataframe["close"].ewm(span=20, adjust=False, min_periods=20).mean()
        dataframe["ema50_1h"] = dataframe["close"].ewm(span=50, adjust=False, min_periods=50).mean()
        dataframe["ret_1h"] = dataframe["close"] / dataframe["close"].shift(1) - 1.0
        dataframe["prev_3h_return"] = dataframe["close"].shift(1) / dataframe["close"].shift(4) - 1.0
        dataframe["prev_6h_return"] = dataframe["close"].shift(1) / dataframe["close"].shift(7) - 1.0
        dataframe["breakdown_depth"] = (dataframe["compression_low"] - dataframe["close"]) / dataframe["compression_low"]
        dataframe["atr_pct_percentile"] = self._rolling_percentile(dataframe["atr_pct"], 720)
        dataframe["close_not_low_enough"] = dataframe["close_position"] > 0.30
        return dataframe.copy()

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        short_entry = dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)

        if self.use_short_daily_center_filter and short_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            center_down_1d = dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            center_up_1d = dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            market_center_1d = dataframe.get("legacy_market_center_1d", pd.Series(np.nan, index=dataframe.index))
            close_below_center = dataframe["close"] < market_center_1d
            close_above_center = dataframe["close"] > market_center_1d

            if self.short_filter_mode == "strict_all":
                allow_short = center_down_1d & close_below_center
                reject_short = short_entry & ~allow_short
            elif self.short_filter_mode == "strict_breakdown_only":
                allow_short = center_down_1d & close_below_center
                reject_short = short_entry & enter_tag.eq("short_compression_breakdown") & ~allow_short
            elif self.short_filter_mode == "reject_clear_uptrend_all":
                reject_short = short_entry & center_up_1d & close_above_center
            elif self.short_filter_mode == "reject_clear_uptrend_breakdown_only":
                reject_short = (
                    short_entry
                    & enter_tag.eq("short_compression_breakdown")
                    & center_up_1d
                    & close_above_center
                )
            else:
                reject_short = pd.Series(False, index=dataframe.index)

            dataframe.loc[reject_short, "enter_short"] = 0
            dataframe.loc[reject_short, "enter_tag"] = None
            dataframe.loc[reject_short, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_short, "enter_risk_pct"] = np.nan

        if self.use_long_strong_confirm and long_entry.any():
            allow_long = (
                dataframe.get("daily_momentum_long_1d", pd.Series(False, index=dataframe.index)).fillna(False)
                & dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index)).fillna(False)
                & dataframe.get("center_up_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            )
            if self.use_long_btc_trend_filter and metadata["pair"] != "BTC/USDT:USDT":
                allow_long &= dataframe.get("btc_trend_up_4h", pd.Series(False, index=dataframe.index)).fillna(False)

            reject_long = long_entry & ~allow_long
            dataframe.loc[reject_long, "enter_long"] = 0
            dataframe.loc[reject_long, "enter_tag"] = None
            dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_long, "enter_risk_pct"] = np.nan

        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.long_filter_mode != "none" and long_entry.any():
            center_down_1d = dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            center_up_1d = dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            market_center_1d = dataframe.get("legacy_market_center_1d", pd.Series(np.nan, index=dataframe.index))
            close_below_center = dataframe["close"] < market_center_1d
            close_above_center = dataframe["close"] > market_center_1d

            if self.long_filter_mode == "reject_clear_downtrend":
                reject_long = long_entry & center_down_1d & close_below_center
            elif self.long_filter_mode == "require_4h_trend_up":
                allow_long = dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index)).fillna(False)
                reject_long = long_entry & ~allow_long
            elif self.long_filter_mode == "require_legacy_center_up":
                reject_long = long_entry & ~(center_up_1d & close_above_center)
            else:
                reject_long = pd.Series(False, index=dataframe.index)

            dataframe.loc[reject_long, "enter_long"] = 0
            dataframe.loc[reject_long, "enter_tag"] = None
            dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_long, "enter_risk_pct"] = np.nan

        short_entry = dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.use_short_pullback_shape_filter and short_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            center_down_1d = dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            market_center_1d = dataframe.get("legacy_market_center_1d", pd.Series(np.nan, index=dataframe.index))
            close_below_center = dataframe["close"] < market_center_1d
            tight_enough = dataframe.get(
                "compression_width_pct",
                pd.Series(np.nan, index=dataframe.index),
            ) <= self.short_pullback_max_width_pct
            shape_ok = center_down_1d & close_below_center & tight_enough.fillna(False)
            reject_short = short_entry & enter_tag.eq("short_pullback_restart") & ~shape_ok
            dataframe.loc[reject_short, "enter_short"] = 0
            dataframe.loc[reject_short, "enter_tag"] = None
            dataframe.loc[reject_short, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_short, "enter_risk_pct"] = np.nan

        short_entry = dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.use_short_pullback_depth_guard and short_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            breakdown_depth = dataframe.get("breakdown_depth", pd.Series(np.nan, index=dataframe.index))
            reject_short = (
                short_entry
                & enter_tag.eq("short_pullback_restart")
                & (breakdown_depth < self.short_pullback_breakdown_depth_min)
            )
            dataframe.loc[reject_short, "enter_short"] = 0
            dataframe.loc[reject_short, "enter_tag"] = None
            dataframe.loc[reject_short, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_short, "enter_risk_pct"] = np.nan

        if self.use_short_compression_flush_guard and short_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            prev_3h = dataframe.get("prev_3h_return", pd.Series(np.nan, index=dataframe.index))
            prev_6h = dataframe.get("prev_6h_return", pd.Series(np.nan, index=dataframe.index))
            atr_pct_percentile = dataframe.get("atr_pct_percentile", pd.Series(np.nan, index=dataframe.index))
            reject_short = (
                short_entry
                & enter_tag.eq("short_compression_breakdown")
                & (prev_3h <= self.short_compression_prev3h_reject)
                & (prev_6h <= self.short_compression_prev6h_reject)
                & (atr_pct_percentile >= self.short_compression_atr_pct_percentile_reject)
            )
            dataframe.loc[reject_short, "enter_short"] = 0
            dataframe.loc[reject_short, "enter_tag"] = None
            dataframe.loc[reject_short, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_short, "enter_risk_pct"] = np.nan

        short_entry = dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.use_short_compression_close_quality_guard and short_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            close_position = dataframe.get("close_position", pd.Series(np.nan, index=dataframe.index))
            reject_short = (
                short_entry
                & enter_tag.eq("short_compression_breakdown")
                & (close_position > self.short_compression_close_quality_max_close_position)
            )
            dataframe.loc[reject_short, "enter_short"] = 0
            dataframe.loc[reject_short, "enter_tag"] = None
            dataframe.loc[reject_short, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_short, "enter_risk_pct"] = np.nan

        short_entry = dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.use_short_compression_close_quality_oversold_guard and short_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            close_position = dataframe.get("close_position", pd.Series(np.nan, index=dataframe.index))
            prev_3h = dataframe.get("prev_3h_return", pd.Series(np.nan, index=dataframe.index))
            prev_6h = dataframe.get("prev_6h_return", pd.Series(np.nan, index=dataframe.index))
            reject_short = (
                short_entry
                & enter_tag.eq("short_compression_breakdown")
                & (close_position > self.short_compression_close_quality_max_close_position)
                & (
                    (prev_3h <= self.short_compression_oversold_prev3h_reject)
                    | (prev_6h <= self.short_compression_oversold_prev6h_reject)
                )
            )
            dataframe.loc[reject_short, "enter_short"] = 0
            dataframe.loc[reject_short, "enter_tag"] = None
            dataframe.loc[reject_short, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_short, "enter_risk_pct"] = np.nan

        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.use_long_center_streak_filter and long_entry.any():
            enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
            center_up_1d = dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            range_contracting_1d = dataframe.get("range_contracting_1d", pd.Series(False, index=dataframe.index)).fillna(False)
            streak = pd.Series(0, index=dataframe.index, dtype="int64")
            for i in range(1, self.long_center_streak_min + 1):
                streak += center_up_1d.shift(i - 1).fillna(False).astype("int64")
            streak_ok = streak >= self.long_center_streak_min
            confirm_long = range_contracting_1d & streak_ok
            reject_long = long_entry & enter_tag.eq("long_1d_center_compression") & ~confirm_long
            dataframe.loc[reject_long, "enter_long"] = 0
            dataframe.loc[reject_long, "enter_tag"] = None
            dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_long, "enter_risk_pct"] = np.nan

        return dataframe


class DualTrendCombinedGlobalV2Strategy(_DualTrendCombinedGlobalFilterBase):
    """
    Current combined candidate:
    - keep validated Long daily center RSI at 58
    - reject shorts only when 1d legacy center is clearly up and price is above it
    """

    use_short_daily_center_filter = True
    short_filter_mode = "reject_clear_uptrend_all"
    long_daily_rsi = 58


class DualTrendRawStrategy(DualTrendCombinedGlobalV2Strategy):
    """
    Raw combined strategy with the validated pullback shape filter.
    """

    use_short_pullback_shape_filter = True
    short_pullback_max_width_pct = 0.035


class DualTrendRawBreakevenStrategy(DualTrendRawStrategy):
    """
    Raw strategy plus only the +2% breakeven profit-lock.

    No reach5 split, no guard layer, no extra trailing logic.
    """

    profit_lock_steps = ((0.02, 0.001),)


class DualTrendRawBreakevenGuardStrategy(DualTrendRawBreakevenStrategy):
    """
    Raw breakeven strategy plus the validated compression flush guard.

    This is intentionally guard-only and does not inherit the old reach5
    strong/weak split from DualTrendBaselineStrategy.
    """

    use_short_compression_flush_guard = True
    short_compression_prev3h_reject = -0.006
    short_compression_prev6h_reject = -0.012
    short_compression_atr_pct_percentile_reject = 0.45


class _DualTrendReach5ConditionalMixin:
    reach5_strong_hours = 18.0

    @staticmethod
    def _elapsed_hours_since_open(trade: Trade, current_time) -> float:
        trade_time = pd.Timestamp(trade.open_date_utc)
        if trade_time.tzinfo is None:
            trade_time = trade_time.tz_localize("UTC")
        now = pd.Timestamp(current_time)
        if now.tzinfo is None:
            now = now.tz_localize(timezone.utc)
        return max(0.0, (now - trade_time).total_seconds() / 3600.0)

    def _is_strong_reach5_trade(self, trade: Trade, current_time) -> bool:
        return self._elapsed_hours_since_open(trade, current_time) <= self.reach5_strong_hours

    @staticmethod
    def _adverse_move_since_open(trade: Trade) -> float:
        open_rate = float(trade.open_rate)
        if trade.is_short:
            max_rate = float(getattr(trade, "max_rate", open_rate) or open_rate)
            return max(0.0, (max_rate - open_rate) / open_rate)
        min_rate = float(getattr(trade, "min_rate", open_rate) or open_rate)
        return max(0.0, (open_rate - min_rate) / open_rate)

    def _current_body_ratio(self, pair: str) -> float:
        candle = self._current_candle(pair)
        if candle is None:
            return 0.0
        candle_range = float(candle["high"] - candle["low"])
        if candle_range <= 0:
            return 0.0
        return abs(float(candle["close"]) - float(candle["open"])) / candle_range

    def _current_ret_1h(self, pair: str) -> float:
        candle = self._current_candle(pair)
        if candle is None:
            return 0.0
        value = candle.get("ret_1h", 0.0)
        if pd.isna(value):
            return 0.0
        return float(value)

    def _current_close_vs_ema20(self, pair: str) -> float:
        candle = self._current_candle(pair)
        if candle is None:
            return 0.0
        ema20 = candle.get("ema20_1h", np.nan)
        close = candle.get("close", np.nan)
        if pd.isna(ema20) or pd.isna(close) or float(ema20) == 0.0:
            return 0.0
        return (float(close) - float(ema20)) / float(ema20)

    def _current_ret_6h(self, pair: str) -> float:
        candle = self._current_candle(pair)
        if candle is None:
            return 0.0
        value = candle.get("ret_6h", 0.0)
        if pd.isna(value):
            return 0.0
        return float(value)

    def _current_4h_ema50_slope_3(self, pair: str) -> float:
        if not self.dp:
            return 0.0
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty or "ema50_4h" not in dataframe:
            return 0.0
        valid = dataframe["ema50_4h"].dropna()
        if len(valid) < 13:
            return 0.0
        current = float(valid.iloc[-1])
        previous = float(valid.iloc[-13])
        if previous == 0.0:
            return 0.0
        return (current - previous) / previous

    @staticmethod
    def _trade_enter_tag(trade: Trade) -> Optional[str]:
        tag = getattr(trade, "enter_tag", None)
        if tag:
            return str(tag)
        getter = getattr(trade, "get_custom_data", None)
        if getter is None:
            return None
        stored_tag = getter(key="enter_tag")
        return None if stored_tag is None else str(stored_tag)


class DualTrendBaselineStrategy(
    _DualTrendReach5ConditionalMixin,
    DualTrendRawStrategy,
):
    """
    Main baseline strategy:
    - +2% breakeven lock
    - at +5%, weak trades exit fully
    - strong trades keep the ROI 10% path
    - strong/weak split uses adverse move before 5%: <=1.25% is strong
    """

    position_adjustment_enable = True
    profit_lock_steps = ((0.02, 0.001),)
    reach5_trigger_profit = 0.05
    strong_adverse_limit = 0.0125

    def adjust_trade_position(
        self,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        min_stake: Optional[float],
        max_stake: float,
        current_entry_rate: float,
        current_exit_rate: float,
        current_entry_profit: float,
        current_exit_profit: float,
        **kwargs,
    ) -> Optional[float]:
        getter = getattr(trade, "get_custom_data", None)
        setter = getattr(trade, "set_custom_data", None)
        if getter is None or setter is None:
            return None
        if getter(key="dualtrend_reach5_decision") is not None:
            return None
        if current_profit < self.reach5_trigger_profit:
            return None

        adverse = self._adverse_move_since_open(trade)
        setter(key="dualtrend_reach5_decision_time", value=pd.Timestamp(current_time).isoformat())
        setter(key="dualtrend_reach5_decision_profit", value=float(current_profit))
        setter(key="dualtrend_reach5_decision_adverse", value=float(adverse))
        if adverse <= self.strong_adverse_limit:
            setter(key="dualtrend_reach5_decision", value="strong_adverse125_hold_roi10")
            return None

        setter(key="dualtrend_reach5_decision", value="weak_full_exit")
        return -float(trade.stake_amount)


class _DualTrendStrongRunnerReach5Mixin(_DualTrendReach5ConditionalMixin):
    """
    Strong-runner split for short_pullback_restart after +5% profit.

    Only short_pullback_restart trades use the new classification.
    All other tags keep the parent baseline / guard behavior unchanged.
    """

    def adjust_trade_position(
        self,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        min_stake: Optional[float],
        max_stake: float,
        current_entry_rate: float,
        current_exit_rate: float,
        current_entry_profit: float,
        current_exit_profit: float,
        **kwargs,
    ) -> Optional[float]:
        if self._trade_enter_tag(trade) != "short_pullback_restart" or not bool(getattr(trade, "is_short", False)):
            return super().adjust_trade_position(
                trade=trade,
                current_time=current_time,
                current_rate=current_rate,
                current_profit=current_profit,
                min_stake=min_stake,
                max_stake=max_stake,
                current_entry_rate=current_entry_rate,
                current_exit_rate=current_exit_rate,
                current_entry_profit=current_entry_profit,
                current_exit_profit=current_exit_profit,
                **kwargs,
            )

        getter = getattr(trade, "get_custom_data", None)
        setter = getattr(trade, "set_custom_data", None)
        if getter is None or setter is None:
            return None
        if getter(key="dualtrend_reach5_decision") is not None:
            return None
        if current_profit < self.reach5_trigger_profit:
            return None

        elapsed_hours = self._elapsed_hours_since_open(trade, current_time)
        adverse = self._adverse_move_since_open(trade)
        strong = elapsed_hours <= self.reach5_strong_hours and adverse <= self.strong_adverse_limit

        setter(key="dualtrend_reach5_decision_time", value=pd.Timestamp(current_time).isoformat())
        setter(key="dualtrend_reach5_decision_profit", value=float(current_profit))
        setter(key="dualtrend_reach5_decision_adverse", value=float(adverse))
        setter(key="dualtrend_reach5_decision_hours_to_5", value=float(elapsed_hours))
        if strong:
            setter(
                key="dualtrend_reach5_decision",
                value=f"strong_runner_h{self.reach5_strong_hours:g}_a{self.strong_adverse_limit:.4f}",
            )
            return None

        setter(key="dualtrend_reach5_decision", value="weak_full_exit")
        return -float(trade.stake_amount)


class _DualTrendStructureStrongRunnerReach5Mixin(_DualTrendReach5ConditionalMixin):
    """
    Strong-runner split for short_pullback_restart after +5% profit.

    This version adds a stricter structure check at the +5% decision point:
    - adverse move before +5% must still be small
    - the last 6h return must remain strongly negative
    - the merged 4h EMA50 slope must still point down
    """

    structure_adverse_limit = 0.0125
    structure_ret_6h_max = -0.02
    structure_4h_ema50_slope3_max = -0.005

    def adjust_trade_position(
        self,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        min_stake: Optional[float],
        max_stake: float,
        current_entry_rate: float,
        current_exit_rate: float,
        current_entry_profit: float,
        current_exit_profit: float,
        **kwargs,
    ) -> Optional[float]:
        if self._trade_enter_tag(trade) != "short_pullback_restart" or not bool(getattr(trade, "is_short", False)):
            return super().adjust_trade_position(
                trade=trade,
                current_time=current_time,
                current_rate=current_rate,
                current_profit=current_profit,
                min_stake=min_stake,
                max_stake=max_stake,
                current_entry_rate=current_entry_rate,
                current_exit_rate=current_exit_rate,
                current_entry_profit=current_entry_profit,
                current_exit_profit=current_exit_profit,
                **kwargs,
            )

        getter = getattr(trade, "get_custom_data", None)
        setter = getattr(trade, "set_custom_data", None)
        if getter is None or setter is None:
            return None
        if getter(key="dualtrend_reach5_decision") is not None:
            return None
        if current_profit < self.reach5_trigger_profit:
            return None

        pair = trade.pair
        adverse = self._adverse_move_since_open(trade)
        ret_6h = self._current_ret_6h(pair)
        slope_4h = self._current_4h_ema50_slope_3(pair)
        strong = (
            adverse <= self.structure_adverse_limit
            and ret_6h <= self.structure_ret_6h_max
            and slope_4h <= self.structure_4h_ema50_slope3_max
        )

        setter(key="dualtrend_reach5_decision_time", value=pd.Timestamp(current_time).isoformat())
        setter(key="dualtrend_reach5_decision_profit", value=float(current_profit))
        setter(key="dualtrend_reach5_decision_adverse", value=float(adverse))
        setter(key="dualtrend_reach5_decision_ret_6h", value=float(ret_6h))
        setter(key="dualtrend_reach5_decision_ema50_slope3_4h", value=float(slope_4h))
        if strong:
            setter(
                key="dualtrend_reach5_decision",
                value=(
                    "strong_structure_"
                    f"a{self.structure_adverse_limit:.4f}_"
                    f"r{self.structure_ret_6h_max:.4f}_"
                    f"s{self.structure_4h_ema50_slope3_max:.4f}"
                ),
            )
            return None

        setter(key="dualtrend_reach5_decision", value="weak_full_exit")
        return -float(trade.stake_amount)


class DualTrendGuardStrategy(DualTrendBaselineStrategy):
    """
    Main guard strategy:
    - only for short_compression_breakdown
    - reject flushy breakdowns with already-heavy short-term downside and hot ATR
    """

    use_short_compression_flush_guard = True
    short_compression_prev3h_reject = -0.006
    short_compression_prev6h_reject = -0.012
    short_compression_atr_pct_percentile_reject = 0.45


class DualTrendRawBreakevenGuardStrongRunnerStructureStrategy(
    _DualTrendStructureStrongRunnerReach5Mixin,
    DualTrendRawBreakevenGuardStrategy,
):
    """
    Current mainline guard base plus narrow +5% strong-runner split.

    Scope is intentionally small:
    - only short_pullback_restart
    - only after the trade has already reached +5%
    - keep current raw+breakeven+guard entries unchanged
    """

    position_adjustment_enable = True
    reach5_trigger_profit = 0.05


class DualTrendCompressionCloseQualityGuardStrategy(
    _DualTrendStructureStrongRunnerReach5Mixin,
    DualTrendRawBreakevenGuardStrategy,
):
    """
    Light entry-quality variant:
    - keep the current main candidate unchanged otherwise
    - only reject short_compression_breakdown entries when the breakdown candle
      does not close near the low
    """

    position_adjustment_enable = True
    reach5_trigger_profit = 0.05
    use_short_compression_close_quality_guard = True
    short_compression_close_quality_max_close_position = 0.30


class DualTrendCompressionCloseQualityGuard028Strategy(
    DualTrendCompressionCloseQualityGuardStrategy,
):
    """Threshold sweep: reject when close_position > 0.28."""

    short_compression_close_quality_max_close_position = 0.28


class _DualTrendTagStructuredStopMixin:
    """
    Tag-specific stoploss research layer.

    Keep entries unchanged. Only change the live stop placement after entry so
    we can test whether pullback-restarters and compression-breakdowns deserve
    different stop widths.
    """

    short_pullback_stop_atr_mult = 0.2
    short_compression_stop_atr_mult = 0.2
    short_pullback_stop_cap = 0.05
    short_compression_stop_cap = 0.05

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> Optional[float]:
        if not bool(getattr(trade, "is_short", False)):
            return super().custom_stoploss(
                pair=pair,
                trade=trade,
                current_time=current_time,
                current_rate=current_rate,
                current_profit=current_profit,
                after_fill=after_fill,
                **kwargs,
            )

        candle = self._entry_candle(pair, trade)
        if candle is None:
            return self.stoploss

        tag = self._trade_enter_tag(trade) or ""
        if tag == "short_compression_breakdown":
            anchor = float(candle.get("compression_high", np.nan))
            atr_ref = float(candle.get("atr_ref", np.nan))
            atr_mult = self.short_compression_stop_atr_mult
            stop_cap = self.short_compression_stop_cap
        else:
            anchor = float(candle.get("pullback_high_12", np.nan))
            atr_ref = float(candle.get("atr_ref", np.nan))
            atr_mult = self.short_pullback_stop_atr_mult
            stop_cap = self.short_pullback_stop_cap

        if not np.isfinite(anchor):
            return super().custom_stoploss(
                pair=pair,
                trade=trade,
                current_time=current_time,
                current_rate=current_rate,
                current_profit=current_profit,
                after_fill=after_fill,
                **kwargs,
            )

        stop_price = anchor
        if np.isfinite(atr_ref):
            stop_price = anchor + atr_mult * atr_ref

        capped_stop = trade.open_rate * (1 + stop_cap)
        stop_price = min(stop_price, capped_stop)

        profit_lock_stop = self._profit_lock_stop_price(trade, current_profit)
        if profit_lock_stop is not None:
            stop_price = min(stop_price, profit_lock_stop)

        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=True,
            leverage=trade.leverage,
        )


class DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy(
    _DualTrendTagStructuredStopMixin,
    DualTrendCompressionCloseQualityGuard028Strategy,
):
    """
    Candidate A:
    - keep pullback stop unchanged
    - make compression-breakdown stop tighter
    """

    short_pullback_stop_atr_mult = 0.20
    short_compression_stop_atr_mult = 0.10
    short_pullback_stop_cap = 0.05
    short_compression_stop_cap = 0.04


class _DualTrendWinnerPyramidMixin:
    """
    Let winner-pyramiding run before the reach5 decision mixins.

    The imported base strategy already implements the actual add-on logic in
    `adjust_trade_position()`. Some higher-level research mixins also override
    that callback for +5% profit decisions, which can short-circuit the add-on
    path before it ever executes. This shim restores the intended order:
    1. try add-on / partial logic from the base strategy
    2. if nothing happened, continue into the reach5 decision chain
    """

    def adjust_trade_position(
        self,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        min_stake: Optional[float],
        max_stake: float,
        current_entry_rate: float,
        current_exit_rate: float,
        current_entry_profit: float,
        current_exit_profit: float,
        **kwargs,
    ) -> Optional[float]:
        base_result = DualTrendCombinedLongDailyCenterShortV1Strategy.adjust_trade_position(
            self,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            min_stake=min_stake,
            max_stake=max_stake,
            current_entry_rate=current_entry_rate,
            current_exit_rate=current_exit_rate,
            current_entry_profit=current_entry_profit,
            current_exit_profit=current_exit_profit,
            **kwargs,
        )
        if base_result is not None:
            return base_result

        return super().adjust_trade_position(
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            min_stake=min_stake,
            max_stake=max_stake,
            current_entry_rate=current_entry_rate,
            current_exit_rate=current_exit_rate,
            current_entry_profit=current_entry_profit,
            current_exit_profit=current_exit_profit,
            **kwargs,
        )


class DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25Strategy(
    _DualTrendWinnerPyramidMixin,
    DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy,
):
    """
    Same early profit window as the best narrow candidate, but with a slightly
    larger second layer to test the return / drawdown balance.
    """

    position_adjustment_enable = True
    pyramiding_enabled = True
    pyramid_allowed_tags = ("short_pullback_restart",)
    max_entry_position_adjustment = 1
    pyramid_profit_threshold = 0.005
    pyramid_profit_cap = 0.020
    pyramid_stake_fraction = 0.25
    pyramid_max_additions = 1
    pyramid_use_structural_reinforcement = False


class DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardStrategy(
    DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25Strategy,
):
    """
    Add-on only when the second signal also closes near the low.
    """

    pyramid_require_close_position_max = 0.30


class DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardLegBeStrategy(
    DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardStrategy,
):
    """
    Add a separate breakeven-protect layer for the first add-on leg only.
    """

    pyramid_leg_breakeven_enabled = True
    pyramid_leg_breakeven_trigger_profit = 0.02


class DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardLegBe015Strategy(
    DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardLegBeStrategy,
):
    """
    Same as the leg-breakeven candidate, but arm add-on breakeven earlier.
    """

    pyramid_leg_breakeven_trigger_profit = 0.015


class DualTrendCompressionCloseQualityGuard028PyramidWindow03To12LegBe015Strategy(
    DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardLegBe015Strategy,
):
    """
    Earlier / tighter add-on window for stronger momentum continuation only.
    """

    pyramid_profit_threshold = 0.003
    pyramid_profit_cap = 0.012


class DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy(
    DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardLegBe015Strategy,
):
    """
    Slightly tighter add-on window than the current baseline.
    """

    pyramid_profit_threshold = 0.005
    pyramid_profit_cap = 0.015


class DualTrendCombinedShortPullbackShapeV1Strategy(DualTrendRawStrategy):
    """Backward-compatible alias for the old raw strategy name."""


class DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy(
    DualTrendBaselineStrategy
):
    """Backward-compatible alias for the old baseline strategy name."""


class DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy(DualTrendGuardStrategy):
    """Backward-compatible alias for the old guard strategy name."""


