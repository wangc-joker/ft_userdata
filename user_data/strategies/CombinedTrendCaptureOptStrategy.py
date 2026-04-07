from pandas import DataFrame

from freqtrade.strategy import BooleanParameter, IntParameter

from DoubleShunStrategy import DoubleShunStrategy


class CombinedTrendCaptureOptStrategy(DoubleShunStrategy):
    allowed_pairs = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
    }

    enable_long_1h_triangle = BooleanParameter(default=True, space="buy", optimize=True)
    enable_long_1d_triangle = BooleanParameter(default=True, space="buy", optimize=True)
    enable_long_1d_center = BooleanParameter(default=True, space="buy", optimize=True)
    enable_short_1h_center = BooleanParameter(default=True, space="buy", optimize=True)
    enable_short_1h_compression = BooleanParameter(default=True, space="buy", optimize=True)
    enable_short_1d_triangle = BooleanParameter(default=True, space="buy", optimize=True)
    enable_short_1d_center = BooleanParameter(default=True, space="buy", optimize=True)

    hourly_long_rsi = IntParameter(48, 62, default=52, space="buy", optimize=True)
    daily_long_rsi = IntParameter(50, 65, default=55, space="buy", optimize=True)
    daily_short_rsi = IntParameter(35, 50, default=45, space="buy", optimize=True)

    cooldown_candles = IntParameter(2, 8, default=4, space="protection", optimize=True)
    stop_guard_lookback = IntParameter(24, 72, default=48, space="protection", optimize=True)
    stop_guard_duration = IntParameter(6, 18, default=12, space="protection", optimize=True)
    maxdd_lookback = IntParameter(48, 144, default=96, space="protection", optimize=True)
    maxdd_duration = IntParameter(12, 36, default=24, space="protection", optimize=True)

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": int(self.cooldown_candles.value),
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": int(self.stop_guard_lookback.value),
                "trade_limit": 2,
                "stop_duration_candles": int(self.stop_guard_duration.value),
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": int(self.maxdd_lookback.value),
                "trade_limit": 10,
                "stop_duration_candles": int(self.maxdd_duration.value),
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
        center_short = self._bool_series(dataframe, "center_breakout_short")
        compression_short = self._bool_series(dataframe, "compression_breakout_short")
        triangle_short_1d = self._bool_series(dataframe, "triangle_breakout_short_1d")
        center_short_1d = self._bool_series(dataframe, "center_breakout_short_1d")

        daily_long_context = self._bool_series(dataframe, "restart_ready_long_1d")
        daily_short_context = self._bool_series(dataframe, "restart_ready_short_1d")

        daily_long_signal = daily_long_context & (
            triangle_long_1d | center_long_1d
        ) & (dataframe["rsi_1d"] > int(self.daily_long_rsi.value))
        daily_short_signal = daily_short_context & (
            triangle_short_1d | center_short_1d
        ) & (dataframe["rsi_1d"] < int(self.daily_short_rsi.value))

        daily_long_trigger = daily_long_signal & ~daily_long_signal.shift(1).eq(True)
        daily_short_trigger = daily_short_signal & ~daily_short_signal.shift(1).eq(True)

        strong_hourly_long_triangle = (
            hourly_long_context
            & triangle_long
            & self._bool_series(dataframe, "range_tight")
            & self._bool_series(dataframe, "ema_slow_slope_up")
            & (dataframe["rsi"] > int(self.hourly_long_rsi.value))
            & self._bool_series(dataframe, "breakout_above_recent_1d")
        )

        if bool(self.enable_long_1h_triangle.value):
            dataframe.loc[
                strong_hourly_long_triangle,
                ["enter_long", "enter_tag"],
            ] = (1, "long_1h_triangle")

        if bool(self.enable_long_1d_triangle.value):
            dataframe.loc[
                daily_long_trigger & triangle_long_1d,
                ["enter_long", "enter_tag"],
            ] = (1, "long_1d_triangle")

        if bool(self.enable_long_1d_center.value):
            dataframe.loc[
                daily_long_trigger & center_long_1d,
                ["enter_long", "enter_tag"],
            ] = (1, "long_1d_center_compression")

        if bool(self.enable_short_1h_center.value):
            dataframe.loc[
                daily_short_context & center_short,
                ["enter_short", "enter_tag"],
            ] = (1, "short_1h_center")

        if bool(self.enable_short_1h_compression.value):
            dataframe.loc[
                daily_short_context & compression_short,
                ["enter_short", "enter_tag"],
            ] = (1, "short_1h_compression")

        if bool(self.enable_short_1d_triangle.value):
            dataframe.loc[
                daily_short_trigger & triangle_short_1d,
                ["enter_short", "enter_tag"],
            ] = (1, "short_1d_triangle")

        if bool(self.enable_short_1d_center.value):
            dataframe.loc[
                daily_short_trigger & center_short_1d,
                ["enter_short", "enter_tag"],
            ] = (1, "short_1d_center_compression")

        return dataframe
