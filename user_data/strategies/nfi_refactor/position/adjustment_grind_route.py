"""Grind position-adjustment routing helpers."""

from nfi_refactor.position.adjustment_context import (
  AdjustmentCallContext,
  AdjustmentModeState,
)
from nfi_refactor.position.adjustment_execution import call_adjustment_handler
from nfi_refactor.position.adjustment_grind_selectors import (
  select_long_grind_adjustment_func,
  select_short_grind_adjustment_func,
)


def route_long_grind_adjustment(
  strategy,
  context: AdjustmentCallContext,
  state: AdjustmentModeState,
):
  adjustment_func = select_long_grind_adjustment_func(strategy, context, state)
  if adjustment_func:
    return call_adjustment_handler(adjustment_func, context)

  return None


def route_short_grind_adjustment(
  strategy,
  context: AdjustmentCallContext,
  state: AdjustmentModeState,
):
  adjustment_func = select_short_grind_adjustment_func(strategy, context, state)
  if adjustment_func:
    return call_adjustment_handler(adjustment_func, context)

  return None


def select_grind_route_func(context: AdjustmentCallContext):
  if not context.trade.is_short:
    return route_long_grind_adjustment

  if context.trade.is_short:
    return route_short_grind_adjustment

  return None


def route_grind_adjustment(
  strategy,
  context: AdjustmentCallContext,
  state: AdjustmentModeState,
):
  route_func = select_grind_route_func(context)
  if route_func:
    return route_func(
      strategy,
      context,
      state,
    )

  return None
