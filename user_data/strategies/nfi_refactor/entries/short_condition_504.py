"""Short entry condition #504 extracted from NFI."""

import numpy as np
import pandas as pd

def append_short_504(df, short_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI short condition #504, a normal-mode short entry."""
    # Protections
    short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

    short_entry_logic.append(df["RSI_3_1h"] >= 5.0)
    short_entry_logic.append(df["RSI_3_4h"] >= 20.0)
    short_entry_logic.append(df["RSI_3_1d"] >= 20.0)
    short_entry_logic.append(df["RSI_14_1h"] > 20.0)
    short_entry_logic.append(df["RSI_14_4h"] > 20.0)
    short_entry_logic.append(df["RSI_14_1d"] > 10.0)
    # 15m & 1h down move, 4h still high
    short_entry_logic.append(
        (df["RSI_3_15m"] < 95.0)
        | (df["MFI_14_15m"] < 90.0)
        | (df["RSI_3_1h"] < 80.0)
        | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m & 1h down move, 4h still high
    short_entry_logic.append(
        (df["RSI_3_15m"] < 90.0) | (df["MFI_14_15m"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 14m & 4h down move, 4h still high
    short_entry_logic.append(
        (df["RSI_3_15m"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 15m down move, 1h & 4h still high
    short_entry_logic.append(
        (df["RSI_3_15m"] < 90.0) | (df["UO_7_14_28_1h"] < 45.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 1h strong down move, 4h still high
    short_entry_logic.append(
        (df["RSI_3_1h"] < 95.0) | (df["RSI_14_change_pct_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 1h strong down move, 4h down move, 4h still high
    short_entry_logic.append(
        (df["RSI_3_1h"] < 95.0) | (df["RSI_3_change_pct_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 1h & 4h down move, 4h still not low enough
    short_entry_logic.append(
        (df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 75.0)
    )
    # 1h & 4h down move, 4h still not low enough
    short_entry_logic.append((df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 75.0) | (df["AROOND_14_4h"] < 50.0))
    # 15m down move, 1h strong downtrend
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["MFI_14_1h"] > 5.0))
    # 15m downtrend, 4h down move, 4h stil high
    short_entry_logic.append(
        (df["ROC_9_15m"] > -20.0) | (df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )

    # Logic
    short_entry_logic.append(df["AROOND_14"] < 25.0)
    short_entry_logic.append(df["AROOND_14_15m"] < 25.0)
    short_entry_logic.append(df["close"] > (df["EMA_9"] * 1.058))
    short_entry_logic.append(df["close"] > (df["EMA_20"] * 1.040))
