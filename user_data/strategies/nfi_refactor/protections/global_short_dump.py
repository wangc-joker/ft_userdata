"""Global protection column helper extracted from NFI."""

from pandas import DataFrame

def apply_short_dump_protection(df: DataFrame) -> DataFrame:
  df["global_protections_short_dump"] = (
    # 15m & 1h up move, 15m & 1h still not high enough, 4h still low, 1d still low & downtrend
    (
      (df["RSI_3_15m"] < 80.0)
      | (df["RSI_3_1h"] < 70.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["CCI_20_15m"] > 400.0)
      | (df["RSI_14_1h"] > 75.0)
      | (df["CCI_20_1h"] > 250.0)
      | (df["RSI_14_4h"] > 60.0)
      | (df["AROOND_14_4h"] < 50.0)
      | (df["CCI_20_4h"] > 200.0)
      | (df["RSI_14_1d"] > 50.0)
      | (df["AROOND_14_1d"] < 75.0)
      | (df["ROC_9_1d"] > -30.0)
    )
    # 15m up move, 15m still low, 1h & 4h & 1d still not high
    & (
      (df["RSI_3_15m"] < 85.0)
      | (df["AROOND_14_15m"] < 50.0)
      | (df["RSI_14_1h"] > 70.0)
      | (df["WILLR_14_1h"] > -50.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
      | (df["AROOND_14_1h"] < 75.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["WILLR_14_4h"] > -50.0)
      | (df["AROOND_14_4h"] < 25.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
      | (df["RSI_14_1d"] > 70.0)
    )
    # 1h & 4h up move, 15m & 1h & 4h still not high enough, 1d still low & downtrend
    & (
      (df["RSI_3_1h"] < 70.0)
      | (df["RSI_3_4h"] < 90.0)
      | (df["RSI_14_15m"] > 95.0)
      | (df["CCI_20_15m"] > 600.0)
      | (df["RSI_14_1h"] > 95.0)
      | (df["CCI_20_1h"] > 600.0)
      | (df["RSI_14_4h"] > 95.0)
      | (df["WILLR_14_4h"] > -10.0)
      | (df["CCI_20_4h"] > 600.0)
      | (df["RSI_14_1d"] > 40.0)
      | (df["ROC_9_1d"] > -20.0)
    )
  )


  return df

