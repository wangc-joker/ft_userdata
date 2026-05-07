"""Rebuy position-adjustment routing helpers."""

from nfi_refactor.position.adjustment_context import (
  AdjustmentCallContext,
  AdjustmentModeState,
)
from nfi_refactor.position.adjustment_execution import call_adjustment_handler
from nfi_refactor.position.adjustment_rebuy_selectors import (
  select_long_rebuy_adjustment_func,
  select_short_rebuy_adjustment_func,
)
from nfi_refactor.position.adjustment_rebuy_tags import (
  matches_long_rebuy_adjustment,
  matches_short_rebuy_adjustment,
)


def route_rebuy_adjustment(
  strategy,
  context: AdjustmentCallContext,
  state: AdjustmentModeState,
):
  if not context.trade.is_short and matches_long_rebuy_adjustment(strategy, context.enter_tags):
    adjustment_func = select_long_rebuy_adjustment_func(strategy, state)
    return True, call_adjustment_handler(adjustment_func, context)

  if context.trade.is_short and matches_short_rebuy_adjustment(strategy, context.enter_tags):
    adjustment_func = select_short_rebuy_adjustment_func(strategy, state)
    return True, call_adjustment_handler(adjustment_func, context)

  return False, None
