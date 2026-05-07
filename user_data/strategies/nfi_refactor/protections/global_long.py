"""Long global protection column router extracted from NFI."""

from pandas import DataFrame
from nfi_refactor.protections.global_long_chunk_0 import long_global_chunk_0
from nfi_refactor.protections.global_long_chunk_1 import long_global_chunk_1
from nfi_refactor.protections.global_long_chunk_2 import long_global_chunk_2
from nfi_refactor.protections.global_long_chunk_3 import long_global_chunk_3
from nfi_refactor.protections.global_long_chunk_4 import long_global_chunk_4
from nfi_refactor.protections.global_long_chunk_5 import long_global_chunk_5


def apply_long_global_protection(df: DataFrame) -> DataFrame:
  df["protections_long_global"] = (
    long_global_chunk_0(df)
    & long_global_chunk_1(df)
    & long_global_chunk_2(df)
    & long_global_chunk_3(df)
    & long_global_chunk_4(df)
    & long_global_chunk_5(df)
  )
  return df
