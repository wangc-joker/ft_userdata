from pandas import DataFrame


def apply_short_entry_signals(strategy, dataframe: DataFrame, metadata: dict) -> DataFrame:
    if metadata["pair"] not in strategy.allowed_pairs:
        return dataframe

    bool_series = strategy._bool_series

    center_short = bool_series(dataframe, "center_breakout_short")
    compression_short = bool_series(dataframe, "compression_breakout_short")
    triangle_short_1d = bool_series(dataframe, "triangle_breakout_short_1d")
    center_short_1d = bool_series(dataframe, "center_breakout_short_1d")
    daily_short_context = bool_series(dataframe, "restart_ready_short_1d")

    daily_short_signal = daily_short_context & (
        triangle_short_1d | center_short_1d
    ) & (dataframe["rsi_1d"] < int(strategy.daily_short_rsi.value))
    daily_short_trigger = daily_short_signal & ~daily_short_signal.shift(1).eq(True)

    if bool(strategy.enable_short_1h_center.value):
        dataframe.loc[
            daily_short_context & center_short,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1h_center")

    if bool(strategy.enable_short_1h_compression.value):
        dataframe.loc[
            daily_short_context & compression_short,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1h_compression")

    if bool(strategy.enable_short_1d_triangle.value):
        dataframe.loc[
            daily_short_trigger & triangle_short_1d,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1d_triangle")

    if bool(strategy.enable_short_1d_center.value):
        dataframe.loc[
            daily_short_trigger & center_short_1d,
            ["enter_short", "enter_tag"],
        ] = (1, "short_1d_center_compression")

    return dataframe
