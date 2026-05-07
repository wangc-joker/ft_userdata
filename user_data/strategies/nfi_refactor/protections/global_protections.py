"""Global protection columns extracted from NostalgiaForInfinityX7.

These columns are used by entry signals and position adjustment guards. Keep the
logic mechanically equivalent while parity migration is in progress.
"""

from pandas import DataFrame

from nfi_refactor.protections.global_long import apply_long_global_protection
from nfi_refactor.protections.global_long_simple import apply_long_simple_protections
from nfi_refactor.protections.global_short import apply_short_global_protection
from nfi_refactor.protections.global_short_dump import apply_short_dump_protection
from nfi_refactor.protections.global_short_pump import apply_short_pump_protection
from nfi_refactor.protections.global_short_simple import apply_short_simple_protections


def apply_global_protections(df: DataFrame) -> DataFrame:
  df = apply_long_global_protection(df)
  df = apply_long_simple_protections(df)
  df = apply_short_global_protection(df)
  df = apply_short_pump_protection(df)
  df = apply_short_dump_protection(df)
  df = apply_short_simple_protections(df)
  return df
