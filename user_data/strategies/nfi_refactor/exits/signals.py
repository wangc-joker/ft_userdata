"""Shared exit signal aggregator compatibility module.

The long and short helpers live in dedicated modules so this file can remain a
stable import surface for the strategy adapter.
"""

from nfi_refactor.exits.signals_long import long_exit_signals
from nfi_refactor.exits.signals_short import short_exit_signals

__all__ = ["long_exit_signals", "short_exit_signals"]
