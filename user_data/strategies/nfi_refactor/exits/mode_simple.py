"""Small mode-specific exit helpers extracted from NFI."""


def long_exit_grind(
    strategy,
    pair: str,
    current_rate: float,
    profit_stake: float,
    profit_ratio: float,
    profit_current_stake_ratio: float,
    profit_init_ratio: float,
    max_profit: float,
    max_loss: float,
    filled_entries,
    filled_exits,
    last_candle,
    previous_candle_1,
    previous_candle_2,
    previous_candle_3,
    previous_candle_4,
    previous_candle_5,
    trade,
    current_time,
    enter_tags,
) -> tuple:
    if profit_init_ratio > 0.25:
        return True, f"exit_{strategy.long_grind_mode_name}_g"

    return False, None


def long_exit_btc(
    strategy,
    pair: str,
    current_rate: float,
    profit_stake: float,
    profit_ratio: float,
    profit_current_stake_ratio: float,
    profit_init_ratio: float,
    max_profit: float,
    max_loss: float,
    filled_entries,
    filled_exits,
    last_candle,
    previous_candle_1,
    previous_candle_2,
    previous_candle_3,
    previous_candle_4,
    previous_candle_5,
    trade,
    current_time,
    enter_tags,
) -> tuple:
    if profit_init_ratio > 0.25:
        return True, f"exit_{strategy.long_btc_mode_name}_g"

    return False, None


def short_exit_grind(
    strategy,
    pair: str,
    current_rate: float,
    profit_stake: float,
    profit_ratio: float,
    profit_current_stake_ratio: float,
    profit_init_ratio: float,
    max_profit: float,
    max_loss: float,
    filled_entries,
    filled_exits,
    last_candle,
    previous_candle_1,
    previous_candle_2,
    previous_candle_3,
    previous_candle_4,
    previous_candle_5,
    trade,
    current_time,
    enter_tags,
) -> tuple:
    if profit_init_ratio > 0.25:
        return True, f"exit_{strategy.short_grind_mode_name}_g"

    return False, None
