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


def _filled_bool(series: pd.Series, default: bool = False) -> pd.Series:
    """Normalize merged informative boolean columns without implicit downcasting."""
    return series.astype("boolean").fillna(default).astype(bool)


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
        dataframe["ret_6h"] = dataframe["close"] / dataframe["close"].shift(6) - 1.0
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
            center_down_1d = _filled_bool(
                dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index))
            )
            center_up_1d = _filled_bool(
                dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index))
            )
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
                _filled_bool(dataframe.get("daily_momentum_long_1d", pd.Series(False, index=dataframe.index)))
                & _filled_bool(dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index)))
                & _filled_bool(dataframe.get("center_up_1d", pd.Series(False, index=dataframe.index)))
            )
            if self.use_long_btc_trend_filter and metadata["pair"] != "BTC/USDT:USDT":
                allow_long &= _filled_bool(
                    dataframe.get("btc_trend_up_4h", pd.Series(False, index=dataframe.index))
                )

            reject_long = long_entry & ~allow_long
            dataframe.loc[reject_long, "enter_long"] = 0
            dataframe.loc[reject_long, "enter_tag"] = None
            dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
            dataframe.loc[reject_long, "enter_risk_pct"] = np.nan

        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        if self.long_filter_mode != "none" and long_entry.any():
            center_down_1d = _filled_bool(
                dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index))
            )
            center_up_1d = _filled_bool(
                dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index))
            )
            market_center_1d = dataframe.get("legacy_market_center_1d", pd.Series(np.nan, index=dataframe.index))
            close_below_center = dataframe["close"] < market_center_1d
            close_above_center = dataframe["close"] > market_center_1d

            if self.long_filter_mode == "reject_clear_downtrend":
                reject_long = long_entry & center_down_1d & close_below_center
            elif self.long_filter_mode == "require_4h_trend_up":
                allow_long = _filled_bool(
                    dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index))
                )
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
            center_down_1d = _filled_bool(
                dataframe.get("legacy_center_down_1d", pd.Series(False, index=dataframe.index))
            )
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
            center_up_1d = _filled_bool(
                dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index))
            )
            range_contracting_1d = _filled_bool(
                dataframe.get("range_contracting_1d", pd.Series(False, index=dataframe.index))
            )
            streak = pd.Series(0, index=dataframe.index, dtype="int64")
            for i in range(1, self.long_center_streak_min + 1):
                streak += _filled_bool(center_up_1d.shift(i - 1)).astype("int64")
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


class _DualTrendPyramidClosePositionFloorMixin:
    """Avoid adding on flush candles that close at the extreme low."""

    pyramid_require_close_position_min = 0.07

    def _pyramid_extra_filters_pass(self, pair: str, trade: Trade) -> bool:
        if not super()._pyramid_extra_filters_pass(pair, trade):
            return False
        candle = self._current_candle(pair)
        if candle is None:
            return False
        close_position = float(candle.get("close_position", np.nan))
        return bool(
            np.isfinite(close_position)
            and close_position >= self.pyramid_require_close_position_min
        )


class DualTrendPyramidCloseFloor07V1Strategy(
    _DualTrendPyramidClosePositionFloorMixin,
    DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy,
):
    """Current candidate plus one diagnosed anti-flush add-on filter."""


class _DualTrendSecondAddMixin:
    """
    Research layer for a second winner add-on.

    The base strategy already handles multiple add-on legs and leg-level
    breakeven state. This layer only makes the second leg smaller and later.
    """

    max_entry_position_adjustment = 2
    pyramid_max_additions = 2
    pyramid_leg_stake_fractions = (0.25, 0.12)
    pyramid_second_profit_threshold = 0.018
    pyramid_second_profit_cap = 0.035
    pyramid_second_require_trend_down_4h = False
    pyramid_second_require_center_down = False

    def _pyramid_stake_amount(
        self,
        trade: Trade,
        min_stake: Optional[float],
        max_stake: float,
    ) -> float:
        getter = getattr(trade, "get_custom_data", None)
        setter = getattr(trade, "set_custom_data", None)
        additions_done = int(getter(key="dualtrend_pyramid_additions") or 0) if getter else 0

        base_stake = None
        if getter is not None:
            stored = getter(key="dualtrend_initial_stake_amount")
            if stored is not None:
                base_stake = float(stored)
        if base_stake is None:
            base_stake = float(trade.stake_amount)
            if setter is not None:
                setter(key="dualtrend_initial_stake_amount", value=base_stake)

        fractions = tuple(getattr(self, "pyramid_leg_stake_fractions", (self.pyramid_stake_fraction,)))
        fraction = fractions[min(additions_done, len(fractions) - 1)] if fractions else self.pyramid_stake_fraction
        stake = min(float(max_stake), base_stake * float(fraction))
        if min_stake is not None and stake < min_stake:
            return 0.0
        return max(0.0, stake)

    def _pyramid_extra_filters_pass(self, pair: str, trade: Trade) -> bool:
        if not super()._pyramid_extra_filters_pass(pair, trade):
            return False

        getter = getattr(trade, "get_custom_data", None)
        additions_done = int(getter(key="dualtrend_pyramid_additions") or 0) if getter else 0
        if additions_done < 1:
            return True

        candle = self._current_candle(pair)
        if candle is None:
            return False
        if self.pyramid_second_require_trend_down_4h and not bool(candle.get("trend_down_4h", False)):
            return False
        if self.pyramid_second_require_center_down and not bool(candle.get("center_down", False)):
            return False
        return True

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
        if getter is not None and int(getter(key="dualtrend_pyramid_additions") or 0) >= 1:
            original_threshold = self.pyramid_profit_threshold
            original_cap = self.pyramid_profit_cap
            self.pyramid_profit_threshold = self.pyramid_second_profit_threshold
            self.pyramid_profit_cap = self.pyramid_second_profit_cap
            try:
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
            finally:
                self.pyramid_profit_threshold = original_threshold
                self.pyramid_profit_cap = original_cap

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


class DualTrendPyramidSecondAdd15V1Strategy(
    _DualTrendSecondAddMixin,
    DualTrendPyramidCloseFloor07V1Strategy,
):
    """CloseFloor07 plus a 15% second add-on after stronger confirmation."""

    pyramid_leg_stake_fractions = (0.25, 0.15)


class DualTrendPyramidSecondAdd20V1Strategy(DualTrendPyramidSecondAdd15V1Strategy):
    """CloseFloor07 plus a larger 20% second add-on after stronger confirmation."""

    pyramid_leg_stake_fractions = (0.25, 0.20)


class _DualTrendLongExpansionMixin:
    """Add independently testable 1h long continuations without touching short entries."""

    enable_long_pullback_restart_1h = True
    enable_long_compression_breakout_1h = True
    # Do not override the parent daily-long breakout buffer (0.009).
    long_expansion_breakout_buffer = 0.001
    long_close_position_min = 0.60
    long_pullback_min_depth_1h = 0.008
    long_pullback_max_depth_1h = 0.08
    long_pullback_ema50_buffer = 0.01
    long_stop_atr_buffer = 0.20
    long_pullback_deep_depth_1h = 0.025
    long_volume_expansion_strong = 1.30
    long_body_expansion_strong = 0.70

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata).copy()
        hw = self.compression_half_window
        cw = self.compression_window

        dataframe["low_min_first_half"] = dataframe["low"].shift(hw + 1).rolling(hw).min()
        dataframe["low_min_last_half"] = dataframe["low"].shift(1).rolling(hw).min()
        dataframe["long_center_up_1h"] = (
            (dataframe["low_min_last_half"] > dataframe["low_min_first_half"])
            & (dataframe["close_mean_last_half"] > dataframe["close_mean_first_half"])
        )
        dataframe["breakout_long_1h"] = dataframe["close"] > dataframe["compression_high"] * (
            1 + self.long_expansion_breakout_buffer
        )
        dataframe["near_high_zone_long"] = dataframe["close"].shift(1) >= dataframe[
            "compression_high"
        ] * 0.985
        dataframe["recent_high_24"] = dataframe["high"].shift(1).rolling(self.pretrend_window).max()
        dataframe["pullback_low_12_long"] = dataframe["low"].shift(1).rolling(cw).min()
        dataframe["pullback_depth_long_1h"] = (
            dataframe["recent_high_24"] - dataframe["pullback_low_12_long"]
        ) / dataframe["recent_high_24"]
        dataframe["pullback_seen_long_1h"] = dataframe["pullback_depth_long_1h"].between(
            self.long_pullback_min_depth_1h,
            self.long_pullback_max_depth_1h,
        )
        dataframe["pullback_intact_long_1h"] = dataframe["pullback_low_12_long"] >= dataframe[
            "ema50_4h"
        ] * (1 - self.long_pullback_ema50_buffer)
        candle_range = dataframe["high"] - dataframe["low"]
        dataframe["candle_quality_long"] = (
            (candle_range > 0)
            & (dataframe["body_pct_of_range"] >= self.candle_body_min)
            & (dataframe["close_position"] >= self.long_close_position_min)
        )
        dataframe["long_pullback_stop_1h"] = dataframe["pullback_low_12_long"] - (
            self.long_stop_atr_buffer * dataframe["atr_ref"]
        )
        dataframe["long_compression_stop_1h"] = dataframe["compression_low"] - (
            self.long_stop_atr_buffer * dataframe["atr_ref"]
        )
        dataframe["long_pullback_risk_pct_ok_1h"] = (
            (dataframe["close"] - dataframe["long_pullback_stop_1h"]) / dataframe["close"]
        ).between(self.min_stop_distance, self.max_stop_distance)
        dataframe["long_compression_risk_pct_ok_1h"] = (
            (dataframe["close"] - dataframe["long_compression_stop_1h"]) / dataframe["close"]
        ).between(self.min_stop_distance, self.max_stop_distance)
        dataframe["long_pullback_deep_1h"] = (
            dataframe["pullback_depth_long_1h"] >= self.long_pullback_deep_depth_1h
        )
        dataframe["long_above_1d_center"] = dataframe["close"] > dataframe.get(
            "legacy_market_center_1d",
            pd.Series(np.nan, index=dataframe.index),
        )
        dataframe["long_1d_center_up"] = _filled_bool(
            dataframe.get("legacy_center_up_1d", pd.Series(False, index=dataframe.index))
        )
        dataframe["long_strong_trend_context"] = (
            dataframe["long_1d_center_up"]
            & dataframe["long_above_1d_center"].fillna(False)
            & _filled_bool(dataframe.get("daily_momentum_long_1d", pd.Series(False, index=dataframe.index)))
        )
        dataframe["long_volume_expansion_strong"] = (
            dataframe["volume"] >= dataframe["volume_ma20"] * self.long_volume_expansion_strong
        )
        dataframe["long_candle_expansion_strong"] = (
            dataframe["body_pct_of_range"] >= self.long_body_expansion_strong
        )
        dataframe["btc_filter_long_ok"] = True
        if self.use_btc_filter and metadata["pair"] != "BTC/USDT:USDT":
            dataframe["btc_filter_long_ok"] = _filled_bool(
                dataframe.get("btc_trend_up_4h", pd.Series(False, index=dataframe.index))
            )
        return dataframe

    @staticmethod
    def _append_long_tag_suffix(
        dataframe: DataFrame,
        mask: pd.Series,
        base_tag: str,
        suffix_rules: tuple[tuple[str, pd.Series], ...],
    ) -> pd.Series:
        tags = pd.Series(base_tag, index=dataframe.index, dtype="object")
        for suffix, suffix_mask in suffix_rules:
            tags.loc[mask & suffix_mask.fillna(False)] = tags.loc[mask & suffix_mask.fillna(False)] + suffix
        return tags.loc[mask]

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata).copy()
        if metadata["pair"] not in self.trade_pair_allowlist:
            return dataframe

        no_existing_entry = (
            dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(0)
            & dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(0)
        )
        trend_up_4h = _filled_bool(
            dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index))
        )
        btc_filter = _filled_bool(dataframe["btc_filter_long_ok"])
        ema20_rising = dataframe["ema20_1h"] > dataframe["ema20_1h_prev"]
        base = (
            trend_up_4h
            & dataframe["long_center_up_1h"].fillna(False)
            & (dataframe["close"] > dataframe["ema20_1h"])
            & ema20_rising
            & dataframe["breakout_long_1h"].fillna(False)
            & dataframe["vol_ok"].fillna(False)
            & dataframe["candle_quality_long"].fillna(False)
            & btc_filter
            & (dataframe["volume"] > 0)
        )
        pullback_restart = (
            self.enable_long_pullback_restart_1h
            & base
            & dataframe["pullback_seen_long_1h"].fillna(False)
            & dataframe["pullback_intact_long_1h"].fillna(False)
            & dataframe["long_pullback_risk_pct_ok_1h"].fillna(False)
        )
        compression_breakout = (
            self.enable_long_compression_breakout_1h
            & base
            & ~pullback_restart
            & dataframe["compression_ok"].fillna(False)
            & dataframe["near_high_zone_long"].fillna(False)
            & dataframe["long_compression_risk_pct_ok_1h"].fillna(False)
        )

        pullback_entry = no_existing_entry & pullback_restart
        compression_entry = no_existing_entry & compression_breakout
        pullback_tag = self._append_long_tag_suffix(
            dataframe,
            pullback_entry,
            "long_pullback_restart_1h",
            (
                ("_deep", dataframe["long_pullback_deep_1h"]),
                ("_dailyconfirm", dataframe["long_strong_trend_context"]),
                ("_vol", dataframe["long_volume_expansion_strong"]),
                ("_body", dataframe["long_candle_expansion_strong"]),
            ),
        )
        compression_tag = self._append_long_tag_suffix(
            dataframe,
            compression_entry,
            "long_compression_breakout_1h",
            (
                ("_dailyconfirm", dataframe["long_strong_trend_context"]),
                ("_vol", dataframe["long_volume_expansion_strong"]),
                ("_body", dataframe["long_candle_expansion_strong"]),
            ),
        )
        dataframe.loc[pullback_entry, "enter_long"] = 1
        dataframe.loc[pullback_entry, "enter_tag"] = pullback_tag
        dataframe.loc[pullback_entry, "enter_initial_stop"] = dataframe.loc[
            pullback_entry,
            "long_pullback_stop_1h",
        ].astype("float32")
        dataframe.loc[pullback_entry, "enter_risk_pct"] = (
            (dataframe.loc[pullback_entry, "close"] - dataframe.loc[pullback_entry, "long_pullback_stop_1h"])
            / dataframe.loc[pullback_entry, "close"]
        ).astype("float32")
        dataframe.loc[compression_entry, "enter_long"] = 1
        dataframe.loc[compression_entry, "enter_tag"] = compression_tag
        dataframe.loc[compression_entry, "enter_initial_stop"] = dataframe.loc[
            compression_entry,
            "long_compression_stop_1h",
        ].astype("float32")
        dataframe.loc[compression_entry, "enter_risk_pct"] = (
            (dataframe.loc[compression_entry, "close"] - dataframe.loc[compression_entry, "long_compression_stop_1h"])
            / dataframe.loc[compression_entry, "close"]
        ).astype("float32")
        return dataframe


class DualTrendLongExpansionPullbackBodyOnlyV1Strategy(
    _DualTrendLongExpansionMixin,
    DualTrendPyramidSecondAdd20V1Strategy,
):
    """Test only 1h long pullback restarts with a strong breakout candle body."""

    enable_long_compression_breakout_1h = False

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata).copy()
        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        enter_tag = dataframe.get("enter_tag", pd.Series("", index=dataframe.index)).fillna("")
        reject_long = (
            long_entry
            & enter_tag.str.startswith("long_pullback_restart_1h")
            & ~enter_tag.str.contains("_body", regex=False)
        )
        dataframe.loc[reject_long, "enter_long"] = 0
        dataframe.loc[reject_long, "enter_tag"] = None
        dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
        dataframe.loc[reject_long, "enter_risk_pct"] = np.nan
        return dataframe


class DualTrendLongExpansionPullbackBodyMicroV1Strategy(
    DualTrendLongExpansionPullbackBodyOnlyV1Strategy
):
    """Allow only the rarest non-deep strong-body 1h long add-on."""

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata).copy()
        long_entry = dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(1)
        enter_tag = dataframe.get("enter_tag", pd.Series("", index=dataframe.index)).fillna("")
        reject_long = (
            long_entry
            & enter_tag.str.startswith("long_pullback_restart_1h")
            & ~enter_tag.eq("long_pullback_restart_1h_body")
        )
        dataframe.loc[reject_long, "enter_long"] = 0
        dataframe.loc[reject_long, "enter_tag"] = None
        dataframe.loc[reject_long, "enter_initial_stop"] = np.nan
        dataframe.loc[reject_long, "enter_risk_pct"] = np.nan
        return dataframe


class DualTrendPyramidSecondAdd20LongMicroV1Strategy(
    DualTrendLongExpansionPullbackBodyMicroV1Strategy
):
    """SecondAdd20 plus the validated rare non-deep strong-body 1h long."""


class DualTrendPyramidSecondAdd20LongMicroShortOnlyV1Strategy(
    DualTrendPyramidSecondAdd20LongMicroV1Strategy
):
    """Experimental short engine for split-capital portfolio reconstruction."""

    enable_long_daily_center = False
    enable_long_pullback_restart_1h = False
    enable_long_compression_breakout_1h = False


class DualTrendPyramidSecondAdd20LongMicroLongOnlyV1Strategy(
    DualTrendPyramidSecondAdd20LongMicroV1Strategy
):
    """Experimental long engine for split-capital portfolio reconstruction."""

    enable_short_pullback_restart = False
    enable_short_compression_breakdown = False


class _DualTrendSideSlotLimitMixin:
    """Limit open trades by direction while retaining the global slot ceiling."""

    max_open_short_slots = 3
    max_open_long_slots = 1

    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> bool:
        if not super().confirm_trade_entry(
            pair=pair,
            order_type=order_type,
            amount=amount,
            rate=rate,
            time_in_force=time_in_force,
            current_time=current_time,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        ):
            return False

        open_trades = Trade.get_trades_proxy(is_open=True)
        if side == "short":
            return sum(bool(trade.is_short) for trade in open_trades) < self.max_open_short_slots
        if side == "long":
            return sum(not bool(trade.is_short) for trade in open_trades) < self.max_open_long_slots
        return False


class DualTrendPyramidSecondAdd20LongMicroSideSlots3S1LV1Strategy(
    _DualTrendSideSlotLimitMixin,
    DualTrendPyramidSecondAdd20LongMicroV1Strategy,
):
    """Experimental max4 portfolio with at most three shorts and one long."""


class _DualTrendHigherLowReclaimMixin:
    """Add a confirmed higher-low plus neckline-reclaim long experiment."""

    higher_low_only = False
    higher_low_pivot_span = 2
    higher_low_min_separation = 4
    higher_low_max_separation = 24
    higher_low_min_lift_atr = 0.05
    higher_low_max_lift_atr = 2.0
    higher_low_min_rebound_atr = 1.0
    higher_low_max_age = 8
    higher_low_breakout_buffer = 0.001
    higher_low_stop_atr_buffer = 0.20
    higher_low_close_position_min = 0.60

    def _populate_higher_low_structure(self, dataframe: DataFrame) -> DataFrame:
        size = len(dataframe)
        trigger = np.zeros(size, dtype=bool)
        neckline_values = np.full(size, np.nan, dtype=float)
        second_low_values = np.full(size, np.nan, dtype=float)
        stop_values = np.full(size, np.nan, dtype=float)
        separation_values = np.full(size, np.nan, dtype=float)
        lift_atr_values = np.full(size, np.nan, dtype=float)
        rebound_atr_values = np.full(size, np.nan, dtype=float)

        lows = dataframe["low"].to_numpy(dtype=float, copy=False)
        highs = dataframe["high"].to_numpy(dtype=float, copy=False)
        closes = dataframe["close"].to_numpy(dtype=float, copy=False)
        atr_values = dataframe["atr_ref"].to_numpy(dtype=float, copy=False)
        span = int(self.higher_low_pivot_span)
        pivots: list[tuple[int, float]] = []
        active: Optional[dict[str, float | int]] = None

        for current_idx in range(span * 2, size):
            pivot_idx = current_idx - span
            pivot_window = lows[pivot_idx - span : pivot_idx + span + 1]
            pivot_low = lows[pivot_idx]
            if (
                len(pivot_window) == span * 2 + 1
                and np.isfinite(pivot_window).all()
                and pivot_low < np.min(pivot_window[:span])
                and pivot_low <= np.min(pivot_window[span + 1 :])
            ):
                if pivots and pivot_idx - pivots[-1][0] > self.higher_low_max_separation:
                    pivots = []
                if pivots:
                    first_idx, first_low = pivots[-1]
                    separation = pivot_idx - first_idx
                    atr_at_pivot = atr_values[pivot_idx]
                    if (
                        self.higher_low_min_separation <= separation <= self.higher_low_max_separation
                        and np.isfinite(atr_at_pivot)
                        and atr_at_pivot > 0
                    ):
                        neckline = float(np.max(highs[first_idx + 1 : pivot_idx]))
                        lift_atr = (pivot_low - first_low) / atr_at_pivot
                        rebound_atr = (neckline - pivot_low) / atr_at_pivot
                        if (
                            self.higher_low_min_lift_atr <= lift_atr <= self.higher_low_max_lift_atr
                            and rebound_atr >= self.higher_low_min_rebound_atr
                        ):
                            active = {
                                "pivot_idx": pivot_idx,
                                "neckline": neckline,
                                "second_low": pivot_low,
                                "separation": separation,
                                "lift_atr": lift_atr,
                                "rebound_atr": rebound_atr,
                            }
                pivots.append((pivot_idx, pivot_low))

            if active is None:
                continue

            second_idx = int(active["pivot_idx"])
            second_low = float(active["second_low"])
            neckline = float(active["neckline"])
            if current_idx - second_idx > self.higher_low_max_age or lows[current_idx] < second_low:
                active = None
                continue

            neckline_values[current_idx] = neckline
            second_low_values[current_idx] = second_low
            separation_values[current_idx] = float(active["separation"])
            lift_atr_values[current_idx] = float(active["lift_atr"])
            rebound_atr_values[current_idx] = float(active["rebound_atr"])
            if np.isfinite(atr_values[current_idx]):
                stop_values[current_idx] = second_low - (
                    self.higher_low_stop_atr_buffer * atr_values[current_idx]
                )

            breakout_level = neckline * (1 + self.higher_low_breakout_buffer)
            previous_close = closes[current_idx - 1]
            if closes[current_idx] > breakout_level and previous_close <= breakout_level:
                trigger[current_idx] = True
                active = None

        structure_columns = DataFrame(
            {
                "higher_low_reclaim_1h": trigger,
                "higher_low_neckline_1h": neckline_values,
                "higher_low_second_low_1h": second_low_values,
                "higher_low_stop_1h": stop_values,
                "higher_low_separation_1h": separation_values,
                "higher_low_lift_atr_1h": lift_atr_values,
                "higher_low_rebound_atr_1h": rebound_atr_values,
            },
            index=dataframe.index,
        )
        return pd.concat([dataframe, structure_columns], axis=1)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata).copy()
        return self._populate_higher_low_structure(dataframe)

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata).copy()
        if self.higher_low_only:
            dataframe["enter_long"] = 0
            dataframe["enter_short"] = 0
            dataframe["enter_tag"] = None
            dataframe["enter_initial_stop"] = np.nan
            dataframe["enter_risk_pct"] = np.nan

        if metadata["pair"] not in self.trade_pair_allowlist:
            return dataframe

        no_existing_entry = (
            dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(0)
            & dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(0)
        )
        btc_filter = pd.Series(True, index=dataframe.index)
        if self.use_btc_filter and metadata["pair"] != "BTC/USDT:USDT":
            btc_filter = _filled_bool(
                dataframe.get("btc_trend_up_4h", pd.Series(False, index=dataframe.index))
            )

        stop = dataframe["higher_low_stop_1h"]
        risk_pct = (dataframe["close"] - stop) / dataframe["close"]
        risk_ok = risk_pct.between(self.min_stop_distance, self.max_stop_distance)
        candle_quality = (
            (dataframe["body_pct_of_range"] >= self.candle_body_min)
            & (dataframe["close_position"] >= self.higher_low_close_position_min)
        )
        entry = (
            no_existing_entry
            & dataframe["higher_low_reclaim_1h"].fillna(False)
            & _filled_bool(dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index)))
            & (dataframe["close"] > dataframe["ema20_1h"])
            & (dataframe["ema20_1h"] > dataframe["ema20_1h_prev"])
            & dataframe["vol_ok"].fillna(False)
            & candle_quality.fillna(False)
            & risk_ok.fillna(False)
            & btc_filter
            & (dataframe["volume"] > 0)
        )
        dataframe.loc[entry, ["enter_long", "enter_tag"]] = (1, "long_higher_low_reclaim_1h")
        dataframe.loc[entry, "enter_initial_stop"] = stop.loc[entry].astype("float32")
        dataframe.loc[entry, "enter_risk_pct"] = risk_pct.loc[entry].astype("float32")
        return dataframe


class DualTrendPyramidSecondAdd20HigherLowV1Strategy(
    _DualTrendHigherLowReclaimMixin,
    DualTrendPyramidSecondAdd20V1Strategy,
):
    """SecondAdd20 plus the isolated higher-low reclaim experiment."""


class DualTrendHigherLowOnlyV1Strategy(
    _DualTrendHigherLowReclaimMixin,
    DualTrendPyramidSecondAdd20V1Strategy,
):
    """Diagnostic strategy that trades only the higher-low reclaim tag."""

    higher_low_only = True


class DualTrendPyramidSecondAdd20LongMicroHigherLowV1Strategy(
    _DualTrendHigherLowReclaimMixin,
    DualTrendPyramidSecondAdd20LongMicroV1Strategy,
):
    """Current LongMicro candidate plus the higher-low reclaim experiment."""


class _DualTrendFailedBreakdownReclaimMixin:
    """Add a confirmed false-breakdown reclaim long experiment."""

    failed_breakdown_only = False
    failed_breakdown_support_window = 24
    failed_breakdown_min_sweep_atr = 0.05
    failed_breakdown_max_sweep_atr = 0.80
    failed_breakdown_confirm_buffer = 0.001
    failed_breakdown_stop_atr_buffer = 0.20
    failed_breakdown_close_position_min = 0.65

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata).copy()
        support = dataframe["low"].shift(1).rolling(self.failed_breakdown_support_window).min()
        sweep_depth_atr = (support - dataframe["low"]) / dataframe["atr_ref"]
        setup = (
            (dataframe["low"] < support)
            & (dataframe["close"] > support)
            & (dataframe["close"] > dataframe["open"])
            & (dataframe["body_pct_of_range"] >= self.candle_body_min)
            & (dataframe["close_position"] >= self.failed_breakdown_close_position_min)
            & sweep_depth_atr.between(
                self.failed_breakdown_min_sweep_atr,
                self.failed_breakdown_max_sweep_atr,
            )
        )
        previous_low = dataframe["low"].shift(1)
        previous_high = dataframe["high"].shift(1)
        confirmation_level = previous_high * (1 + self.failed_breakdown_confirm_buffer)
        confirmed = (
            _filled_bool(setup.shift(1))
            & (dataframe["close"] > confirmation_level)
            & (dataframe["low"] >= previous_low)
        )
        stop = previous_low - (self.failed_breakdown_stop_atr_buffer * dataframe["atr_ref"])
        dataframe = dataframe.assign(
            failed_breakdown_support_1h=support,
            failed_breakdown_sweep_atr_1h=sweep_depth_atr,
            failed_breakdown_setup_1h=setup,
            failed_breakdown_reclaim_1h=confirmed,
            failed_breakdown_stop_1h=stop,
        )
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata).copy()
        if self.failed_breakdown_only:
            dataframe["enter_long"] = 0
            dataframe["enter_short"] = 0
            dataframe["enter_tag"] = None
            dataframe["enter_initial_stop"] = np.nan
            dataframe["enter_risk_pct"] = np.nan

        if metadata["pair"] not in self.trade_pair_allowlist:
            return dataframe

        no_existing_entry = (
            dataframe.get("enter_long", pd.Series(0, index=dataframe.index)).fillna(0).eq(0)
            & dataframe.get("enter_short", pd.Series(0, index=dataframe.index)).fillna(0).eq(0)
        )
        btc_filter = pd.Series(True, index=dataframe.index)
        if self.use_btc_filter and metadata["pair"] != "BTC/USDT:USDT":
            btc_filter = _filled_bool(
                dataframe.get("btc_trend_up_4h", pd.Series(False, index=dataframe.index))
            )

        stop = dataframe["failed_breakdown_stop_1h"]
        risk_pct = (dataframe["close"] - stop) / dataframe["close"]
        risk_ok = risk_pct.between(self.min_stop_distance, self.max_stop_distance)
        entry = (
            no_existing_entry
            & dataframe["failed_breakdown_reclaim_1h"].fillna(False)
            & _filled_bool(dataframe.get("trend_up_4h", pd.Series(False, index=dataframe.index)))
            & (dataframe["close"] > dataframe["ema20_1h"])
            & (dataframe["ema20_1h"] > dataframe["ema20_1h_prev"])
            & dataframe["vol_ok"].fillna(False)
            & risk_ok.fillna(False)
            & btc_filter
            & (dataframe["volume"] > 0)
        )
        dataframe.loc[entry, ["enter_long", "enter_tag"]] = (1, "long_failed_breakdown_reclaim_1h")
        dataframe.loc[entry, "enter_initial_stop"] = stop.loc[entry].astype("float32")
        dataframe.loc[entry, "enter_risk_pct"] = risk_pct.loc[entry].astype("float32")
        return dataframe


class DualTrendFailedBreakdownOnlyV1Strategy(
    _DualTrendFailedBreakdownReclaimMixin,
    DualTrendPyramidSecondAdd20V1Strategy,
):
    """Diagnostic strategy that trades only the false-breakdown reclaim tag."""

    failed_breakdown_only = True


class DualTrendPyramidSecondAdd20FailedBreakdownV1Strategy(
    _DualTrendFailedBreakdownReclaimMixin,
    DualTrendPyramidSecondAdd20V1Strategy,
):
    """SecondAdd20 plus the false-breakdown reclaim experiment."""


class DualTrendCombinedShortPullbackShapeV1Strategy(DualTrendRawStrategy):
    """Backward-compatible alias for the old raw strategy name."""


class DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy(
    DualTrendBaselineStrategy
):
    """Backward-compatible alias for the old baseline strategy name."""


class DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy(DualTrendGuardStrategy):
    """Backward-compatible alias for the old guard strategy name."""


