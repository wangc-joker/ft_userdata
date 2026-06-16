from __future__ import annotations

from typing import Optional

import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, informative, stoploss_from_absolute

from core.indicators.structure import populate_structure_indicators


class DualTrendLongDailyCenterV1Strategy(IStrategy):
    """
    Validation strategy for the old long_1d_center_compression idea.

    It intentionally keeps a narrow surface:
    - long-only
    - 1d center compression breakout only
    - no DCA / no partial take-profit
    """

    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "1h"
    process_only_new_candles = True
    startup_candle_count = 240

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True
    use_custom_stoploss = True

    minimal_roi = {"0": 0.10}
    stoploss = -0.02

    trend_ema_fast = 6
    trend_ema_slow = 46
    center_window = 5
    pullback_window = 6
    restart_window = 4
    triangle_window = 5
    compression_window = 11
    swing_window = 3

    pullback_depth = 0.009
    breakout_buffer = 0.009
    compression_limit = 0.006
    level_tolerance = 0.016
    level_proximity = 0.015
    volume_multiplier = 1.13
    daily_long_rsi = 55

    allowed_pairs: set[str] | None = None

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 2,
            }
        ]

    @staticmethod
    def _bool_series(dataframe: DataFrame, column: str) -> pd.Series:
        if column not in dataframe:
            return pd.Series(False, index=dataframe.index)
        return dataframe[column].eq(True)

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)

    def _populate_structure_indicators(self, dataframe: DataFrame) -> DataFrame:
        return populate_structure_indicators(
            dataframe=dataframe,
            trend_ema_fast=self.trend_ema_fast,
            trend_ema_slow=self.trend_ema_slow,
            center_window=self.center_window,
            pullback_window=self.pullback_window,
            restart_window=self.restart_window,
            triangle_window=self.triangle_window,
            compression_window=self.compression_window,
            swing_window=self.swing_window,
            pullback_depth=self.pullback_depth,
            breakout_buffer=self.breakout_buffer,
            compression_limit=self.compression_limit,
            level_tolerance=self.level_tolerance,
            level_proximity=self.level_proximity,
            volume_multiplier=self.volume_multiplier,
        )

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_long"] = 0
        dataframe["enter_tag"] = None

        if self.allowed_pairs is not None and metadata["pair"] not in self.allowed_pairs:
            return dataframe

        daily_long_signal = (
            self._bool_series(dataframe, "restart_ready_long_1d")
            & self._bool_series(dataframe, "center_breakout_long_1d")
            & (dataframe["rsi_1d"] > self.daily_long_rsi)
        )
        daily_long_trigger = daily_long_signal & ~daily_long_signal.shift(1).eq(True)

        dataframe.loc[daily_long_trigger, ["enter_long", "enter_tag"]] = (
            1,
            "long_1d_center_compression",
        )
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
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
        if not self.dp:
            return self.stoploss

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return self.stoploss

        candle = dataframe.iloc[-1]
        structure_stop = candle.get("structure_stop_long_1d")
        stop_price = trade.open_rate * 0.98
        if pd.notna(structure_stop):
            stop_price = max(float(structure_stop), stop_price)

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
        if not self.dp:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        candle = dataframe.iloc[-1]
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


class DualTrendLongDailyCenterRoi5V1Strategy(DualTrendLongDailyCenterV1Strategy):
    minimal_roi = {"0": 0.05}

    def custom_exit(self, *args, **kwargs) -> Optional[str]:
        return None


class DualTrendLongDailyCenterRoi6V1Strategy(DualTrendLongDailyCenterV1Strategy):
    minimal_roi = {"0": 0.06}

    def custom_exit(self, *args, **kwargs) -> Optional[str]:
        return None


class DualTrendLongDailyCenterTop9V1Strategy(DualTrendLongDailyCenterV1Strategy):
    allowed_pairs = {
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


class DualTrendLongDailyCenterCore3V1Strategy(DualTrendLongDailyCenterV1Strategy):
    allowed_pairs = {
        "BNB/USDT:USDT",
        "DOGE/USDT:USDT",
        "XRP/USDT:USDT",
    }
