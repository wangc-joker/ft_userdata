"""Williams-R exit signal compatibility module.

The long and short Williams-R condition libraries live in dedicated modules so
this file can remain a small stable import surface for the strategy adapter.
"""

from nfi_refactor.exits.williams_long import long_exit_williams_r
from nfi_refactor.exits.williams_short import short_exit_williams_r

__all__ = ["long_exit_williams_r", "short_exit_williams_r"]
