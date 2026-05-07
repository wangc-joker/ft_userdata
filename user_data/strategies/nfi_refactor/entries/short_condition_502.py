"""Short entry condition #502 extracted from NFI."""

import numpy as np
import pandas as pd

def append_short_502(df, short_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI short condition #502, the normal-mode short entry."""
    # Protections
    short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    short_entry_logic.append(df["protections_short_global"] == True)

    # 5m & 15m & 1h & 4h up move
    short_entry_logic.append(
      (df["RSI_3"] < 97.0) | (df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 80.0)
    )
    # 5m & 4h up move
    short_entry_logic.append((df["RSI_3"] < 97.0) | (df["RSI_3_4h"] < 95.0))
    # 5m up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3"] < 97.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0))
    # 5m & 15m strong up move
    short_entry_logic.append((df["RSI_3"] < 95.0) | (df["RSI_3_15m"] < 95.0))
    # 5m & 15m up move, 4h low
    short_entry_logic.append((df["RSI_3"] < 95.0) | (df["RSI_3_15m"] < 90.0) | (df["AROONU_14_4h"] > 30.0))
    # 5m & 1h & 4h up move
    short_entry_logic.append((df["RSI_3"] < 95.0) | (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 90.0))
    # 5m & 1h up move, 15m still not high enough
    short_entry_logic.append(
      (df["RSI_3"] < 95.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0)
    )
    # 5m up move, 15m still low
    short_entry_logic.append((df["RSI_3"] < 95.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0))
    # 5m up move, 4h low
    short_entry_logic.append((df["RSI_3"] < 90.0) | (df["AROONU_14_4h"] > 20.0))
    # 15m & 1h down move, 4h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 97.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 15m up move, 1h still low
    short_entry_logic.append((df["RSI_3_15m"] < 97.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0))
    # 15m & 1h & 4h up move
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 85.0))
    # 15m & 1h up move, 4h still low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 15m up move, 1h still low
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 40.0))
    # 15m up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["AROONU_14_4h"] > 70.0))
    # 15m & 1h & 4h up move
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 90.0))
    # 15m & 1h up move, 15m still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0)
    )
    # 15m & 1h up move, 1d low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 40.0)
    )
    # 15m & 1h up move, 1h still not high enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
    )
    # 15m & 1h up move, 4h stil low
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_1h"] < 80.0) | (df["AROONU_14_4h"] > 50.0))
    # 15m & 4h up move, 1d low
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["RSI_14_1d"] > 40.0))
    # 15m & 4h up move, 1d low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0)
    )
    # 15m up move, 1h still low, 1d low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["AROONU_14_1h"] > 50.0) | (df["AROONU_14_1d"] > 30.0)
    )
    # 15m up move, 1h high
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["AROONU_14_1h"] < 100.0))
    # 15m up move, 1h still low
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0))
    # 15m up move, 4h uptrend
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["ROC_9_4h"] < 20.0))
    # 15m & 1h up move, 1h still low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_1h"] < 65.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0)
    )
    # 15m up move, 1h low
    short_entry_logic.append((df["RSI_3_15m"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0))
    # 15m & 4h up move, 15m still low
    short_entry_logic.append((df["RSI_3_15m"] < 80.0) | (df["RSI_3_4h"] < 75.0) | (df["AROONU_14_15m"] > 50.0))
    # 15m up move, 1h low
    short_entry_logic.append((df["RSI_3_15m"] < 80.0) | (df["AROONU_14_1h"] > 10.0))
    # 15m up move, 1h low, 1d uptrend
    short_entry_logic.append((df["RSI_3_15m"] < 80.0) | (df["AROONU_14_1h"] > 40.0) | (df["ROC_9_1d"] < 100.0))
    # 15m up move, 4h low
    short_entry_logic.append((df["RSI_3_15m"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0))
    # 15m up move, 1h uptrend
    short_entry_logic.append((df["RSI_3_15m"] < 75.0) | (df["ROC_9_1h"] < 40.0))
    # 1h & 1d strong up move
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_3_1d"] < 95.0))
    # 1h up move, 1h still not high enough
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0))
    # 1h up move, 4h still low, 1h moving higher
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0) | (df["CCI_20_change_pct_1h"] < -0.0)
    )
    # 1h up move, 1d low
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_14_1d"] > 40.0))
    # 1h strong up move, 15m still move higher
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["CCI_20_change_pct_15m"] < -0.0))
    # 1h up move, relative stable before the hour
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["close_min_12"] > (df["close_min_48"] * 1.10)))
    # 1h up move, 15m uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["AROONU_14_15m"] < 100.0))
    # 1h up move, 1d low
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 10.0))
    # 1h up move, 1h & 4h uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["ROC_9_1h"] < 30.0) | (df["ROC_9_4h"] < 30.0))
    # 1h up move, 4h uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["ROC_9_4h"] < 20.0))
    # 1h up move, 4h still low
    short_entry_logic.append((df["RSI_3_1h"] < 85.0) | (df["AROONU_14_4h"] > 50.0))
    # 1h & 4h up move, 1d low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 80.0) | (df["RSI_3_4h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0)
    )
    # 1h up move, 1h still not high enough
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0))
    # 1h up move, 4h still low, 1h still moving higher
    short_entry_logic.append(
      (df["RSI_3_1h"] < 80.0) | (df["RSI_14_4h"] > 60.0) | (df["CCI_20_change_pct_1h"] < -0.0)
    )
    # 1h up move, 4h low
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0))
    # 1h up move, 4h low
    short_entry_logic.append((df["RSI_3_1h"] < 80.0) | (df["AROONU_14_4h"] > 10.0))
    # 1h up move, 1h still low
    short_entry_logic.append((df["RSI_3_1h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0))
    # 1h up move, 4h low
    short_entry_logic.append((df["RSI_3_1h"] < 70.0) | (df["RSI_14_4h"] > 40.0))
    # 1h up move, 4h low
    short_entry_logic.append((df["RSI_3_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0))
    # 1h up move, 1h uptrend
    short_entry_logic.append((df["RSI_3_1h"] < 70.0) | (df["ROC_9_1h"] < 40.0))
    # 1h up move, 1h low
    short_entry_logic.append((df["RSI_3_1h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0))
    # 4h up move, 1d still low
    short_entry_logic.append((df["RSI_3_4h"] < 97.0) | (df["RSI_14_1d"] > 50.0))
    # 4h up move, 1h still not high enough
    short_entry_logic.append((df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0))
    # 4h up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0))
    # 4h up move, 15m still not high enough, 4h moving higher
    short_entry_logic.append(
      (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0) | (df["CCI_20_change_pct_4h"] < 0.0)
    )
    # 4h up move, 15m still low
    short_entry_logic.append((df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0))
    # 4h up move, 1h still low
    short_entry_logic.append((df["RSI_3_4h"] < 90.0) | (df["AROONU_14_1h"] > 40.0))
    # 4h up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 75.0))
    # 4h up move, 4h still not high enough
    short_entry_logic.append((df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0))
    # 4h up move, 1d still low, 4h uptrend
    short_entry_logic.append((df["RSI_3_4h"] < 85.0) | (df["RSI_14_1d"] > 50.0) | (df["ROC_9_4h"] < 20.0))
    # 4h up move, 4h uptrend
    short_entry_logic.append((df["RSI_3_4h"] < 80.0) | (df["ROC_9_4h"] < 20.0))
    # 4h up move, 1h low
    short_entry_logic.append((df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0))
    # 4h up move, 4h low
    short_entry_logic.append((df["RSI_3_4h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0))
    # 1d up move, 1h still not high enough
    short_entry_logic.append((df["RSI_3_1d"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 90.0))
    # 1d up move, 1h still low
    short_entry_logic.append((df["RSI_3_1d"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0))
    # 1d up move, 4h still low
    short_entry_logic.append((df["RSI_3_1d"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0))
    # 15m low, 1h still low
    short_entry_logic.append((df["AROONU_14_15m"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0))
    # 15m low, 4h low
    short_entry_logic.append((df["AROONU_14_15m"] > 20.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0))
    # 15m still low, 1h low
    short_entry_logic.append((df["AROONU_14_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0))
    # 15m still not high enough, 4h low
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["AROONU_14_4h"] > 10.0))
    # 1h & 4h low
    short_entry_logic.append((df["AROONU_14_1h"] > 20.0) | (df["AROONU_14_4h"] > 20.0))
    # 1h & 4h low
    short_entry_logic.append((df["AROONU_14_1h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0))
    # 1h low, 1d low
    short_entry_logic.append((df["AROONU_14_1h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0))
    # 4h still not high enough, 4h & 1d uptrend
    short_entry_logic.append((df["AROONU_14_4h"] > 70.0) | (df["ROC_9_4h"] < 60.0) | (df["ROC_9_1d"] < 200.0))
    # 1h & 4h low
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_1h"] > 20.0) | (df["AROONU_14_4h"] > 20.0))
    # 1d big green, 1d still not high enough
    short_entry_logic.append((df["change_pct_1d"] < 30.0) | (df["RSI_14_1d"] > 65.0))
    # rise in the last hour, relatively stable before the hour
    short_entry_logic.append(
      (df["close"] < (df["close_min_12"] * 1.10)) | (df["close_min_12"] > (df["close_min_48"] * 1.10))
    )
    # big pump in the last 6 days, 4h still not high enough
    short_entry_logic.append((df["close"] < (df["low_min_6_1d"] * 4.0)) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0))
    # big pump in the last 20 days, 1h up move
    short_entry_logic.append((df["close"] < (df["low_min_20_1d"] * 6.0)) | (df["RSI_3_1h"] < 90.0))

    # Logic
    short_entry_logic.append(df["AROOND_14"] < 25.0)
    short_entry_logic.append(df["STOCHRSIk_14_14_3_3"] > 80.0)
    short_entry_logic.append(df["close"] > (df["EMA_20"] * 1.060))
    short_entry_logic.append(df["close"] > (df["BBU_20_2.0"] * 0.995))
    short_entry_logic.append(df["AROOND_14_15m"] < 25.0)
