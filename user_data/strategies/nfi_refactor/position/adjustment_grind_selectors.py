"""Grind position-adjustment handler selector helpers."""

from nfi_refactor.position.adjustment_context import (
  AdjustmentCallContext,
  AdjustmentModeState,
)
from nfi_refactor.position.adjustment_grind_tags import (
  matches_long_grind_adjustment_v2_or_v3,
  matches_short_grind_adjustment_v2_or_v3,
)


def select_long_grind_adjustment_func(strategy, context: AdjustmentCallContext, state: AdjustmentModeState):
  if not state.is_long_grind_mode and not state.is_long_btc_mode and state.is_system_v3_family:
    if matches_long_grind_adjustment_v2_or_v3(strategy, context.enter_tags):
      return strategy.long_grind_adjust_trade_position_v3
  elif state.is_long_grind_mode or state.is_long_btc_mode or not state.is_v2_date:
    return strategy.long_grind_adjust_trade_position
  elif matches_long_grind_adjustment_v2_or_v3(strategy, context.enter_tags):
    return strategy.long_grind_adjust_trade_position_v2

  return None


def select_short_grind_adjustment_func(strategy, context: AdjustmentCallContext, state: AdjustmentModeState):
  if not state.is_short_grind_mode and state.is_system_v3_family:
    if matches_short_grind_adjustment_v2_or_v3(strategy, context.enter_tags):
      return strategy.short_grind_adjust_trade_position_v3
  elif state.is_short_grind_mode or not state.is_v2_date:
    return strategy.short_grind_adjust_trade_position
  elif matches_short_grind_adjustment_v2_or_v3(strategy, context.enter_tags):
    return strategy.short_grind_adjust_trade_position_v2

  return None
