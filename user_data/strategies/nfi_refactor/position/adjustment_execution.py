"""Shared position-adjustment handler execution helpers."""

from nfi_refactor.position.adjustment_context import AdjustmentCallContext


def call_adjustment_handler(adjustment_func, context: AdjustmentCallContext):
  return adjustment_func(
    context.trade,
    context.enter_tags,
    context.current_time,
    context.current_rate,
    context.current_profit,
    context.min_stake,
    context.max_stake,
    context.current_entry_rate,
    context.current_exit_rate,
    context.current_entry_profit,
    context.current_exit_profit,
  )
