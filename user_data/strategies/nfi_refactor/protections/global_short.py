"""Global protection column helper extracted from NFI."""

from pandas import DataFrame

def apply_short_global_protection(df: DataFrame) -> DataFrame:
  df["protections_short_global"] = (
    # 5m & 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h still low, 1h uptrend
    (
      (df["RSI_3"] < 90.0)
      | (df["RSI_3_15m"] < 75.0)
      | (df["RSI_3_1h"] < 75.0)
      | (df["RSI_3_4h"] < 75.0)
      | (df["RSI_14_15m"] > 90.0)
      | (df["RSI_14_1h"] > 85.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
      | (df["ROC_9_1h"] < 15.0)
    )
    # 5m & 15m up move, 15m & 1h & 4h still low, 15m & 1h low, 4h still low
    & (
      (df["RSI_3"] < 90.0)
      | (df["RSI_3_15m"] < 75.0)
      | (df["RSI_14_15m"] > 60.0)
      | (df["RSI_14_1h"] > 50.0)
      | (df["RSI_14_4h"] > 40.0)
      | (df["AROONU_14_15m"] > 20.0)
      | (df["AROONU_14_1h"] > 20.0)
      | (df["AROONU_14_4h"] > 40.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h still low, 4h low
    & (
      (df["RSI_3_15m"] < 90.0)
      | (df["RSI_3_1h"] < 60.0)
      | (df["RSI_3_4h"] < 60.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 70.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["AROONU_14_1h"] > 60.0)
      | (df["AROONU_14_4h"] > 60.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0)
    )
    # 15m & 1h & 4h up move, 15m still not high enough, 1h & 4h still low, 1h low
    & (
      (df["RSI_3_15m"] < 90.0)
      | (df["RSI_3_1h"] < 60.0)
      | (df["RSI_3_4h"] < 35.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 60.0)
      | (df["RSI_14_4h"] > 60.0)
      | (df["AROONU_14_1h"] > 40.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h uptrend
    & (
      (df["RSI_3_15m"] < 95.0)
      | (df["RSI_3_1h"] < 80.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 80.0)
      | (df["CCI_20_1h"] > 200.0)
      | (df["CCI_20_4h"] > 150.0)
      | (df["ROC_9_4h"] < 20.0)
    )
    # 15m & 1h & 4h up move, 1h & 4h still now high enough, 15m uptrend, 1h still not high enough
    & (
      (df["RSI_3_15m"] < 95.0)
      | (df["RSI_3_1h"] < 50.0)
      | (df["RSI_3_4h"] < 50.0)
      | (df["RSI_14_1h"] > 70.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["CMF_20_15m"] < 0.20)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h & 1d uptrend
    & (
      (df["RSI_3_15m"] < 90.0)
      | (df["RSI_3_1h"] < 90.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 80.0)
      | (df["ROC_9_1h"] < 10.0)
      | (df["ROC_9_4h"] < 20.0)
      | (df["ROC_9_1d"] < 80.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h uptrend
    & (
      (df["RSI_3_15m"] < 90.0)
      | (df["RSI_3_1h"] < 80.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 80.0)
      | (df["CCI_20_1h"] > 250.0)
      | (df["CCI_20_4h"] > 200.0)
      | (df["ROC_9_1h"] < 10.0)
      | (df["ROC_9_4h"] < 40.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m uptrend, 4h still low
    & (
      (df["RSI_3_15m"] < 90.0)
      | (df["RSI_3_1h"] < 80.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["CMF_20_15m"] < 0.25)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 15m & 1h & 4h up move, 15m still not high enough, 1h & 4h still low, 4h still low
    & (
      (df["RSI_3_15m"] < 90.0)
      | (df["RSI_3_1h"] < 60.0)
      | (df["RSI_3_4h"] < 60.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 60.0)
      | (df["RSI_14_4h"] > 60.0)
      | (df["AROONU_14_4h"] > 50.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h still not high enough, 1h & 4h uptrend
    & (
      (df["RSI_3_15m"] < 85.0)
      | (df["RSI_3_1h"] < 85.0)
      | (df["RSI_3_4h"] < 85.0)
      | (df["AROONU_14_15m"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
      | (df["ROC_9_1h"] < 10.0)
      | (df["ROC_9_4h"] < 30.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m & 1h & 4h uptrend
    & (
      (df["RSI_3_15m"] < 85.0)
      | (df["RSI_3_1h"] < 85.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["RSI_14_15m"] > 85.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 80.0)
      | (df["CMF_20_15m"] < 0.20)
      | (df["CMF_20_1h"] < 0.10)
      | (df["CMF_20_4h"] < 0.10)
    )
    # 15m & 1h & 4h up move, 1h still low, 4h & 1d uptrend
    & (
      (df["RSI_3_15m"] < 85.0)
      | (df["RSI_3_1h"] < 85.0)
      | (df["RSI_3_4h"] < 70.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
      | (df["ROC_9_4h"] < 80.0)
      | (df["ROC_9_1d"] < 100.0)
    )
    # 15m & 1h & 4h up move, 1h & 4h still not high enough, 4h overbought
    & (
      (df["RSI_3_15m"] < 85.0)
      | (df["RSI_3_1h"] < 80.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["AROONU_14_4h"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
      | (df["ROC_9_4h"] < 10.0)
    )
    # 15m & 1h & 4h up move, 1h still nt high enough, 1h & 4h uptrend
    & (
      (df["RSI_3_15m"] < 85.0)
      | (df["RSI_3_1h"] < 70.0)
      | (df["RSI_3_4h"] < 70.0)
      | (df["AROONU_14_1h"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
      | (df["ROC_9_1h"] < 45.0)
      | (df["ROC_9_4h"] < 45.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h still low, 1h & 4h uptrend
    & (
      (df["RSI_3_15m"] < 85.0)
      | (df["RSI_3_1h"] < 70.0)
      | (df["RSI_3_4h"] < 70.0)
      | (df["RSI_14_15m"] > 70.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 80.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0)
      | (df["ROC_9_1h"] < 20.0)
      | (df["ROC_9_4h"] < 40.0)
    )
    # 15m & 1h & 4h up move, 4h still not high enough, 15m & 1h & 4h uptrend
    & (
      (df["RSI_3_15m"] < 80.0)
      | (df["RSI_3_1h"] < 80.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 75.0)
      | (df["ROC_9_15m"] < 10.0)
      | (df["ROC_9_1h"] < 10.0)
      | (df["ROC_9_4h"] < 20.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low, 1h & 4h uptrend
    & (
      (df["RSI_3_15m"] < 80.0)
      | (df["RSI_3_1h"] < 80.0)
      | (df["RSI_3_4h"] < 60.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 60.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0)
      | (df["ROC_9_1h"] < 20.0)
      | (df["ROC_9_4h"] < 20.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h still low, 15m & 1h & 4h uptrend
    & (
      (df["RSI_3_15m"] < 80.0)
      | (df["RSI_3_1h"] < 80.0)
      | (df["RSI_3_4h"] < 55.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["AROONU_14_4h"] > 70.0)
      | (df["ROC_9_15m"] < 10.0)
      | (df["ROC_9_1h"] < 10.0)
      | (df["ROC_9_4h"] < 20.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m uptrend
    & (
      (df["RSI_3_15m"] < 80.0)
      | (df["RSI_3_1h"] < 70.0)
      | (df["RSI_3_4h"] < 70.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 70.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["AROONU_14_4h"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] > 90.0)
      | (df["ROC_9_15m"] < 10.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h low, 4h overbought
    & (
      (df["RSI_3_15m"] < 80.0)
      | (df["RSI_3_1h"] < 70.0)
      | (df["RSI_3_4h"] < 70.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 80.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 40.0)
      | (df["ROC_9_4h"] < 30.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low
    & (
      (df["RSI_3_15m"] < 80.0)
      | (df["RSI_3_1h"] < 70.0)
      | (df["RSI_3_4h"] < 35.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 70.0)
      | (df["RSI_14_4h"] > 60.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low, 4h overbought
    & (
      (df["RSI_3_15m"] < 75.0)
      | (df["RSI_3_1h"] < 75.0)
      | (df["RSI_3_4h"] < 70.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["AROONU_14_4h"] > 30.0)
      | (df["ROC_9_4h"] < 10.0)
    )
    # 15m & 1h & 4h up move, 15m low, 1h uptrend
    & (
      (df["RSI_3_15m"] < 70.0)
      | (df["RSI_3_1h"] < 95.0)
      | (df["RSI_3_4h"] < 85.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] > 30.0)
      | (df["ROC_9_1h"] < 25.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h uptrend, 15m still low, 1h uptrend
    & (
      (df["RSI_3_15m"] < 70.0)
      | (df["RSI_3_1h"] < 70.0)
      | (df["RSI_3_4h"] < 70.0)
      | (df["CMF_20_15m"] < 0.20)
      | (df["CMF_20_1h"] < 0.20)
      | (df["CMF_20_4h"] < 0.20)
      | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0)
      | (df["ROC_9_1h"] < 50.0)
    )
    # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h uptrend
    & (
      (df["RSI_3_15m"] < 70.0)
      | (df["RSI_3_1h"] < 60.0)
      | (df["RSI_3_4h"] < 60.0)
      | (df["RSI_14_15m"] > 70.0)
      | (df["RSI_14_1h"] > 70.0)
      | (df["RSI_14_4h"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
      | (df["ROC_9_4h"] < 50.0)
    )
    # 1h & 4h up move, 1d still low, 15m & 4h still not high enough
    & (
      (df["RSI_3_1h"] < 95.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["RSI_14_1d"] > 50.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 1h & 4h up move, 1d still low, 1h & 4h & 1d uptrend
    & (
      (df["RSI_3_1h"] < 90.0)
      | (df["RSI_3_4h"] < 90.0)
      | (df["RSI_14_1d"] > 50.0)
      | (df["ROC_9_1h"] < 20.0)
      | (df["ROC_9_4h"] < 20.0)
      | (df["ROC_9_1d"] < 20.0)
    )
    # 4h up move, 15m & 1h & 4h still not high enough, 1d still low, 4h still not high enough, 1d still low
    & (
      (df["RSI_3_4h"] < 90.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 80.0)
      | (df["RSI_14_1d"] > 50.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
      | (df["STOCHRSIk_14_14_3_3_1d"] > 50.0)
    )
    # 4h up move, 15m & 1h & 4h still not high enough, 15m low, 15m & 1h & 4h uptrend
    & (
      (df["RSI_3_4h"] < 90.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 80.0)
      | (df["STOCHRSIk_14_14_3_3_15m"] > 40.0)
      | (df["ROC_9_15m"] < 20.0)
      | (df["ROC_9_1h"] < 15.0)
      | (df["ROC_9_4h"] < 15.0)
    )
    # 4h up move, 15m & 1h & 4h still not high enough, 1h still low, 1h & 4h overbought
    & (
      (df["RSI_3_4h"] < 90.0)
      | (df["RSI_14_15m"] > 80.0)
      | (df["RSI_14_1h"] > 80.0)
      | (df["RSI_14_4h"] > 90.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0)
      | (df["ROC_9_1h"] < 20.0)
      | (df["ROC_9_4h"] < 60.0)
    )
  )


  return df

