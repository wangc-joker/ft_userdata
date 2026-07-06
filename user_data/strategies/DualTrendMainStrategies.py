from __future__ import annotations

from datetime import timezone
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import informative

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


class _DualTrendTagProfitLockMixin(_DualTrendReach5ConditionalMixin):
    """
    Tag-specific profit-lock research layer.

    This adds trailing-profit style exits without changing entry logic, pair pool,
    leverage, stop placement, or max_open_trades.
    """

    @staticmethod
    def _max_profit_seen(trade: Trade, current_profit: float) -> float:
        open_rate = max(float(trade.open_rate or 0.0), 1e-12)
        if bool(getattr(trade, "is_short", False)):
            min_rate = float(getattr(trade, "min_rate", open_rate) or open_rate)
            profit = open_rate / max(min_rate, 1e-12) - 1.0
        else:
            max_rate = float(getattr(trade, "max_rate", open_rate) or open_rate)
            profit = max_rate / open_rate - 1.0
        return max(float(current_profit), float(profit), 0.0)

    def _supports_trade_direction(self, pair: str, trade: Trade) -> bool:
        candle = self._current_candle(pair)
        if candle is None:
            return True
        if bool(getattr(trade, "is_short", False)):
            return bool(candle.get("trend_down_4h", False))
        return bool(candle.get("trend_up_4h", False))

    def _update_mfe_state(self, trade: Trade, current_time, current_profit: float) -> tuple[float, Optional[pd.Timestamp]]:
        getter = getattr(trade, "get_custom_data", None)
        setter = getattr(trade, "set_custom_data", None)
        max_profit_seen = self._max_profit_seen(trade, current_profit)
        if getter is None or setter is None:
            return max_profit_seen, None

        stored_profit = getter(key="dualtrend_profit_lock_max_profit")
        stored_profit = float(stored_profit) if stored_profit is not None else None
        stored_time_raw = getter(key="dualtrend_profit_lock_last_mfe_time")
        last_mfe_time = pd.Timestamp(stored_time_raw) if stored_time_raw else None
        improved = stored_profit is None or max_profit_seen > stored_profit + 1e-9
        if improved:
            setter(key="dualtrend_profit_lock_max_profit", value=float(max_profit_seen))
            setter(key="dualtrend_profit_lock_last_mfe_time", value=pd.Timestamp(current_time).isoformat())
            last_mfe_time = pd.Timestamp(current_time)
        elif stored_profit is not None:
            max_profit_seen = max(max_profit_seen, stored_profit)
        return max_profit_seen, last_mfe_time

    def _base_tag_lock_profit(self, tag: str, max_profit_seen: float) -> Optional[float]:
        lock_profit: Optional[float] = None
        if tag == "short_pullback_restart":
            if max_profit_seen >= 0.02:
                lock_profit = 0.003
            if max_profit_seen >= 0.04:
                lock_profit = max(lock_profit or 0.0, 0.008, max_profit_seen * 0.35)
            if max_profit_seen >= 0.08:
                lock_profit = max(lock_profit or 0.0, 0.025, max_profit_seen * 0.50)
        elif tag == "short_compression_breakdown":
            if max_profit_seen >= 0.015:
                lock_profit = 0.003
            if max_profit_seen >= 0.03:
                lock_profit = max(lock_profit or 0.0, 0.010, max_profit_seen * 0.45)
            if max_profit_seen >= 0.05:
                lock_profit = max(lock_profit or 0.0, 0.020, max_profit_seen * 0.60)
        elif tag == "long_1d_center_compression":
            if max_profit_seen >= 0.03:
                lock_profit = 0.005
            if max_profit_seen >= 0.06:
                lock_profit = max(lock_profit or 0.0, 0.015, max_profit_seen * 0.35)
            if max_profit_seen >= 0.10:
                lock_profit = max(lock_profit or 0.0, 0.035, max_profit_seen * 0.50)
        return lock_profit

    def _tag_profit_lock_exit_reason(self, tag: str) -> Optional[str]:
        if tag == "short_pullback_restart":
            return "profit_lock_pullback_restart"
        if tag == "short_compression_breakdown":
            return "profit_lock_compression_breakdown"
        if tag == "long_1d_center_compression":
            return "profit_lock_long_center"
        return None

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        tag = self._trade_enter_tag(trade) or ""
        max_profit_seen, last_mfe_time = self._update_mfe_state(trade, current_time, current_profit)
        lock_profit = self._base_tag_lock_profit(tag, max_profit_seen)

        if max_profit_seen >= 0.05 and current_profit <= max_profit_seen * 0.40:
            return "profit_giveback_guard"

        age_hours = self._elapsed_hours_since_open(trade, current_time)
        if (
            lock_profit is not None
            and age_hours > 48.0
            and current_profit > 0.015
            and last_mfe_time is not None
            and (pd.Timestamp(current_time) - last_mfe_time).total_seconds() >= 24 * 3600
        ):
            lock_profit = max(lock_profit, current_profit * 0.70)

        if (
            age_hours > 72.0
            and current_profit > 0.008
            and not self._supports_trade_direction(pair, trade)
        ):
            return "time_decay_profit_exit"

        tag_exit_reason = self._tag_profit_lock_exit_reason(tag)
        if lock_profit is not None and tag_exit_reason and current_profit <= lock_profit:
            return tag_exit_reason

        return super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )


class _DualTrendStructureFailureExitMixin(_DualTrendReach5ConditionalMixin):
    """
    Research exit layer for profitable trades that start to lose local structure.

    Core idea:
    - keep the +2% breakeven protection from the base strategy
    - only intervene once the trade is already meaningfully profitable
    - exit when a profitable move pauses in a tight range, attempts continuation,
      fails back into the range, and the local 1h center shifts against us
    """

    structure_exit_enable = True
    structure_profit_activation = 0.02
    structure_range_lookback = 6
    structure_breakout_lookback = 3
    structure_range_atr_mult = 2.6
    structure_range_width_pct_max = 0.03
    structure_break_buffer = 0.001
    structure_center_shift_bars = 2
    structure_ret1h_confirm = 0.002

    def _recent_structure_snapshot(self, pair: str) -> Optional[dict]:
        if not self.dp:
            return None
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        need = self.structure_range_lookback + self.structure_breakout_lookback + 2
        if len(dataframe) < need:
            return None

        current = dataframe.iloc[-1]
        # Range is measured on the six candles before the recent breakout/failure window.
        range_end = len(dataframe) - self.structure_breakout_lookback - 1
        range_start = range_end - self.structure_range_lookback
        if range_start < 0:
            return None

        range_slice = dataframe.iloc[range_start:range_end]
        recent_slice = dataframe.iloc[range_end : len(dataframe)]
        if range_slice.empty or recent_slice.empty:
            return None

        range_high = float(range_slice["high"].max())
        range_low = float(range_slice["low"].min())
        close = float(current.get("close", np.nan))
        atr_ref = float(current.get("atr_ref", np.nan))
        ema20 = float(current.get("ema20_1h", np.nan))
        if not np.isfinite(close) or close <= 0 or not np.isfinite(range_high) or not np.isfinite(range_low):
            return None

        range_width = max(0.0, range_high - range_low)
        width_pct = range_width / close
        atr_ok = np.isfinite(atr_ref) and range_width <= atr_ref * self.structure_range_atr_mult
        width_ok = width_pct <= self.structure_range_width_pct_max

        recent_high = float(recent_slice["high"].max())
        recent_low = float(recent_slice["low"].min())
        center_now = float(current.get("legacy_market_center", np.nan))
        if not np.isfinite(center_now):
            center_now = close
        center_prev_src = dataframe["legacy_market_center"].dropna()
        if len(center_prev_src) >= self.structure_center_shift_bars + 1:
            center_prev = float(center_prev_src.iloc[-(self.structure_center_shift_bars + 1)])
        else:
            center_prev = center_now
        ret_1h = float(current.get("ret_1h", 0.0) or 0.0)
        center_up = center_now > center_prev
        center_down = center_now < center_prev

        return {
            "close": close,
            "ema20": ema20,
            "range_high": range_high,
            "range_low": range_low,
            "range_ok": bool(atr_ok and width_ok),
            "recent_high": recent_high,
            "recent_low": recent_low,
            "center_up": center_up,
            "center_down": center_down,
            "ret_1h": ret_1h,
        }

    def _structure_failure_exit_reason(self, pair: str, trade: Trade, current_profit: float) -> Optional[str]:
        if not self.structure_exit_enable or current_profit < self.structure_profit_activation:
            return None

        snapshot = self._recent_structure_snapshot(pair)
        if snapshot is None or not snapshot["range_ok"]:
            return None

        close = snapshot["close"]
        ema20 = snapshot["ema20"]
        range_high = snapshot["range_high"]
        range_low = snapshot["range_low"]
        breakout_up_failed = (
            snapshot["recent_high"] >= range_high * (1 + self.structure_break_buffer)
            and close <= range_high
        )
        breakdown_failed = (
            snapshot["recent_low"] <= range_low * (1 - self.structure_break_buffer)
            and close >= range_low
        )

        tag = self._trade_enter_tag(trade) or ""
        is_short = bool(getattr(trade, "is_short", False))
        if is_short:
            if breakdown_failed and snapshot["center_up"] and np.isfinite(ema20) and close >= ema20:
                return "structure_exit_short_failed_breakdown"
            if (
                current_profit >= max(self.structure_profit_activation, 0.03)
                and snapshot["center_up"]
                and np.isfinite(ema20)
                and close >= ema20
                and snapshot["ret_1h"] >= self.structure_ret1h_confirm
            ):
                return "structure_exit_short_countertrend"
            return None

        if breakout_up_failed and snapshot["center_down"] and np.isfinite(ema20) and close <= ema20:
            return "structure_exit_long_failed_breakout"
        if (
            current_profit >= max(self.structure_profit_activation, 0.03)
            and snapshot["center_down"]
            and np.isfinite(ema20)
            and close <= ema20
            and snapshot["ret_1h"] <= -self.structure_ret1h_confirm
        ):
            return "structure_exit_long_countertrend"
        return None

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        structure_reason = self._structure_failure_exit_reason(pair, trade, current_profit)
        if structure_reason:
            return structure_reason
        return super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )


class _DualTrendEarlyFailExitMixin(_DualTrendReach5ConditionalMixin):
    """
    Phase 1A research layer.

    Only adds short-side early-fail exits during the first few hours after entry.
    The goal is to cut false breakdown / quick reverse trades earlier without
    changing entry logic, stop placement, or the main reach5 handling.
    """

    early_fail_enable = True
    early_fail_short_window_hours = 6.0
    early_fail_trend_flip_window_hours = 3.0
    early_fail_profit_cap = 0.01
    early_fail_close_vs_ema20_min = 0.0
    early_fail_need_center_up = True

    def _current_center_direction(self, pair: str, bars: int = 2) -> int:
        if not self.dp:
            return 0
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty or "legacy_market_center" not in dataframe:
            return 0
        valid = dataframe["legacy_market_center"].dropna()
        if len(valid) < bars + 1:
            return 0
        current = float(valid.iloc[-1])
        previous = float(valid.iloc[-(bars + 1)])
        if current > previous:
            return 1
        if current < previous:
            return -1
        return 0

    def _close_vs_ema20_now(self, pair: str) -> float:
        candle = self._current_candle(pair)
        if candle is None:
            return 0.0
        ema20 = candle.get("ema20_1h", np.nan)
        close = candle.get("close", np.nan)
        if pd.isna(ema20) or pd.isna(close) or float(ema20) == 0.0:
            return 0.0
        return (float(close) - float(ema20)) / float(ema20)

    def _short_reclaimed_breakdown_range(self, pair: str) -> bool:
        candle = self._current_candle(pair)
        if candle is None:
            return False
        compression_low = candle.get("compression_low", np.nan)
        close = candle.get("close", np.nan)
        if pd.isna(compression_low) or pd.isna(close):
            return False
        return float(close) >= float(compression_low)

    def _btc_short_support_lost(self, pair: str) -> bool:
        if pair == "BTC/USDT:USDT":
            return False
        candle = self._current_candle(pair)
        if candle is None:
            return False
        return bool(candle.get("btc_trend_up_4h", False))

    def _supports_trade_direction(self, pair: str, trade: Trade) -> bool:
        candle = self._current_candle(pair)
        if candle is None:
            return True
        if bool(getattr(trade, "is_short", False)):
            return bool(candle.get("trend_down_4h", False))
        return bool(candle.get("trend_up_4h", False))

    def _early_fail_short_reason(self, pair: str, trade: Trade, current_time, current_profit: float) -> Optional[str]:
        if not self.early_fail_enable or not bool(getattr(trade, "is_short", False)):
            return None

        tag = self._trade_enter_tag(trade) or ""
        if tag not in {"short_pullback_restart", "short_compression_breakdown"}:
            return None

        age_hours = self._elapsed_hours_since_open(trade, current_time)
        if age_hours > self.early_fail_short_window_hours or current_profit > self.early_fail_profit_cap:
            return None

        center_dir = self._current_center_direction(pair)
        close_vs_ema20 = self._close_vs_ema20_now(pair)
        reclaimed_range = self._short_reclaimed_breakdown_range(pair)
        center_up_ok = (center_dir > 0) if self.early_fail_need_center_up else True
        above_ema20 = close_vs_ema20 >= self.early_fail_close_vs_ema20_min

        if tag == "short_pullback_restart":
            if reclaimed_range and center_up_ok and above_ema20:
                return "early_fail_short_pullback_reclaim"
            if age_hours <= self.early_fail_trend_flip_window_hours and not self._supports_trade_direction(pair, trade):
                return "early_fail_short_pullback_trend_flip"
            if self._btc_short_support_lost(pair) and current_profit <= 0.003:
                return "early_fail_short_pullback_btc_flip"
            return None

        if reclaimed_range and center_up_ok:
            return "early_fail_short_breakdown_reclaim"
        if reclaimed_range and above_ema20:
            return "early_fail_short_breakdown_ema_reclaim"
        if age_hours <= self.early_fail_trend_flip_window_hours and not self._supports_trade_direction(pair, trade):
            return "early_fail_short_breakdown_trend_flip"
        if self._btc_short_support_lost(pair) and current_profit <= 0.003:
            return "early_fail_short_breakdown_btc_flip"
        return None

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        short_reason = self._early_fail_short_reason(pair, trade, current_time, current_profit)
        if short_reason:
            return short_reason
        return super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )


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


class DualTrendCompressionCloseQualityGuard032Strategy(
    DualTrendCompressionCloseQualityGuardStrategy,
):
    """Threshold sweep: reject when close_position > 0.32."""

    short_compression_close_quality_max_close_position = 0.32


class DualTrendCompressionCloseQualityOversoldGuardStrategy(
    _DualTrendStructureStrongRunnerReach5Mixin,
    DualTrendRawBreakevenGuardStrategy,
):
    """
    Light entry-quality + oversold variant:
    - only reject short_compression_breakdown
    - require close_not_low_enough
    - and require a short-term oversold stretch before rejecting
    """

    position_adjustment_enable = True
    reach5_trigger_profit = 0.05
    use_short_compression_close_quality_oversold_guard = True


class DualTrendEarlyFailPhase1AStrategy(
    _DualTrendEarlyFailExitMixin,
    DualTrendRawBreakevenGuardStrongRunnerStructureStrategy,
):
    """
    Phase 1A research candidate:
    - keep the current main candidate entry stack unchanged
    - add only short-side early-fail exits
    - leave reach5, guard, breakeven, ROI, and stoploss otherwise unchanged
    """


class _DualTrendEarlyFailCompressionOnlyNarrowMixin(_DualTrendEarlyFailExitMixin):
    """
    Narrow follow-up to Phase 1A.

    Scope is intentionally tighter:
    - only short_compression_breakdown
    - only in the first 3 hours
    - only while the trade is not profitable
    - only on reclaim + center-up confirmation
    """

    early_fail_short_window_hours = 3.0
    early_fail_trend_flip_window_hours = 0.0
    early_fail_profit_cap = 0.0

    def _early_fail_short_reason(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_profit: float,
    ) -> Optional[str]:
        if not self.early_fail_enable or not bool(getattr(trade, "is_short", False)):
            return None

        tag = self._trade_enter_tag(trade) or ""
        if tag != "short_compression_breakdown":
            return None

        age_hours = self._elapsed_hours_since_open(trade, current_time)
        if age_hours > self.early_fail_short_window_hours or current_profit > self.early_fail_profit_cap:
            return None

        center_dir = self._current_center_direction(pair)
        reclaimed_range = self._short_reclaimed_breakdown_range(pair)
        if reclaimed_range and center_dir > 0:
            return "early_fail_short_breakdown_reclaim_narrow"
        return None


class DualTrendEarlyFailCompressionOnlyNarrowStrategy(
    _DualTrendEarlyFailCompressionOnlyNarrowMixin,
    DualTrendRawBreakevenGuardStrongRunnerStructureStrategy,
):
    """
    Narrow research candidate:
    - only target the weakest short_compression_breakdown fake-breakdown cases
    - do not touch short_pullback_restart
    - do not use BTC flip / EMA reclaim / trend flip exits
    """


class DualTrendCombinedShortPullbackShapeV1Strategy(DualTrendRawStrategy):
    """Backward-compatible alias for the old raw strategy name."""


class DualTrendCombinedShortPullbackShapeBreakevenTp5ConditionalAdverse125Roi10Strategy(
    DualTrendBaselineStrategy
):
    """Backward-compatible alias for the old baseline strategy name."""


class DualTrendCombinedShortPullbackShapeCompressionFlushGuardStrategy(DualTrendGuardStrategy):
    """Backward-compatible alias for the old guard strategy name."""


