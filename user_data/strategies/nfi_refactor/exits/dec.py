"""DEC exit signal compatibility module.

The long and short DEC condition libraries live in dedicated modules so this
file can remain a small stable import surface for the strategy adapter.
"""

from nfi_refactor.exits.dec_long import long_exit_dec
from nfi_refactor.exits.dec_short import short_exit_dec

__all__ = ["long_exit_dec", "short_exit_dec"]
