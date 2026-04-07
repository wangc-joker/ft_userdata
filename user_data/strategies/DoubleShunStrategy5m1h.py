from datetime import datetime
from typing import Optional

from pandas import DataFrame

import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import DecimalParameter, IStrategy, IntParameter, informative, stoploss_from_open


class DoubleShunStrategy5m1h(IStrategy):
    INTERFACE_VERSION = 3

    can_short: bool = False
    timeframe = "5m"
    process_only_new_candles = True
    startup_candle_count: int = 1000

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    use_custom_stoploss = True

    minimal_roi = {
        "0": 0.03,
        "180": 0.015,
        "720": 0.008,
        "1440": 0.0,
    }

    stoploss = -0.15

    trend_ema_fast = IntParameter(10, 40, default=20, space="buy", optimize=True)
    trend_ema_slow = IntParameter(40, 150, default=55, space="buy", optimize=True)
    center_window = IntParameter(6, 24, default=12, space="buy", optimize=True)
    structure_window = IntParameter(3, 12, default=5, space="buy", optimize=True)
    pullback_window = IntParameter(3, 12, default=6, space="buy", optimize=True)
    restart_window = IntParameter(2, 8, default=3, space="buy", optimize=True)
    box_window = IntParameter(6, 20, default=10, space="buy", optimize=True)
    volume_window = IntParameter(10, 40, default=20, space="buy", optimize=True)
    momentum_rsi_long = IntParameter(50, 65, default=54, space="buy", optimize=True)

    pullback_depth = DecimalParameter(0.005, 0.050, default=0.018, decimals=3, space="buy", optimize=True)
    breakout_buffer = DecimalParameter(0.001, 0.015, default=0.003, decimals=3, space="buy", optimize=True)
    box_range_limit = DecimalParameter(0.010, 0.080, default=0.035, decimals=3, space="buy", optimize=True)
    volume_multiplier = DecimalParameter(1.00, 2.50, default=1.20, decimals=2, space="buy", optimize=True)
    atr_contract_factor = DecimalParameter(0.80, 1.20, default=0.95, decimals=2, space="buy", optimize=True)
    abnormal_candle_limit = DecimalParameter(0.010, 0.080, default=0.035, decimals=3, space="buy", optimize=True)

    stoploss_pct = DecimalParameter(0.010, 0.060, default=0.025, decimals=3, space="sell", optimize=True)
    breakeven_profit = DecimalParameter(0.005, 0.030, default=0.010, decimals=3, space="sell", optimize=True)
    trail_trigger_profit = DecimalParameter(0.010, 0.060, default=0.020, decimals=3, space="sell", optimize=True)
    trail_open_profit = DecimalParameter(0.002, 0.030, default=0.007, decimals=3, space="sell", optimize=True)
    exit_rsi_long = IntParameter(35, 55, default=45, space="sell", optimize=True)

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 3,
            }
        ]

    @informative("1h")
    def populate_indicators_1h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._populate_trend_indicators(dataframe)

    def _populate_trend_indicators(self, dataframe: DataFrame) -> DataFrame:
        ema_fast = int(self.trend_ema_fast.value)
        ema_slow = int(self.trend_ema_slow.value)
        center_window = int(self.center_window.value)
        structure_window = int(self.structure_window.value)
        volume_window = int(self.volume_window.value)

        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=ema_fast)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=ema_slow)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]

        dataframe["typical_price"] = (
            dataframe["high"] + dataframe["low"] + dataframe["close"]
        ) / 3.0
        dataframe["market_center"] = dataframe["typical_price"].rolling(center_window).mean()
        dataframe["market_center_prev"] = dataframe["market_center"].shift(center_window)
        dataframe["center_up"] = dataframe["market_center"] > dataframe["market_center_prev"]
        dataframe["center_down"] = dataframe["market_center"] < dataframe["market_center_prev"]

        rolling_high = dataframe["high"].rolling(structure_window).max()
        rolling_low = dataframe["low"].rolling(structure_window).min()
        dataframe["higher_high"] = rolling_high > rolling_high.shift(structure_window)
        dataframe["higher_low"] = rolling_low > rolling_low.shift(structure_window)
        dataframe["lower_high"] = rolling_high < rolling_high.shift(structure_window)
        dataframe["lower_low"] = rolling_low < rolling_low.shift(structure_window)

        dataframe["ema_long_bias"] = (
            (dataframe["close"] > dataframe["ema_slow"])
            & (dataframe["ema_fast"] > dataframe["ema_slow"])
        )
        dataframe["ema_short_bias"] = (
            (dataframe["close"] < dataframe["ema_slow"])
            & (dataframe["ema_fast"] < dataframe["ema_slow"])
        )
        dataframe["structure_long"] = dataframe["higher_high"] & dataframe["higher_low"]
        dataframe["structure_short"] = dataframe["lower_high"] & dataframe["lower_low"]

        dataframe["trend_long_score"] = (
            dataframe["ema_long_bias"].astype(int)
            + dataframe["structure_long"].astype(int)
            + dataframe["center_up"].astype(int)
        )
        dataframe["trend_short_score"] = (
            dataframe["ema_short_bias"].astype(int)
            + dataframe["structure_short"].astype(int)
            + dataframe["center_down"].astype(int)
        )

        dataframe["trend_long"] = dataframe["trend_long_score"] >= 2
        dataframe["trend_short"] = dataframe["trend_short_score"] >= 2
        dataframe["volume_mean"] = dataframe["volume"].rolling(volume_window).mean()
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = self._populate_trend_indicators(dataframe)

        pullback_window = int(self.pullback_window.value)
        restart_window = int(self.restart_window.value)
        box_window = int(self.box_window.value)

        dataframe["box_high"] = dataframe["high"].shift(1).rolling(box_window).max()
        dataframe["box_low"] = dataframe["low"].shift(1).rolling(box_window).min()
        dataframe["box_width"] = (dataframe["box_high"] - dataframe["box_low"]) / dataframe["close"]
        dataframe["atr_pct_mean"] = dataframe["atr_pct"].rolling(box_window).mean()

        dataframe["consolidating"] = (
            (dataframe["box_width"] < float(self.box_range_limit.value))
            & (dataframe["atr_pct"] < dataframe["atr_pct_mean"] * float(self.atr_contract_factor.value))
        )
        dataframe["volume_expansion"] = (
            dataframe["volume"] > dataframe["volume_mean"] * float(self.volume_multiplier.value)
        )
        dataframe["range_expansion"] = dataframe["atr_pct"] > dataframe["atr_pct_mean"]

        candle_body = (dataframe["close"] - dataframe["open"]).abs() / dataframe["close"]
        candle_range = (dataframe["high"] - dataframe["low"]) / dataframe["close"]
        dataframe["abnormal_candle"] = (
            candle_body > float(self.abnormal_candle_limit.value)
        ) | (candle_range > float(self.abnormal_candle_limit.value))

        dataframe["pullback_low"] = dataframe["low"].shift(1).rolling(pullback_window).min()
        dataframe["restart_high"] = dataframe["high"].shift(1).rolling(restart_window).max()

        dataframe["pullback_seen_long"] = (
            dataframe["close"].shift(1).rolling(pullback_window).min() < dataframe["ema_fast"].shift(1)
        )
        dataframe["structure_intact_long"] = (
            dataframe["pullback_low"] > dataframe["ema_slow"] * (1 - float(self.pullback_depth.value) * 2.0)
        )

        dataframe["restart_long"] = (
            (dataframe["close"] > dataframe["ema_fast"])
            & (dataframe["close"] > dataframe["restart_high"] * (1 + float(self.breakout_buffer.value)))
            & (dataframe["rsi"] > int(self.momentum_rsi_long.value))
            & (dataframe["rsi"] > dataframe["rsi"].shift(1))
            & dataframe["volume_expansion"]
        )

        dataframe["breakout_long"] = (
            dataframe["consolidating"].shift(1).fillna(False)
            & (dataframe["close"] > dataframe["box_high"] * (1 + float(self.breakout_buffer.value)))
            & dataframe["range_expansion"]
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        long_resonance = (
            dataframe["trend_long"]
            & dataframe["trend_long_1h"]
            & ~dataframe["abnormal_candle"]
        )

        long_pullback_restart = (
            long_resonance
            & dataframe["pullback_seen_long"]
            & dataframe["structure_intact_long"]
            & dataframe["restart_long"]
        )
        long_box_breakout = long_resonance & dataframe["breakout_long"]

        dataframe.loc[long_pullback_restart, ["enter_long", "enter_tag"]] = (1, "trend_restart_long")
        dataframe.loc[long_box_breakout, ["enter_long", "enter_tag"]] = (1, "box_breakout_long")

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        exit_long = (
            ((dataframe["center_down"] & (dataframe["rsi"] < int(self.exit_rsi_long.value))))
            | (dataframe["close"] < dataframe["ema_slow"])
            | (dataframe["trend_short"] & dataframe["trend_short_1h"])
        )
        dataframe.loc[exit_long, ["exit_long", "exit_tag"]] = (1, "trend_flip_long")
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> Optional[float]:
        base_stop = -float(self.stoploss_pct.value)

        if after_fill:
            return base_stop

        if current_profit >= float(self.trail_trigger_profit.value):
            return stoploss_from_open(
                float(self.trail_open_profit.value),
                current_profit,
                is_short=trade.is_short,
                leverage=trade.leverage,
            )

        if current_profit >= float(self.breakeven_profit.value):
            return stoploss_from_open(
                0.001,
                current_profit,
                is_short=trade.is_short,
                leverage=trade.leverage,
            )

        return base_stop
