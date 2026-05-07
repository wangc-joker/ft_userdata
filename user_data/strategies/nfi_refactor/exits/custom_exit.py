"""Custom exit orchestration extracted from NostalgiaForInfinityX7.

This function routes an open trade to the original long/short mode-specific exit
handlers and preserves NFI's exit reason text exactly.
"""

from nfi_refactor.exits.custom_exit_context import prepare_custom_exit_context
from nfi_refactor.exits.custom_exit_long import route_long_custom_exit
from nfi_refactor.exits.custom_exit_short import route_short_custom_exit


def custom_exit(
  strategy, pair: str, trade: "Trade", current_time: "datetime", current_rate: float, current_profit: float, **kwargs
):
  context = prepare_custom_exit_context(strategy, pair, trade, current_rate)
  if context is None:
    return None

  exit_reason = route_long_custom_exit(strategy, pair, trade, current_time, current_rate, **context)
  if exit_reason is not None:
    return exit_reason

  exit_reason = route_short_custom_exit(strategy, pair, trade, current_time, current_rate, **context)
  if exit_reason is not None:
    return exit_reason

  return None

# Custom Stake Amount
# ---------------------------------------------------------------------------------------------
