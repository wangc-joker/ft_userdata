"""Rebuy position-adjustment handler selector helpers."""

from nfi_refactor.position.adjustment_context import AdjustmentModeState


def select_long_rebuy_adjustment_func(strategy, state: AdjustmentModeState):
  return (
    strategy.long_rebuy_adjust_trade_position_v3
    if state.is_system_v3_family
    else strategy.long_rebuy_adjust_trade_position
  )


def select_short_rebuy_adjustment_func(strategy, state: AdjustmentModeState):
  return (
    strategy.short_rebuy_adjust_trade_position_v3
    if state.is_system_v3_family
    else strategy.short_rebuy_adjust_trade_position
  )
