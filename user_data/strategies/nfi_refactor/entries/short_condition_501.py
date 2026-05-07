"""Short entry condition #501 extracted from NFI."""

import numpy as np
import pandas as pd

def append_short_501(df, short_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI short condition #501, a normal-mode short entry."""
    short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    short_entry_logic.append(df["protections_short_global"] == True)
    short_entry_logic.append(df["global_protections_short_pump"] == True)
    short_entry_logic.append(df["global_protections_short_dump"] == True)

    short_entry_logic.append(df["RSI_3_1h"] >= 5.0)
    short_entry_logic.append(df["RSI_3_4h"] >= 20.0)
    short_entry_logic.append(df["RSI_3_1d"] >= 20.0)
    short_entry_logic.append(df["RSI_14_1h"] > 20.0)
    short_entry_logic.append(df["RSI_14_4h"] > 20.0)
    short_entry_logic.append(df["RSI_14_1d"] > 10.0)
    # 5m up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3"] < 97.0) | (df["AROONU_14_4h"] > 60.0))
    # 5m up move, 4h still low
    short_entry_logic.append((df["RSI_3"] < 97.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0))
    # 5m & 15m strong up move
    short_entry_logic.append((df["RSI_3"] < 95.0) | (df["RSI_3_15m"] < 95.0))
    # 5m & 1h up move, 1d uptrend
    short_entry_logic.append((df["RSI_3"] < 95.0) | (df["RSI_3_1h"] < 90.0) | (df["ROC_9_1d"] < 100.0))
    # 5m up move, 15m & 1h still not high enough
    short_entry_logic.append((df["RSI_3"] < 95.0) | (df["AROOND_14_15m"] < 25.0) | (df["AROOND_14_1h"] < 25.0))
    # 4m up move, 1h & 4h still low
    short_entry_logic.append(
      (df["RSI_3"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 4m & 1h up move, 1h still low
    short_entry_logic.append(
      (df["RSI_3"] < 90.0) | (df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m & 1h up move, 4h low
    short_entry_logic.append((df["RSI_3"] < 90.0) | (df["RSI_3_1h"] < 80.0) | (df["AROONU_14_4h"] > 20.0))
    # 5m up move, 15m & 1h uptrend
    short_entry_logic.append((df["RSI_3"] < 90.0) | (df["CMF_20_15m"] < 0.30) | (df["CMF_20_1h"] < 0.30))
    # 5m up move, 15m stil low
    short_entry_logic.append((df["RSI_3"] < 90.0) | (df["AROONU_14_15m"] > 50.0))
    # 5m up move, 15m & 1h still not high enough
    short_entry_logic.append(
      (df["RSI_3"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 75.0)
    )
    # 15m up move, 1h low
    short_entry_logic.append((df["RSI_3_15m"] < 97.0) | (df["AROONU_14_1h"] > 30.0))
    # 15m & 1h up move, 4h still going up
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["CCI_20_change_pct_4h"] < -0.0)
    )
    # 15m & 1h up move, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 15m & 1h up move, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m & 1h up move, 1h still low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m & 4h up move, 1h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 75.0)
    )
    # 15m up move, 1d lost, 1h low
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["RSI_14_1d"] > 40.0) | (df["AROONU_14_1h"] > 40.0))
    # 15m up move, 15m & 4h uptrend
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["AROONU_14_15m"] < 90.0) | (df["AROONU_14_4h"] < 90.0)
    )
    # 15m up move, 15m stil not high enough, 1h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 10.0)
    )
    # 15m up move, 1h still not high enough, 4h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0) | (df["AROONU_14_4h"] > 20.0)
    )
    # 15m up move, 1h & 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 15m up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["AROONU_14_4h"] > 70.0))
    # 15m up move, 4h & 1d uptrend
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["ROC_9_4h"] < 30.0) | (df["ROC_9_1d"] < 50.0))
    # 15m up move, 1h up move, 1h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_change_pct_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m & 1h up move, 1h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
    )
    # 15m & 1h up move, 1h not high enough
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 90.0) | (df["AROOND_14_1h"] < 50.0))
    # 15m & 1h up move, 1d stil not high enough
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 90.0) | (df["RSI_14_1h"] > 80.0))
    # 15m & 1h up move, 1d uptrend
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 80.0) | (df["ROC_9_1d"] < 40.0))
    # 15m & 1h up move, 15m still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0)
    )
    # 15m & 4h up move, 1h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
    )
    # 15m & 4h up move, 1h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 90.0)
    )
    # 15m & 4h up move, 4h not high enough
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 90.0) | (df["AROOND_14_4h"] < 50.0))
    # 15m & 4h up move, 1d low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0)
    )
    # 15m & 4h up move, 1h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0)
    )
    # 15m & 4h up move, 4h low
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 60.0) | (df["AROONU_14_4h"] > 30.0))
    # 15m up move, 1h & 4h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["AROONU_14_1h"] > 40.0) | (df["AROONU_14_4h"] > 10.0)
    )
    # 15m up move, 1h still low, 4h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["AROONU_14_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 15m up move, 1h low, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 15m & 4h up move, 1d low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 20.0)
    )
    # 15m & 1h up move, 4h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0)
    )
    # 15m & 1h up move, 1d still low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 60.0)
    )
    # 15m & 1h up move, 1h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 15m & 1h up move, 4h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 15m & 4h down move, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 75.0)
    )
    # 15m & 4h up move, 15m low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0)
    )
    # 15m down move, 15m still not high enough, 4h low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_14_15m"] > 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0)
    )
    # 15m up move, 4h overbought
    short_entry_logic.append((df["RSI_3_15m"] < 85.0) | (df["ROC_9_4h"] < 50.0))
    # 15m & 1h up move, 1h still not high enough
    short_entry_logic.append((df["RSI_3_15m"] < 80.0) | (df["RSI_3_1h"] < 70.0) | (df["AROONU_14_1h"] > 60.0))
    # 15m & 4h up move, 15m still low
    short_entry_logic.append((df["RSI_3_15m"] < 80.0) | (df["RSI_3_4h"] < 80.0) | (df["AROONU_14_15m"] > 50.0))
    # 15m up move, 1h low
    short_entry_logic.append((df["RSI_3_15m"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0))
    # 15m & 1h up move, 1h low
    short_entry_logic.append((df["RSI_3_15m"] < 70.0) | (df["RSI_3_1h"] < 70.0) | (df["AROONU_14_1h"] > 30.0))
    # 15m up move, 15m still not high enough, 1h still low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 1h & 4h up move, 1h still not high enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
    )
    # 1h up move, 4h low
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0))
    # 1h & 4h up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 95.0) | (df["UO_7_14_28_4h"] > 60.0))
    # 1h & 4h up move, 4h still low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 1h & 4h up move, 4h uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 85.0) | (df["ROC_9_4h"] < 40.0))
    # 1h & 1d strong up move
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_3_1d"] < 95.0))
    # 1h up move, 4h still low
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_14_4h"] > 60.0))
    # 1h up move, 1d still low, 1h uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_14_1d"] > 50.0) | (df["ROC_9_1h"] < 30.0))
    # 1h & 4h strong up move
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["MFI_14_1h"] < 95.0) | (df["RSI_3_4h"] < 95.0))
    # 1h up move, 1d still low, 1h uptrend
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 50.0) | (df["ROC_9_1h"] < 20.0)
    )
    # 1h strong up move, 15m still move higher
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["CCI_20_change_pct_15m"] < -0.0))
    # 1h & 4h up move, 1h still low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 1h & 4h up move, 1d still not high enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 70.0)
    )
    # 1h up move, 4h low, 1d overbought
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["AROONU_14_4h"] > 20.0) | (df["ROC_9_1d"] < 50.0))
    # 1h up move, 1h still low, 1d uptrend
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0) | (df["ROC_9_1d"] < 50.0)
    )
    # 1h up move, 1h still not high enough, 1d low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0)
    )
    # 1h up move, 4h low, 1h uptrend
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0) | (df["ROC_9_1h"] < 10.0)
    )
    # 1h up move, 4h low, 1h overbought
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0) | (df["ROC_9_1h"] < 30.0)
    )
    # 1h up move, 15m & 1h uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["ROC_9_15m"] < 15.0) | (df["ROC_9_1h"] < 15.0))
    # 1h up move, 15m & 4h still low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 1h & 4h up move, 15m still not high enough
    short_entry_logic.append((df["RSI_3_1h"] < 85.0) | (df["RSI_3_4h"] < 85.0) | (df["AROOND_14_15m"] < 50.0))
    # 1h & 4h up move, 15m still not high enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 85.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 90.0)
    )
    # 1h up move, 15m still not high enough, 1h still low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 1h up move, 1h still low
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0))
    # 4h & 1d strong up move
    short_entry_logic.append((df["RSI_3_4h"] < 95.0) | (df["RSI_3_1d"] < 95.0))
    # 4h up move, 15m still low, 1h not high enough
    short_entry_logic.append(
      (df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["AROOND_14_1h"] < 25.0)
    )
    # 4h up move, 15m still not high enough, 4h overbought
    short_entry_logic.append(
      (df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["ROC_9_4h"] < 60.0)
    )
    # 4h up move, 15m uptrend
    short_entry_logic.append((df["RSI_3_4h"] < 95.0) | (df["ROC_9_15m"] < 20.0))
    # 4h up move, 1h uptrend
    short_entry_logic.append((df["RSI_3_4h"] < 95.0) | (df["ROC_9_1h"] < 20.0))
    # 4h up move, 1h & 4h overbought
    short_entry_logic.append((df["RSI_3_4h"] < 95.0) | (df["ROC_9_1h"] < 30.0) | (df["ROC_9_4h"] < 60.0))
    # 4h up move, 1h still low
    short_entry_logic.append((df["RSI_3_4h"] < 90.0) | (df["AROONU_14_1h"] > 40.0))
    # 4h up move, 1d still low, 4h uptrend
    short_entry_logic.append((df["RSI_3_4h"] < 85.0) | (df["RSI_14_1d"] > 40.0) | (df["ROC_9_4h"] < 20.0))
    # 4h up move, 4h still low
    short_entry_logic.append((df["RSI_3_4h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0))
    # 4h up move, 1h low
    short_entry_logic.append((df["RSI_3_4h"] < 70.0) | (df["AROONU_14_1h"] > 25.0))
    # 4h up move, 1d low
    short_entry_logic.append((df["RSI_3_4h"] < 70.0) | (df["AROONU_14_1d"] > 20.0))
    # 4h up move, 1h low
    short_entry_logic.append((df["RSI_3_4h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0))
    # 4h up move, 1d low
    short_entry_logic.append((df["RSI_3_4h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 20.0))
    # 1d up move, 1h & 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1d"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 4h still not high enough, 4h overbought, 4h uptrend
    short_entry_logic.append(
      (df["RSI_14_4h"] > 80.0) | (df["ROC_9_4h"] < 40.0) | (df["CCI_20_change_pct_4h"] < 0.0)
    )
    # 15m & 1h uptrend, 4h still low
    short_entry_logic.append(
      (df["CMF_20_15m"] < 0.30) | (df["CMF_20_1h"] < 0.30) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 15m uptrend, 1h low
    short_entry_logic.append((df["AROONU_14_15m"] < 100.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0))
    # 1h & 4h uptrend
    short_entry_logic.append((df["AROONU_14_1h"] < 100.0) | (df["AROONU_14_4h"] < 100.0))
    # 1h uptrend, 4h uptrend
    short_entry_logic.append((df["AROONU_14_1h"] < 100.0) | (df["ROC_9_4h"] < 20.0))
    # 4h uptrend, 1d uptrend
    short_entry_logic.append((df["AROONU_14_4h"] < 100.0) | (df["AROONU_14_1d"] < 100.0))
    # 4h uptrend, 15m uptrend
    short_entry_logic.append((df["AROONU_14_4h"] < 100.0) | (df["ROC_9_15m"] < 10.0))
    # 4h uptrend, 1h uptrend
    short_entry_logic.append((df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 20.0))
    # 1d uptrend, 15m uptrend
    short_entry_logic.append((df["AROONU_14_1d"] < 100.0) | (df["ROC_9_15m"] < 20.0))
    # 1d uptrend, 1h uptrend
    short_entry_logic.append((df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1h"] < 20.0))
    # 15m still not high enough, 1h & 4h overbought
    short_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["ROC_9_1h"] < 30.0) | (df["ROC_9_4h"] < 60.0)
    )
    # 1h & 4h overbought, 1h uptrend
    short_entry_logic.append(
      (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 40.0) | (df["CCI_20_change_pct_1h"] < 0.0)
    )
    # 1h & 4h overbought, 4h uptrend
    short_entry_logic.append(
      (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 40.0) | (df["CCI_20_change_pct_4h"] < 0.0)
    )
    # 1h & 4h & 1d uptrend
    short_entry_logic.append((df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 10.0) | (df["ROC_9_1d"] < 20.0))
    # 5m green, 15m still not high enough
    short_entry_logic.append((df["change_pct"] < 5.0) | (df["AROOND_14_15m"] < 50.0))
    # 5m green, 15m still not high enough
    short_entry_logic.append((df["change_pct"] < 5.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 90.0))
    # pump in the last half hour, 1h low
    short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (df["AROONU_14_1h"] > 30.0))
    # pump in the last half hour, 15m still low
    short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (df["STOCHRSIk_14_14_3_3_15m"] > 40.0))
    # pump in the last half hour, 1d uptrend
    short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (df["ROC_9_1d"] < 20.0))
    # big pump in the last 4 hours, 15m still low
    short_entry_logic.append((df["close"] < (df["close_min_48"] * 1.50)) | (df["AROONU_14_15m"] > 50.0))

    # Logic
    short_entry_logic.append(df["EMA_12"] > df["EMA_26"])
    short_entry_logic.append((df["EMA_12"] - df["EMA_26"]) > (df["open"] * 0.030))
    short_entry_logic.append((df["EMA_12"].shift() - df["EMA_26"].shift()) > (df["open"] / 100.0))
    short_entry_logic.append(df["close"] > (df["BBU_20_2.0"] * 1.004))
