from pandas import DataFrame


def apply_long_entry_signals(strategy, dataframe: DataFrame, metadata: dict) -> DataFrame:
    if metadata["pair"] not in strategy.allowed_pairs:
        return dataframe

    bool_series = strategy._bool_series

    hourly_long_context = (
        bool_series(dataframe, "restart_ready_long_1d")
        & bool_series(dataframe, "daily_momentum_long_1d")
    )
    triangle_long = bool_series(dataframe, "triangle_breakout_long")
    triangle_long_1d = bool_series(dataframe, "triangle_breakout_long_1d")
    center_long_1d = bool_series(dataframe, "center_breakout_long_1d")
    daily_long_context = bool_series(dataframe, "restart_ready_long_1d")

    daily_long_signal = daily_long_context & (
        triangle_long_1d | center_long_1d
    ) & (dataframe["rsi_1d"] > int(strategy.daily_long_rsi.value))
    daily_long_trigger = daily_long_signal & ~daily_long_signal.shift(1).eq(True)

    strong_hourly_long_triangle = (
        hourly_long_context
        & triangle_long
        & bool_series(dataframe, "range_tight")
        & bool_series(dataframe, "ema_slow_slope_up")
        & (dataframe["rsi"] > int(strategy.hourly_long_rsi.value))
        & bool_series(dataframe, "breakout_above_recent_1d")
    )

    if bool(strategy.enable_long_1h_triangle.value):
        dataframe.loc[
            strong_hourly_long_triangle,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1h_triangle")

    if bool(strategy.enable_long_1d_triangle.value):
        dataframe.loc[
            daily_long_trigger & triangle_long_1d,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1d_triangle")

    if bool(strategy.enable_long_1d_center.value):
        dataframe.loc[
            daily_long_trigger & center_long_1d,
            ["enter_long", "enter_tag"],
        ] = (1, "long_1d_center_compression")

    return dataframe
