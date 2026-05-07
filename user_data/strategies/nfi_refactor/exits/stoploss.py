"""Emergency stoploss exit helper compatibility module.

The long and short helpers live in dedicated modules so this file can remain a
stable import surface for the strategy adapter.
"""

from nfi_refactor.exits.stoploss_long import long_exit_stoploss
from nfi_refactor.exits.stoploss_short import short_exit_stoploss

__all__ = ["long_exit_stoploss", "short_exit_stoploss"]
