from pandas import DataFrame

from DoubleShunStrategy import DoubleShunStrategy


class CombinedTrendCaptureStrategy(DoubleShunStrategy):
    allowed_pairs = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
    }

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 4,
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 48,
                "trade_limit": 2,
                "stop_duration_candles": 12,
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 96,
                "trade_limit": 10,
                "stop_duration_candles": 24,
                "max_allowed_drawdown": 0.10,
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

        hourly_short_context = self._bool_series(dataframe, "restart_ready_short_1d")
        center_short = self._bool_series(dataframe, "center_breakout_short")
        compression_short = self._bool_series(dataframe, "compression_breakout_short")
        triangle_short_1d = self._bool_series(dataframe, "triangle_breakout_short_1d")
        center_short_1d = self._bool_series(dataframe, "center_breakout_short_1d")
        daily_short_context = self._bool_series(dataframe, "restart_ready_short_1d")
        daily_short_signal = daily_short_context & (triangle_short_1d | center_short_1d)
        daily_short_trigger = daily_short_signal & ~daily_short_signal.shift(1).eq(True)

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
