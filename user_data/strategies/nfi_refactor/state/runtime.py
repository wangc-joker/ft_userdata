def is_backtest_mode(strategy) -> bool:
    """Return True for Freqtrade modes where historical data is being replayed."""
    return strategy.dp.runmode.value in ["backtest", "hyperopt"]


def get_ticker_indicator(strategy):
    return int(strategy.timeframe[:-1])


def is_system_v3(strategy, trade) -> bool:
    return trade.get_custom_data(key="system_version") == strategy.system_v3_name


def is_system_v3_1(strategy, trade) -> bool:
    return trade.get_custom_data(key="system_version") == strategy.system_v3_1_name


def is_system_v3_2(strategy, trade) -> bool:
    return trade.get_custom_data(key="system_version") == strategy.system_v3_2_name


def has_valid_entry_conditions(strategy, trade, exit_rate: float, last_candle, previous_candle) -> bool:
    filled_orders = trade.select_filled_orders()
    if len(filled_orders) < 1:
        return False

    slice_profit = (exit_rate - filled_orders[-1].safe_price) / filled_orders[-1].safe_price
    if not trade.is_short:
        return last_candle["enter_long"] or strategy.long_grind_entry(
            last_candle, previous_candle, slice_profit, False
        )

    return last_candle["enter_short"] or strategy.short_grind_entry(
        last_candle, previous_candle, slice_profit, False
    )


def update_signals_from_config(strategy, config):
    if hasattr(strategy, "long_entry_signal_params") and "long_entry_signal_params" in config:
        for condition_key in strategy.long_entry_signal_params:
            if condition_key in config["long_entry_signal_params"]:
                strategy.long_entry_signal_params[condition_key] = config["long_entry_signal_params"][
                    condition_key
                ]

    if hasattr(strategy, "short_entry_signal_params") and "short_entry_signal_params" in config:
        for condition_key in strategy.short_entry_signal_params:
            if condition_key in config["short_entry_signal_params"]:
                strategy.short_entry_signal_params[condition_key] = config["short_entry_signal_params"][
                    condition_key
                ]


def set_profit_target(strategy, pair: str, sell_reason: str, rate: float, current_profit: float, current_time):
    strategy.target_profit_cache.data[pair] = {
        "rate": rate,
        "profit": current_profit,
        "sell_reason": sell_reason,
        "time_profit_reached": current_time.isoformat(),
    }
    strategy.target_profit_cache.save()


def remove_profit_target(strategy, pair: str):
    if strategy.target_profit_cache is not None:
        strategy.target_profit_cache.data.pop(pair, None)
        strategy.target_profit_cache.save()
