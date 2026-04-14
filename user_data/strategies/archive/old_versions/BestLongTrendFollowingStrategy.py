from pandas import DataFrame

from DoubleShunStrategy import DoubleShunStrategy


class BestLongTrendFollowingStrategy(DoubleShunStrategy):
    can_short = False
    minimal_roi = {
        "0": 0.10,
    }
    allowed_pairs = {
        "BTC/USDT",
        "ETH/USDT",
        "BNB/USDT",
        "SOL/USDT",
        "XRP/USDT",
        "ADA/USDT",
        "DOGE/USDT",
        "AVAX/USDT",
        "LINK/USDT",
        "TRX/USDT",
    }

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 3,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 96,
                "trade_limit": 12,
                "stop_duration_candles": 24,
                "max_allowed_drawdown": 0.12,
            },
        ]

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if metadata["pair"] not in self.allowed_pairs:
            return dataframe

        hourly_long_context = (
            self._bool_series(dataframe, "restart_ready_long_1d")
            & self._bool_series(dataframe, "daily_momentum_long_1d")
        )
        triangle_long = self._bool_series(dataframe, "triangle_breakout_long")
        compression_long = self._bool_series(dataframe, "compression_breakout_long")
        triangle_long_1d = self._bool_series(dataframe, "triangle_breakout_long_1d")
        center_long_1d = self._bool_series(dataframe, "center_breakout_long_1d")
        daily_long_context = self._bool_series(dataframe, "restart_ready_long_1d")
        daily_long_signal = daily_long_context & (triangle_long_1d | center_long_1d)
        daily_long_trigger = daily_long_signal & ~daily_long_signal.shift(1).eq(True)

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

        return dataframe
