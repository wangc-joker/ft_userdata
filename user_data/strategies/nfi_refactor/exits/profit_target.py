from __future__ import annotations

"""Profit target compatibility module.

The marker and exit-decision helpers live in dedicated modules so this file can
remain a stable import surface for the strategy adapter.
"""

from nfi_refactor.exits.profit_target_marker import mark_profit_target
from nfi_refactor.exits.profit_target_exit import exit_profit_target

__all__ = ["mark_profit_target", "exit_profit_target"]
