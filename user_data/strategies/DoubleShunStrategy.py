from typing import Optional

import pandas as pd
from pandas import DataFrame

import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import (
    DecimalParameter,
    IStrategy,
    IntParameter,
    informative,
    stoploss_from_absolute,
)


class DoubleShunStrategy(IStrategy):
    INTERFACE_VERSION = 3
    allowed_pairs = {"BTC/USDT:USDT", "BNB/USDT:USDT", "SOL/USDT:USDT"}

    can_short: bool = True
    timeframe = "1h"
    process_only_new_candles = True
    startup_candle_count: int = 240

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True
    use_custom_stoploss = True

    minimal_roi = {
        "0": 0.10,
    }

    stoploss = -0.02

    trend_ema_fast = IntParameter(5, 20, default=10, space="buy", optimize=True)
    trend_ema_slow = IntParameter(20, 80, default=30, space="buy", optimize=True)
    center_window = IntParameter(4, 12, default=6, space="buy", optimize=True)
    pullback_window = IntParameter(3, 8, default=4, space="buy", optimize=True)
    restart_window = IntParameter(2, 6, default=3, space="buy", optimize=True)
    triangle_window = IntParameter(4, 12, default=6, space="buy", optimize=True)
    compression_window = IntParameter(4, 12, default=6, space="buy", optimize=True)
    swing_window = IntParameter(2, 8, default=3, space="sell", optimize=True)

    pullback_depth = DecimalParameter(0.002, 0.025, default=0.010, decimals=3, space="buy", optimize=True)
    breakout_buffer = DecimalParameter(0.001, 0.012, default=0.002, decimals=3, space="buy", optimize=True)
    compression_limit = DecimalParameter(0.006, 0.040, default=0.018, decimals=3, space="buy", optimize=True)
    level_tolerance = DecimalParameter(0.002, 0.020, default=0.006, decimals=3, space="buy", optimize=True)
    level_proximity = DecimalParameter(0.002, 0.020, default=0.006, decimals=3, space="buy", optimize=True)
    volume_multiplier = DecimalParameter(1.00, 2.20, default=1.10, decimals=2, space="buy", optimize=True)

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
        return dataframe[column].eq(True)

    @informative("1d")
    def populate_indicators_1d(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)

    def _populate_structure_indicators(self, dataframe: DataFrame) -> DataFrame:
        ema_fast = int(self.trend_ema_fast.value)
        ema_slow = int(self.trend_ema_slow.value)
        center_window = int(self.center_window.value)
        pullback_window = int(self.pullback_window.value)
        restart_window = int(self.restart_window.value)
        triangle_window = int(self.triangle_window.value)
        compression_window = int(self.compression_window.value)
        swing_window = int(self.swing_window.value)

        pullback_depth = float(self.pullback_depth.value)
        breakout_buffer = float(self.breakout_buffer.value)
        compression_limit = float(self.compression_limit.value)
        level_tolerance = float(self.level_tolerance.value)
        level_proximity = float(self.level_proximity.value)
        volume_multiplier = float(self.volume_multiplier.value)

        half_window = max(2, triangle_window // 2)
        typical_price = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0

        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=ema_fast)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=ema_slow)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]
        dataframe["volume_mean"] = dataframe["volume"].rolling(max(5, triangle_window)).mean()

        dataframe["market_center"] = typical_price.rolling(center_window).mean()
        dataframe["center_up"] = dataframe["market_center"] > dataframe["market_center"].shift(2)
        dataframe["center_down"] = dataframe["market_center"] < dataframe["market_center"].shift(2)

        dataframe["uptrend"] = (
            (dataframe["close"] > dataframe["ema_slow"])
            & (dataframe["ema_fast"] > dataframe["ema_slow"])
            & dataframe["center_up"]
        )
        dataframe["downtrend"] = (
            (dataframe["close"] < dataframe["ema_slow"])
            & (dataframe["ema_fast"] < dataframe["ema_slow"])
            & dataframe["center_down"]
        )

        dataframe["recent_high"] = dataframe["high"].shift(1).rolling(triangle_window).max()
        dataframe["recent_low"] = dataframe["low"].shift(1).rolling(triangle_window).min()
        dataframe["recent_high_short"] = dataframe["high"].shift(1).rolling(half_window).max()
        dataframe["recent_low_short"] = dataframe["low"].shift(1).rolling(half_window).min()
        dataframe["prior_high_short"] = dataframe["high"].shift(half_window + 1).rolling(half_window).max()
        dataframe["prior_low_short"] = dataframe["low"].shift(half_window + 1).rolling(half_window).min()

        dataframe["rising_lows"] = dataframe["recent_low_short"] > dataframe["prior_low_short"]
        dataframe["falling_highs"] = dataframe["recent_high_short"] < dataframe["prior_high_short"]
        dataframe["flat_ceiling"] = (
            (dataframe["recent_high"] - dataframe["recent_high_short"]).abs() / dataframe["close"]
        ) < level_tolerance
        dataframe["flat_floor"] = (
            (dataframe["recent_low_short"] - dataframe["recent_low"]).abs() / dataframe["close"]
        ) < level_tolerance

        dataframe["range_width"] = (
            (dataframe["high"].shift(1).rolling(compression_window).max()
             - dataframe["low"].shift(1).rolling(compression_window).min())
            / dataframe["close"]
        )
        dataframe["range_width_prev"] = dataframe["range_width"].shift(max(2, compression_window // 2))
        dataframe["range_tight"] = dataframe["range_width"] < compression_limit
        dataframe["range_contracting"] = dataframe["range_width"] < dataframe["range_width_prev"]
        dataframe["volume_expansion"] = (
            dataframe["volume"] > dataframe["volume_mean"] * volume_multiplier
        )

        dataframe["pullback_low"] = dataframe["low"].shift(1).rolling(pullback_window).min()
        dataframe["pullback_high"] = dataframe["high"].shift(1).rolling(pullback_window).max()
        dataframe["restart_high"] = dataframe["high"].shift(1).rolling(restart_window).max()
        dataframe["restart_low"] = dataframe["low"].shift(1).rolling(restart_window).min()

        dataframe["pullback_seen_long"] = dataframe["pullback_low"] <= (
            dataframe["ema_fast"] * (1 + pullback_depth)
        )
        dataframe["pullback_seen_short"] = dataframe["pullback_high"] >= (
            dataframe["ema_fast"] * (1 - pullback_depth)
        )
        dataframe["structure_intact_long"] = dataframe["pullback_low"] > (
            dataframe["ema_slow"] * (1 - pullback_depth * 2.0)
        )
        dataframe["structure_intact_short"] = dataframe["pullback_high"] < (
            dataframe["ema_slow"] * (1 + pullback_depth * 2.0)
        )

        dataframe["restart_ready_long"] = (
            dataframe["uptrend"]
            & dataframe["pullback_seen_long"]
            & dataframe["structure_intact_long"]
            & (dataframe["close"] > dataframe["ema_fast"])
            & (dataframe["rsi"] > dataframe["rsi"].shift(1))
        )
        dataframe["restart_ready_short"] = (
            dataframe["downtrend"]
            & dataframe["pullback_seen_short"]
            & dataframe["structure_intact_short"]
            & (dataframe["close"] < dataframe["ema_fast"])
            & (dataframe["rsi"] < dataframe["rsi"].shift(1))
        )

        dataframe["near_high_compression"] = (
            dataframe["close"].shift(1) >= dataframe["recent_high"] * (1 - level_proximity)
        )
        dataframe["near_low_compression"] = (
            dataframe["close"].shift(1) <= dataframe["recent_low"] * (1 + level_proximity)
        )
        dataframe["breakout_above_recent"] = (
            (dataframe["close"] > dataframe["recent_high"] * (1 + breakout_buffer))
            & (
                dataframe["close"].shift(1)
                <= dataframe["recent_high"].shift(1) * (1 + breakout_buffer)
            )
        )
        dataframe["breakout_below_recent"] = (
            (dataframe["close"] < dataframe["recent_low"] * (1 - breakout_buffer))
            & (
                dataframe["close"].shift(1)
                >= dataframe["recent_low"].shift(1) * (1 - breakout_buffer)
            )
        )
        dataframe["ema_slow_slope_up"] = dataframe["ema_slow"] > dataframe["ema_slow"].shift(3)
        dataframe["ema_slow_slope_down"] = dataframe["ema_slow"] < dataframe["ema_slow"].shift(3)
        dataframe["daily_momentum_long"] = (
            dataframe["uptrend"]
            & dataframe["ema_slow_slope_up"]
            & (dataframe["rsi"] > 55)
        )
        dataframe["daily_momentum_short"] = (
            dataframe["downtrend"]
            & dataframe["ema_slow_slope_down"]
            & (dataframe["rsi"] < 45)
        )

        dataframe["triangle_breakout_long"] = (
            dataframe["restart_ready_long"]
            & dataframe["rising_lows"]
            & dataframe["flat_ceiling"]
            & dataframe["range_contracting"]
            & dataframe["breakout_above_recent"]
            & dataframe["volume_expansion"]
        )
        dataframe["triangle_breakout_short"] = (
            dataframe["restart_ready_short"]
            & dataframe["falling_highs"]
            & dataframe["flat_floor"]
            & dataframe["range_contracting"]
            & dataframe["breakout_below_recent"]
            & dataframe["volume_expansion"]
        )

        dataframe["center_breakout_long"] = (
            dataframe["restart_ready_long"]
            & dataframe["center_up"]
            & dataframe["range_contracting"]
            & dataframe["near_high_compression"]
            & (dataframe["market_center"] > dataframe["market_center"].shift(1))
            & dataframe["breakout_above_recent"]
            & (dataframe["close"] > dataframe["market_center"])
            & dataframe["volume_expansion"]
        )
        dataframe["center_breakout_short"] = (
            dataframe["restart_ready_short"]
            & dataframe["center_down"]
            & dataframe["range_contracting"]
            & dataframe["near_low_compression"]
            & (dataframe["market_center"] < dataframe["market_center"].shift(1))
            & dataframe["breakout_below_recent"]
            & (dataframe["close"] < dataframe["market_center"])
            & dataframe["volume_expansion"]
        )

        dataframe["compression_breakout_long"] = (
            dataframe["restart_ready_long"]
            & dataframe["range_tight"]
            & dataframe["range_contracting"]
            & dataframe["near_high_compression"]
            & dataframe["breakout_above_recent"]
            & dataframe["volume_expansion"]
        )
        dataframe["compression_breakout_short"] = (
            dataframe["restart_ready_short"]
            & dataframe["range_tight"]
            & dataframe["range_contracting"]
            & dataframe["near_low_compression"]
            & dataframe["breakout_below_recent"]
            & dataframe["volume_expansion"]
        )

        dataframe["signal_long"] = (
            dataframe["triangle_breakout_long"]
            | dataframe["center_breakout_long"]
            | dataframe["compression_breakout_long"]
        )
        dataframe["signal_short"] = (
            dataframe["triangle_breakout_short"]
            | dataframe["center_breakout_short"]
            | dataframe["compression_breakout_short"]
        )

        dataframe["structure_stop_long"] = dataframe["low"].shift(1).rolling(swing_window).min()
        dataframe["structure_stop_short"] = dataframe["high"].shift(1).rolling(swing_window).max()

        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_structure_indicators(dataframe)

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if metadata["pair"] not in self.allowed_pairs:
            return dataframe

        hourly_long_context = (
            self._bool_series(dataframe, "restart_ready_long_1d")
            & self._bool_series(dataframe, "daily_momentum_long_1d")
        )
        hourly_short_context = self._bool_series(dataframe, "restart_ready_short_1d")
        triangle_long = self._bool_series(dataframe, "triangle_breakout_long")
        compression_long = self._bool_series(dataframe, "compression_breakout_long")
        center_short = self._bool_series(dataframe, "center_breakout_short")
        compression_short = self._bool_series(dataframe, "compression_breakout_short")
        triangle_long_1d = self._bool_series(dataframe, "triangle_breakout_long_1d")
        center_long_1d = self._bool_series(dataframe, "center_breakout_long_1d")
        triangle_short_1d = self._bool_series(dataframe, "triangle_breakout_short_1d")
        center_short_1d = self._bool_series(dataframe, "center_breakout_short_1d")
        daily_long_context = self._bool_series(dataframe, "restart_ready_long_1d")
        daily_short_context = self._bool_series(dataframe, "restart_ready_short_1d")
        daily_long_signal = daily_long_context & (triangle_long_1d | center_long_1d)
        daily_short_signal = daily_short_context & (triangle_short_1d | center_short_1d)
        daily_long_trigger = daily_long_signal & ~daily_long_signal.shift(1).eq(True)
        daily_short_trigger = daily_short_signal & ~daily_short_signal.shift(1).eq(True)
        strong_hourly_long_triangle = (
            hourly_long_context
            & triangle_long
            & self._bool_series(dataframe, "range_tight")
            & self._bool_series(dataframe, "ema_slow_slope_up")
            & (dataframe["rsi"] > 52)
            & self._bool_series(dataframe, "breakout_above_recent_1d")
        )
        dataframe.loc[
            strong_hourly_long_triangle,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1h_triangle")

        dataframe.loc[
            daily_long_trigger & triangle_long_1d,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1d_triangle")
        dataframe.loc[
            daily_long_trigger & center_long_1d,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1d_center_compression")

        dataframe.loc[
            hourly_short_context & center_short,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1h_center")
        dataframe.loc[
            hourly_short_context & compression_short,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1h_compression")

        dataframe.loc[
            daily_short_trigger & triangle_short_1d,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1d_triangle")
        dataframe.loc[
            daily_short_trigger & center_short_1d,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1d_center_compression")

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
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
        tag = trade.enter_tag or ""
        scope = "1d" if "_1d_" in tag else "1h"
        suffix = "_1d" if scope == "1d" else ""

        if trade.is_short:
            structure_stop = candle.get(f"structure_stop_short{suffix}")
            capped_stop = trade.open_rate * 1.02
            stop_price = capped_stop
            if pd.notna(structure_stop):
                stop_price = min(float(structure_stop), capped_stop)
        else:
            structure_stop = candle.get(f"structure_stop_long{suffix}")
            capped_stop = trade.open_rate * 0.98
            stop_price = capped_stop
            if pd.notna(structure_stop):
                stop_price = max(float(structure_stop), capped_stop)

        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=trade.is_short,
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
        tag = trade.enter_tag or ""
        scope = "1d" if "_1d_" in tag else "1h"
        suffix = "_1d" if scope == "1d" else ""

        stop_long = candle.get(f"structure_stop_long{suffix}")
        stop_short = candle.get(f"structure_stop_short{suffix}")

        if trade.is_short:
            if bool(candle.get("uptrend_1d", False)):
                return "trend_flip_short"
            if scope == "1d":
                if bool(candle.get("center_up_1d", False)) and candle["close"] > candle.get("ema_fast_1d", candle["close"]):
                    return "structure_exit_short_1d"
            else:
                if bool(candle.get("center_up", False)) and candle["close"] > candle.get("ema_fast", candle["close"]):
                    return "structure_exit_short_1h"

            if pd.notna(stop_short) and candle["close"] > stop_short:
                return f"swing_exit_short_{scope}"
            return None

        if bool(candle.get("downtrend_1d", False)):
            return "trend_flip_long"
        if scope == "1d":
            if bool(candle.get("center_down_1d", False)) and candle["close"] < candle.get("ema_fast_1d", candle["close"]):
                return "structure_exit_long_1d"
        else:
            if bool(candle.get("center_down", False)) and candle["close"] < candle.get("ema_fast", candle["close"]):
                return "structure_exit_long_1h"

        if pd.notna(stop_long) and candle["close"] < stop_long:
            return f"swing_exit_long_{scope}"

        return None
