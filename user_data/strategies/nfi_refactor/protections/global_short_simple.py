"""Global protection column helper extracted from NFI."""

from pandas import DataFrame

def apply_short_simple_protections(df: DataFrame) -> DataFrame:
  df["protections_short_rebuy"] = True

  return df

