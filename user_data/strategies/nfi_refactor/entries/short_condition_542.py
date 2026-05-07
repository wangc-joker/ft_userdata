"""Short entry condition #542 extracted from NFI."""

import numpy as np
import pandas as pd

def append_short_542(df, short_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI short condition #542, the quick-mode short entry."""
    # Protections
    short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    short_entry_logic.append(df["protections_short_global"] == True)

    # 5m & 15m up move, 15m stil low
    short_entry_logic.append((df["RSI_3"] < 90.0) | (df["RSI_3_15m"] < 80.0) | (df["AROONU_14_15m"] > 60.0))
    # 15m & 1h up move, 4h still low
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["RSI_14_4h"] > 60.0))
    # 15m & 1h up move, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 15m & 1h up move, 1h still moving higher
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 90.0) | (df["CCI_20_change_pct_1h"] < -0.0)
    )
    # 15m & 4h up move, 4h still moving higher
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 95.0) | (df["CCI_20_change_pct_4h"] < -0.0)
    )
    # 15m & 1d up move, 4h uptrend
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_1d"] < 80.0) | (df["ROC_9_4h"] < 20.0))
    # 15m up move, 15m & 4h high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["AROONU_14_15m"] < 100.0) | (df["AROONU_14_4h"] < 100.0)
    )
    # 15m up move, 15m still not high enough, 1d uptrend
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0) | (df["ROC_9_1d"] < 80.0)
    )
    # 15m & 4h up move, 15m still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0)
    )
    # 15m & 4h up move, 1d uptrend
    short_entry_logic.append((df["RSI_3_15m"] < 85.0) | (df["RSI_3_4h"] < 85.0) | (df["ROC_9_1d"] < 50.0))
    # 15m & 4h up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3_15m"] < 85.0) | (df["RSI_3_4h"] < 80.0) | (df["RSI_14_4h"] > 60.0))
    # 15m up move, 15m still not high enough, 4h still low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0) | (df["AROONU_14_4h"] > 50.0)
    )
    # 15m up move, 4h overbought
    short_entry_logic.append((df["RSI_3_15m"] < 85.0) | (df["ROC_9_4h"] < 50.0))
    # 15m & 1h up move, 15m still low
    short_entry_logic.append((df["RSI_3_15m"] < 70.0) | (df["RSI_3_1h"] < 70.0) | (df["AROONU_14_15m"] > 40.0))
    # 15m & 1h up move, 15m still low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 70.0) | (df["RSI_3_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 40.0)
    )
    # # 15m & 1h up move, 4h low
    short_entry_logic.append((df["RSI_3_15m"] < 70.0) | (df["RSI_3_1h"] < 60.0) | (df["AROONU_14_4h"] > 40.0))
    # 1h & 1d up move, 1h still moving higher
    short_entry_logic.append(
      (df["RSI_3_1h"] < 97.0) | (df["RSI_3_1d"] < 95.0) | (df["CCI_20_change_pct_1h"] < -0.0)
    )
    # 1h & 4h up move, 15m still not high enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0)
    )
    # 1h & 4h up move, 1d uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 95.0) | (df["ROC_9_1d"] < 100.0))
    # 1h & 4h up move, 1d still low
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 85.0) | (df["RSI_14_1d"] > 50.0))
    # 1h up move, 4h still low, 1h still moving higher
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_14_4h"] > 60.0) | (df["CCI_20_change_pct_1h"] < -0.0)
    )
    # 1h up move, 4h low
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["AROONU_14_4h"] > 10.0))
    # 1h & 4h up move, 1h still moving higher
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["CCI_20_change_pct_1h"] < -0.0)
    )
    # 1h & 4h up move, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 1h & 1d up move, 15m still low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_1d"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0)
    )
    # 1h up move, 15m high
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["AROONU_14_15m"] < 100.0))
    # 1h up move, 4h low
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0))
    # 1h up move, 4h still low, 1h still moving higher
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0) | (df["CCI_20_change_pct_1h"] < -0.0)
    )
    # 1h up move, 15m uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["ROC_9_15m"] < 30.0))
    # 1h up move, 15m & 4h uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["ROC_9_15m"] < 20.0) | (df["ROC_9_4h"] < 20.0))
    # 1h & 4h up move, 4h still moving higher
    short_entry_logic.append(
      (df["RSI_3_1h"] < 85.0) | (df["RSI_3_4h"] < 80.0) | (df["CCI_20_change_pct_4h"] < -0.0)
    )
    # 1h up move, 15m low
    short_entry_logic.append((df["RSI_3_1h"] < 85.0) | (df["AROONU_14_15m"] > 40.0))
    # 1h up move, 4h still not high enough, 1d low
    short_entry_logic.append((df["RSI_3_1h"] < 85.0) | (df["AROONU_14_4h"] > 80.0) | (df["RSI_14_1d"] > 40.0))
    # 1h & 4h up move, 4h still low
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["RSI_3_4h"] < 80.0) | (df["AROONU_14_4h"] > 50.0))
    # 1h & 4h up move, 1d still low
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["RSI_3_4h"] < 80.0) | (df["AROONU_14_1d"] > 50.0))
    # 1h & 4h up move, 1d low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 80.0) | (df["RSI_3_4h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0)
    )
    # 1h up move, 1d still low, 1d uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["AROONU_14_1d"] > 50.0) | (df["ROC_9_1d"] < 30.0))
    # 1h up move, 1d low
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 20.0))
    # 1h up move, 4h & 1d uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["ROC_9_4h"] < 20.0) | (df["ROC_9_1d"] < 40.0))
    # 4h up move, 1d low
    short_entry_logic.append((df["RSI_3_4h"] < 95.0) | (df["RSI_14_1d"] > 40.0))
    # 4h down move, 15m still not high enough, 1d low
    short_entry_logic.append(
      (df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0) | (df["AROOND_14_1d"] < 75.0)
    )
    # 4h up move, 1h & 4h uptrend
    short_entry_logic.append((df["RSI_3_4h"] < 95.0) | (df["ROC_9_1h"] < 20.0) | (df["ROC_9_4h"] < 20.0))
    # 4h up move, 15m low
    short_entry_logic.append((df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 45.0))
    # 4h up move, 4h & 1d uptrend
    short_entry_logic.append((df["RSI_3_4h"] < 90.0) | (df["ROC_9_4h"] < 20.0) | (df["ROC_9_1d"] < 40.0))
    # 4h up move, 15m still not high enough
    short_entry_logic.append((df["RSI_3_4h"] < 85.0) | (df["AROONU_14_15m"] > 60.0))
    # 4h up move, 15m low
    short_entry_logic.append((df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 30.0))
    # 4h up move, 4h uptrend
    short_entry_logic.append((df["RSI_3_4h"] < 80.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_4h"] < 20.0))
    # 4h up move, 15m still low, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_4h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0) | (df["AROONU_14_4h"] > 80.0)
    )
    # 4h up move, 15m still low, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 1d up move, 4h low
    short_entry_logic.append((df["RSI_3_1d"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0))
    # 4h still not high enough, 4h overbought, 4h uptrend
    short_entry_logic.append(
      (df["RSI_14_4h"] > 80.0) | (df["ROC_9_4h"] < 40.0) | (df["CCI_20_change_pct_4h"] < 0.0)
    )
    # 15m & 1h high, 4h uptrend
    short_entry_logic.append(
      (df["AROONU_14_15m"] < 100.0) | (df["AROONU_14_1h"] < 100.0) | (df["ROC_9_4h"] < 20.0)
    )
    # 15m & 4h high, 1h uptrend
    short_entry_logic.append(
      (df["AROONU_14_15m"] < 100.0) | (df["AROONU_14_4h"] < 100.0) | (df["ROC_9_1h"] < 20.0)
    )
    # 15m high, 1d low
    short_entry_logic.append((df["AROONU_14_15m"] < 100.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 20.0))
    # 15m high & uptrend
    short_entry_logic.append((df["AROONU_14_15m"] < 100.0) | (df["ROC_9_15m"] < 30.0))
    # 15m high, 1h & 4h uptrend
    short_entry_logic.append((df["AROONU_14_15m"] < 100.0) | (df["ROC_9_1h"] < 20.0) | (df["ROC_9_4h"] < 20.0))
    # 1h high, 15m uptrend
    short_entry_logic.append((df["AROONU_14_1h"] < 100.0) | (df["ROC_9_15m"] < 20.0))
    # 15m & 4h still not high enough
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0))
    # 1h & 4h overbought, 1h uptrend
    short_entry_logic.append(
      (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 40.0) | (df["CCI_20_change_pct_1h"] < 0.0)
    )
    # 1h & 4h overbought, 4h uptrend
    short_entry_logic.append(
      (df["ROC_9_1h"] < 10.0) | (df["ROC_9_4h"] < 40.0) | (df["CCI_20_change_pct_4h"] < 0.0)
    )
    # 1d bot wick, 4h still not high enough
    short_entry_logic.append((df["bot_wick_pct_1d"] < 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0))
    # rise in the last 12 hours, relatively stable before the 12 hours
    short_entry_logic.append(
      (df["close"] < (df["low_min_12_1h"] * 1.30)) | (df["low_min_12_1h"] > (df["low_min_24_1h"] * 1.10))
    )
    # big pump in the last 30 days, 4h up move
    short_entry_logic.append((df["close"] < (df["low_min_30_1d"] * 4.0)) | (df["RSI_3_4h"] < 85.0))

    # Logic
    short_entry_logic.append(df["WILLR_14"] > -50.0)
    short_entry_logic.append(df["AROONU_14"] > 75.0)
    short_entry_logic.append(df["AROOND_14"] < 25.0)
    short_entry_logic.append(df["STOCHRSIk_14_14_3_3"] > 80.0)
    short_entry_logic.append(df["WILLR_84_1h"] > -30.0)
    short_entry_logic.append(df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
    short_entry_logic.append(df["BBB_20_2.0_1h"] > 20.0)
    short_entry_logic.append(df["close_min_48"] <= (df["close"] * 0.90))
