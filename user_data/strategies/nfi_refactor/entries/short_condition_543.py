"""Short entry condition #543 extracted from NFI."""

import numpy as np
import pandas as pd

def append_short_543(df, short_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI short condition #543, the rapid-mode short entry."""
    # Protections
    short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

    short_entry_logic.append(df["RSI_14_1h"] > 20.0)
    short_entry_logic.append(df["RSI_14_4h"] > 20.0)
    short_entry_logic.append(df["RSI_14_1d"] > 10.0)
    # 5m strong down move
    short_entry_logic.append((df["RSI_3"] < 98.0) | (df["ROC_9"] < 50.0))
    # 15m down move, 1h down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_change_pct_1h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m down move, 1h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_change_pct_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 5m down move, 1h down, 4h high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["CMF_20_1h"] < 0.2) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m down move, 1h still not low enough, 4h high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["AROOND_14_1h"] < 25.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 10.0)
    )
    # 15m down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["OBV_change_pct_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 5m & 1h strong down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
    )
    # 5m & 1h strong downtrend
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["MFI_14_1h"] < 90.0))
    # 15m & 1h down move, 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0)
      | (df["RSI_3_1h"] < 80.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
      | (df["AROOND_14_4h"] < 50.0)
    )
    # 15m & 1h down move, 4h still high, 4h downtrend
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 90.0) | (df["UO_7_14_28_4h"] > 60.0) | (df["ROC_9_4h"] < 20.0)
    )
    # 15m & 1h down move, 1d strong downtrend
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 90.0) | (df["ROC_9_1d"] < 50.0))
    # 15m & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 55.0)
    )
    # 15m down move, 15m still not low enough, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 15m & 1h down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_1h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 15m down move, 15m still not low enoug, 1h high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["AROOND_14_15m"] < 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 10.0)
    )
    # 15m down move, 1h downtrend, 4h overbought
    short_entry_logic.append((df["RSI_3_15m"] < 85.0) | (df["ROC_9_1h"] < 5.0) | (df["ROC_9_4h"] > -35.0))
    # 1h & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 75.0)
    )
    # 1h & 4h down move, 4h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_3_change_pct_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 1h & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_3_change_pct_4h"] < 65.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 1h down move, 1h still not low enough, 4h still not low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0) | (df["RSI_14_4h"] > 50.0)
    )
    # 1h down move, 1h not low enough, 1h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 85.0) | (df["AROOND_14_1h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 4h down move, 15m still not low enough, 1h still high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 4h down move, 4h still high, 1d downtrend
    short_entry_logic.append(
      (df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0) | (df["ROC_9_1d"] < 50.0)
    )
    # 4h & 1d down move, 1d strong downtrend
    short_entry_logic.append((df["RSI_3_4h"] < 90.0) | (df["RSI_3_1d"] < 90.0) | (df["ROC_9_1d"] < 60.0))
    # 4h overbought, 1h still high, 1d downtrend
    short_entry_logic.append(
      (df["ROC_9_4h"] > -50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0) | (df["ROC_9_1d"] < 50.0)
    )
    # 4h red, previous 4h green, 4h overbought
    short_entry_logic.append(
      (df["change_pct_4h"] < 5.0) | (df["change_pct_4h"].shift(48) > -5.0) | (df["RSI_14_4h"].shift(48) > 20.0)
    )
    # 4h red, 4h moving down, 4h still high, 1d downtrend
    short_entry_logic.append(
      (df["change_pct_4h"] < 10.0)
      | (df["CCI_20_change_pct_4h"] < 0.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
      | (df["ROC_9_1d"] < 40.0)
    )

    # Logic
    short_entry_logic.append(df["RSI_14"] > 60.0)
    short_entry_logic.append(df["MFI_14"] > 60.0)
    short_entry_logic.append(df["AROOND_14"] < 25.0)
    short_entry_logic.append(df["EMA_26"] < df["EMA_12"])
    short_entry_logic.append((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.024))
    short_entry_logic.append((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
    short_entry_logic.append(df["close"] < (df["EMA_20"] * 0.958))
    short_entry_logic.append(df["close"] < (df["BBL_20_2.0"] * 0.992))
