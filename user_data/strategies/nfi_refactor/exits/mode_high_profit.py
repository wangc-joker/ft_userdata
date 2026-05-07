"""High-profit exit mode compatibility imports."""

from nfi_refactor.exits.mode_high_profit_long import long_exit_high_profit
from nfi_refactor.exits.mode_high_profit_short import short_exit_high_profit

__all__ = [
  "long_exit_high_profit",
  "short_exit_high_profit",
]
