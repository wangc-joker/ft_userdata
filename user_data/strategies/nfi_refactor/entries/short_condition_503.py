"""Short entry condition #503 extracted from NFI."""

import numpy as np
import pandas as pd

def append_short_503(df, short_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI short condition #503, the normal-mode short entry."""
    # Protections
    short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

    short_entry_logic.append(df["RSI_3_1h"] >= 5.0)
    short_entry_logic.append(df["RSI_3_4h"] >= 20.0)
    short_entry_logic.append(df["RSI_3_1d"] >= 20.0)
    short_entry_logic.append(df["RSI_14_1h"] > 20.0)
    short_entry_logic.append(df["RSI_14_4h"] > 20.0)
    short_entry_logic.append(df["RSI_14_1d"] > 10.0)
    # 5m strong down move
    short_entry_logic.append((df["RSI_3"] < 98.0) | (df["ROC_9"] < 50.0))
    # 5m down move, 4h still high
    short_entry_logic.append(
      (df["RSI_3"] < 90.0) | (df["MFI_14"] > 10.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 5m & 1h down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3"] < 90.0) | (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
    )
    # 5m down move, 4h downtrend, 1h still high
    short_entry_logic.append(
      (df["RSI_3"] < 95.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 5m & 4h strong down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 5m down move, 1h high, 1d overbought
    short_entry_logic.append((df["RSI_3"] < 90.0) | (df["ROC_9_1h"] < 15.0) | (df["ROC_9_1d"] > -40.0))
    # 5m down move, 1h & 4h high
    short_entry_logic.append(
      (df["RSI_3"] < 90.0) | (df["UO_7_14_28_1h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 5m down move, 1h high, 4h downtrend
    short_entry_logic.append(
      (df["RSI_3"] < 98.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 10.0) | (df["ROC_9_4h"] < 10.0)
    )
    # 5m & 1h down move, 4h down
    short_entry_logic.append((df["RSI_3"] < 90.0) | (df["RSI_3_1h"] < 85.0) | (df["CMF_20_4h"] > -0.2))
    # 5m down move, 1h high
    short_entry_logic.append((df["RSI_14_change_pct"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0))
    # 5m down move, 1h high
    short_entry_logic.append((df["RSI_14_change_pct"] < 40.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0))
    # 15m & 1h down move, 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m down move, 15m still not low enough, 1h & 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0)
      | (df["AROOND_14_15m"] < 25.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 75.0)
      | (df["MFI_14_4h"] > 50.0)
    )
    # 5m & 1h down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m & 4h down move, 1h still not low
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
    )
    # 15m & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_4h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 15m down move, 1h & 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["RSI_14_4h"] > 50.0)
    )
    # 15m & 1h & 4h down move
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_change_pct_1h"] > -60.0) | (df["RSI_3_change_pct_4h"] > -40.0)
    )
    # 15m down move, 1d downtrend, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["ROC_9_1d"] > -25.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 15m & 1d down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_1d"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 15m & 4h down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m down move, 15m still not low enough, 4h down move
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["AROOND_14_15m"] < 50.0) | (df["RSI_3_4h"] < 85.0))
    # 15m down move, 1h still high, 1d strong downtrend
    short_entry_logic.append((df["RSI_3_15m"] < 80.0) | (df["AROOND_14_1h"] < 25.0) | (df["MFI_14_1d"] < 90.0))
    # 15m down move, 1h still high, 1d downtrend
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0) | (df["ROC_9_1d"] < 50.0)
    )
    # 15m down move, 4h still high, 1d downtrend
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0) | (df["ROC_9_1d"] < 50.0)
    )
    # 15m & 4h down move, 1d downtrend
    short_entry_logic.append((df["RSI_3_15m"] < 85.0) | (df["RSI_3_4h"] < 85.0) | (df["ROC_9_1d"] > -70.0))
    # 15m down move, 15m not low enough, 1h overbought
    short_entry_logic.append(
      (df["RSI_14_change_pct_15m"] > -40.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 90.0) | (df["RSI_14_1h"] > 30.0)
    )
    # 15m strong down move, 1h still high
    short_entry_logic.append((df["ROC_9_15m"] < 15.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0))
    # 15m downtrend, 1h & 4h still high
    short_entry_logic.append(
      (df["ROC_9_15m"] < 10.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m & 1h & 4h down move
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["CCI_20_change_pct_4h"] < 0.0)
    )
    # 15m strong down move
    short_entry_logic.append((df["RSI_3_15m"] < 90.0) | (df["MFI_14_15m"] < 85.0) | (df["AROOND_14_15m"] < 25.0))
    # 14m down move, 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 80.0) | (df["AROOND_14_15m"] < 50.0) | (df["UO_7_14_28_4h"] > 50.0)
    )
    # 15m down move, 1h stil high, 1d overbought
    short_entry_logic.append((df["RSI_3_15m"] < 85.0) | (df["AROOND_14_1h"] < 25.0) | (df["ROC_9_1d"] > -80.0))
    # 15m down move, 1h high, 1d overbought
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0) | (df["ROC_9_1d"] > -50.0)
    )
    # 1h & 4h down move, 4h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_change_pct_4h"] < 65.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 1h & 4h down move, 4h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 10.0)
    )
    # 1h down move, 4h still not low enough, 1d overbought
    short_entry_logic.append((df["RSI_3_1h"] < 90.0) | (df["AROOND_14_4h"] < 25.0) | (df["ROC_9_1d"] > -120.0))
    # 1h down move, 1h still not low enough, 4h still not low
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0) | (df["RSI_14_4h"] > 50.0)
    )
    # 1h down move, 4h still high
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_14_4h"] > 60.0))
    # 1h down move, 4h still high, 1d downtrend
    short_entry_logic.append(
      (df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0) | (df["ROC_9_1d"] < 50.0)
    )
    # 1h down move, 4h still high, 1d downtrend
    short_entry_logic.append(
      (df["RSI_3_change_pct_1h"] > -65.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0) | (df["ROC_9_1d"] < 50.0)
    )
    # 4h & 1d down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 90.0) | (df["ROC_2_1d"] < 20.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m still high, 1h down move, 4h high
    short_entry_logic.append(
      (df["AROOND_14_15m"] < 50.0) | (df["RSI_3_change_pct_1h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 15m still high, 1h & 4h down move, 4h still high
    short_entry_logic.append(
      (df["AROOND_14_15m"] < 50.0)
      | (df["RSI_3_1h"] < 85.0)
      | (df["RSI_3_4h"] < 80.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 15m & 1h still high, 4h overbought
    short_entry_logic.append(
      (df["AROOND_14_15m"] < 50.0) | (df["AROOND_14_1h"] < 50.0) | (df["ROC_9_4h"] > -40.0)
    )
    # 15m still high, 1h down move, 1d downtrend
    short_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_15m"] > 30.0) | (df["RSI_3_4h"] < 90.0) | (df["ROC_9_1d"] < 50.0)
    )
    # 1h & 4h still high, 1d strong down move
    short_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["UO_7_14_28_4h"] > 55.0) | (df["RSI_3_1d"] < 90.0)
    )
    # 1h still high, 4h & 1d downtrend
    short_entry_logic.append((df["AROOND_14_1h"] < 25.0) | (df["ROC_9_4h"] < 20.0) | (df["ROC_9_1d"] < 50.0))
    # 4h moving down, 1d P&D
    short_entry_logic.append(
      (df["ROC_9_4h"] < 30.0) | (df["RSI_3_change_pct_1d"] < 50.0) | (df["ROC_9_1d"] > -50.0)
    )
    # 1d strong downtrend, 4h still high
    short_entry_logic.append(
      (df["ROC_2_1d"] < 20.0) | (df["ROC_9_1d"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 1d P&D, 1d overbought
    short_entry_logic.append(
      (df["ROC_2_1d"] < 10.0) | (df["ROC_9_1d"] > -50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 5.0)
    )
    # 1h red, previous 1h green, 1h overbought
    short_entry_logic.append(
      (df["change_pct_1h"] < 1.0) | (df["change_pct_1h"].shift(12) > -5.0) | (df["RSI_14_1h"].shift(12) < 80.0)
    )
    # 1h red, 1h stil high, 4h downtrend
    short_entry_logic.append(
      (df["change_pct_1h"] < 5.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["ROC_9_4h"] > -25.0)
    )
    # 4h red, 15m down move, 4h still high
    short_entry_logic.append(
      (df["change_pct_4h"] < 5.0) | (df["RSI_3_15m"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 4h red, previous 4h green, 4h overbought
    short_entry_logic.append(
      (df["change_pct_4h"] < 5.0) | (df["change_pct_4h"].shift(48) > -5.0) | (df["ROC_9_4h"].shift(48) > -25.0)
    )
    # 4h red, 4h still not low enough, 1h downtrend, 1h overbought
    short_entry_logic.append(
      (df["change_pct_4h"] < 10.0)
      | (df["AROOND_14_4h"] < 25.0)
      | (df["ROC_9_1h"] < 20.0)
      | (df["ROC_9_1d"] > -40.0)
    )
    # 4h red, 4h still high, 1d downtrend
    short_entry_logic.append(
      (df["change_pct_4h"] < 10.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0) | (df["ROC_9_1d"] < 40.0)
    )
    # 1d P&D, 1d overbought
    short_entry_logic.append(
      (df["change_pct_1d"] < 10.0) | (df["change_pct_1d"].shift(288) > -10.0) | (df["ROC_9_1d"] > -100.0)
    )
    # 1d P&D, 4h still high
    short_entry_logic.append(
      (df["change_pct_1d"] < 15.0) | (df["change_pct_1d"].shift(288) > -15.0) | (df["AROOND_14_4h"] < 50.0)
    )
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 95.0) | (df["CCI_20_change_pct_4h"] < 0.0)
    )

    # Logic
    short_entry_logic.append(df["RSI_20"] > df["RSI_20"].shift(1))
    short_entry_logic.append(df["RSI_4"] > 54.0)
    short_entry_logic.append(df["AROOND_14"] < 25.0)
    short_entry_logic.append(df["close"] > df["SMA_16"] * 1.058)
