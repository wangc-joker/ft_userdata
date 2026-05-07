"""Fallback custom-exit routing for trades not opened by X7 tags."""

from nfi_refactor.exits.custom_exit_call import call_custom_exit_mode
from nfi_refactor.exits.custom_exit_long_match import matches_any_long_mode
from nfi_refactor.exits.custom_exit_short_match import matches_any_short_mode


def route_custom_exit_fallback(
  strategy,
  pair,
  trade,
  current_time,
  current_rate,
  enter_tag,
  enter_tags,
  filled_entries,
  filled_exits,
  profit_stake,
  profit_ratio,
  profit_current_stake_ratio,
  profit_init_ratio,
  max_profit,
  max_loss,
  last_candle,
  previous_candle_1,
  previous_candle_2,
  previous_candle_3,
  previous_candle_4,
  previous_candle_5,
):
  fallback_exit_func = None
  if not trade.is_short and (not matches_any_long_mode(strategy, enter_tags)):
    fallback_exit_func = strategy.long_exit_normal
  if trade.is_short and (not matches_any_short_mode(strategy, enter_tags)):
    fallback_exit_func = strategy.short_exit_normal

  if fallback_exit_func is None:
    return None

  return call_custom_exit_mode(
    fallback_exit_func,
    enter_tag,
    pair,
    current_rate,
    profit_stake,
    profit_ratio,
    profit_current_stake_ratio,
    profit_init_ratio,
    max_profit,
    max_loss,
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
  )
