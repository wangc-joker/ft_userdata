"""Global protection column helper extracted from NFI."""

from pandas import DataFrame

def apply_long_simple_protections(df: DataFrame) -> DataFrame:
  df["global_protections_long_pump"] = True

  df["global_protections_long_dump"] = True

  df["protections_long_rebuy"] = True


  return df

