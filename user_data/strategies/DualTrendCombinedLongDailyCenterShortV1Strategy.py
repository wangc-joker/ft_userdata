from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import informative, stoploss_from_absolute

from core.indicators.structure import populate_structure_indicators
from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy


class DualTrendCombinedLongDailyCenterShortV1Strategy(DualTrendCompressionRestartShortV1Strategy):
    """
    Combined validation strategy:
    - Short side: unchanged DualTrendCompressionRestartShortV1Strategy.
    - Long side: old long_1d_center_compression idea from DualTrendLongDailyCenterV1Strategy.

    This class keeps separate stop/risk fields per side so Short V1 sizing does
    not accidentally reject long entries.
    """

    can_short = True
    startup_candle_count = 1000

    enable_long_daily_center = True
    long_allowed_pairs: set[str] | None = None

    long_trend_ema_fast = 6
    long_trend_ema_slow = 46
    long_center_window = 5
    long_pullback_window = 6
    long_restart_window = 4
    long_triangle_window = 5
    long_compression_window = 11
    long_swing_window = 3

    long_pullback_depth = 0.009
    long_breakout_buffer = 0.009
    long_compression_limit = 0.006
    long_level_tolerance = 0.016
    long_level_proximity = 0.015
    long_volume_multiplier = 1.13
    long_daily_rsi = 55
    long_stop_floor_pct = 0.02

    @staticmethod
    def _bool_series(dataframe: DataFrame, column: str) -> pd.Series:
        if column not in dataframe:
            return pd.Series(False, index=dataframe.index)
        return dataframe[column].eq(True)

    def _populate_long_structure_indicators(self, dataframe: DataFrame) -> DataFrame:
        return populate_structure_indicators(
            dataframe=dataframe,
            trend_ema_fast=self.long_trend_ema_fast,
            trend_ema_slow=self.long_trend_ema_slow,
            center_window=self.long_center_window,
            pullback_window=self.long_pullback_window,
            restart_window=self.long_restart_window,
            triangle_window=self.long_triangle_window,
            compression_window=self.long_compression_window,
            swing_window=self.long_swing_window,
            pullback_depth=self.long_pullback_depth,
            breakout_buffer=self.long_breakout_buffer,
            compression_limit=self.long_compression_limit,
            level_tolerance=self.long_level_tolerance,
            level_proximity=self.long_level_proximity,
            volume_multiplier=self.long_volume_multiplier,
        )

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_long_structure_indicators(dataframe.copy())

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata).copy()
        dataframe["enter_long"] = dataframe.get("enter_long", 0)

        if not self.enable_long_daily_center:
            return dataframe
        if self.long_allowed_pairs is not None and metadata["pair"] not in self.long_allowed_pairs:
            return dataframe

        daily_long_signal = (
            self._bool_series(dataframe, "restart_ready_long_1d")
            & self._bool_series(dataframe, "center_breakout_long_1d")
            & (dataframe["rsi_1d"] > self.long_daily_rsi)
        )
        daily_long_trigger = daily_long_signal & ~daily_long_signal.shift(1).eq(True)

        structure_stop = dataframe["structure_stop_long_1d"]
        floor_stop = dataframe["close"] * (1 - self.long_stop_floor_pct)
        long_stop = pd.concat([structure_stop, floor_stop], axis=1).max(axis=1)
        long_risk_pct = (dataframe["close"] - long_stop) / dataframe["close"]
        long_risk_ok = long_risk_pct.between(self.min_stop_distance, self.max_stop_distance)

        long_entry = daily_long_trigger & long_risk_ok & (dataframe["volume"] > 0)
        dataframe.loc[long_entry, ["enter_long", "enter_tag"]] = (1, "long_1d_center_compression")
        dataframe.loc[long_entry, "enter_initial_stop"] = long_stop.loc[long_entry].astype("float32")
        dataframe.loc[long_entry, "enter_risk_pct"] = long_risk_pct.loc[long_entry].astype("float32")
        return dataframe

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
        if trade.is_short:
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
        initial_stop = float(candle.get("enter_initial_stop", np.nan))
        capped_stop = trade.open_rate * (1 - self.max_stop_distance)
        stop_price = capped_stop if not np.isfinite(initial_stop) else max(initial_stop, capped_stop)
        profit_lock_stop = self._profit_lock_stop_price(trade, current_profit)
        if profit_lock_stop is not None:
            stop_price = max(stop_price, profit_lock_stop)
        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=False,
            leverage=trade.leverage,
        )

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        if trade.is_short:
            return super().custom_exit(
                pair=pair,
                trade=trade,
                current_time=current_time,
                current_rate=current_rate,
                current_profit=current_profit,
                **kwargs,
            )

        candle = self._current_candle(pair)
        if candle is None:
            return None
        if bool(candle.get("downtrend_1d", False)):
            return "trend_flip_long_1d"
        if bool(candle.get("center_down_1d", False)) and candle["close"] < candle.get(
            "ema_fast_1d",
            candle["close"],
        ):
            return "structure_exit_long_1d"
        structure_stop = candle.get("structure_stop_long_1d")
        if pd.notna(structure_stop) and candle["close"] < structure_stop:
            return "swing_exit_long_1d"
        return None


class DualTrendCombinedLongDailyCenterTop9ShortV1Strategy(DualTrendCombinedLongDailyCenterShortV1Strategy):
    long_allowed_pairs = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "TRX/USDT:USDT",
        "ADA/USDT:USDT",
        "ZEC/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
    }


class DualTrendCombinedLongDailyCenterCore3ShortV1Strategy(DualTrendCombinedLongDailyCenterShortV1Strategy):
    long_allowed_pairs = {
        "BNB/USDT:USDT",
        "DOGE/USDT:USDT",
        "XRP/USDT:USDT",
    }
