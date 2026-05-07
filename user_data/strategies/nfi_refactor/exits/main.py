"""Main profit ladder exit helper compatibility module.

The long and short helpers live in dedicated modules so this file can remain a
stable import surface for the strategy adapter.
"""

from nfi_refactor.exits.main_long import long_exit_main
from nfi_refactor.exits.main_short import short_exit_main

__all__ = ["long_exit_main", "short_exit_main"]
