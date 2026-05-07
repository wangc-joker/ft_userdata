"""Position-adjustment context and mode-state helpers."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class AdjustmentCallContext:
  trade: object
  enter_tags: list
  current_time: object
  current_rate: float
  current_profit: float
  min_stake: object
  max_stake: float
  current_entry_rate: float
  current_exit_rate: float
  current_entry_profit: float
  current_exit_profit: float


@dataclass
class AdjustmentModeState:
  is_long_grind_mode: bool
  is_long_btc_mode: bool
  is_short_grind_mode: bool
  is_v2_date: bool
  is_system_v3_family: bool


def get_adjustment_enter_tags(trade) -> list:
  enter_tag = "empty"
  if hasattr(trade, "enter_tag") and trade.enter_tag is not None:
    enter_tag = trade.enter_tag
  return enter_tag.split()


def all_tags_in(enter_tags, valid_tags):
  return all(c in valid_tags for c in enter_tags)


def any_tags_in(enter_tags, valid_tags):
  return any(c in valid_tags for c in enter_tags)


def is_long_grind_mode(strategy, enter_tags):
  return all_tags_in(enter_tags, strategy.long_grind_mode_tags)


def is_long_btc_mode(strategy, enter_tags):
  return all_tags_in(enter_tags, strategy.long_btc_mode_tags)


def is_short_grind_mode(strategy, enter_tags):
  return all_tags_in(enter_tags, strategy.short_grind_mode_tags)


def is_v2_adjustment_date(strategy, trade):
  is_backtest = strategy.is_backtest_mode()
  return trade.open_date_utc.replace(tzinfo=None) >= datetime(2025, 2, 13) or is_backtest


def is_system_v3_family(strategy, trade):
  return (
    strategy.is_system_v3(trade)
    or strategy.is_system_v3_1(trade)
    or strategy.is_system_v3_2(trade)
  )


def build_adjustment_call_context(
  trade,
  enter_tags,
  current_time,
  current_rate: float,
  current_profit: float,
  min_stake,
  max_stake: float,
  current_entry_rate: float,
  current_exit_rate: float,
  current_entry_profit: float,
  current_exit_profit: float,
) -> AdjustmentCallContext:
  return AdjustmentCallContext(
    trade=trade,
    enter_tags=enter_tags,
    current_time=current_time,
    current_rate=current_rate,
    current_profit=current_profit,
    min_stake=min_stake,
    max_stake=max_stake,
    current_entry_rate=current_entry_rate,
    current_exit_rate=current_exit_rate,
    current_entry_profit=current_entry_profit,
    current_exit_profit=current_exit_profit,
  )


def build_adjustment_mode_state(strategy, trade, enter_tags) -> AdjustmentModeState:
  return AdjustmentModeState(
    is_long_grind_mode=is_long_grind_mode(strategy, enter_tags),
    is_long_btc_mode=is_long_btc_mode(strategy, enter_tags),
    is_short_grind_mode=is_short_grind_mode(strategy, enter_tags),
    is_v2_date=is_v2_adjustment_date(strategy, trade),
    is_system_v3_family=is_system_v3_family(strategy, trade),
  )
