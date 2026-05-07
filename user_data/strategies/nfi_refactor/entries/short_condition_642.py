"""Short entry condition #642 extracted from NFI."""

import numpy as np
import pandas as pd

def append_short_642(df, short_entry_logic, allowed_empty_candles_288, is_pair_short_top_coins_mode) -> None:
    """Append NFI short condition #642, the top-coins-mode short entry."""
    # Protections
    short_entry_logic.append(is_pair_short_top_coins_mode)

    short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

    # 5m & 1h & 4h down move
    short_entry_logic.append((df["RSI_3"] < 90.0) | (df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 90.0))
    # 5m down move, 15m & 4h still high
    short_entry_logic.append(
      (df["RSI_3"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 5m down move, 15m still high, 1h high
    short_entry_logic.append(
      (df["RSI_3"] < 85.0) | (df["AROOND_14_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0)
    )
    # 15m & 1h down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 90.0)
    )
    # 15m & 1h down move, 1d still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 70.0)
    )
    # 15m strong down move, 4h high
    short_entry_logic.append((df["RSI_3_15m"] < 95.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0))
    # 15m & 1h down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
    )
    # 15m down move, 15m stil high, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
    )
    # 15m down move, 1h & 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 15m & 1h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 95.0) | (df["RSI_3_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m down move, 15m still not low enough, 4h high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0)
    )
    # 15m down move, 4h still high, 1d high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0)
    )
    # 15m & 4h down move, 1d still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 85.0) | (df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 50.0)
    )
    # 15m & 1h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 80.0) | (df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 15m & 1h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 75.0) | (df["RSI_3_1h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 15m & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 75.0) | (df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 15m down move, 1h still high, 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 75.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 15m down move, 1h still not low enough, 4h high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 75.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 15m down move, 1h high, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 75.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 90.0)
    )
    # 15m down move, 4h high, 1d stil high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 75.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 50.0)
    )
    # 15m & 4h down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_15m"] < 70.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
    )
    # 15m & 4h down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 70.0) | (df["RSI_3_4h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m down move, 15m still high 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m down move, 1h still high, 4h high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 10.0)
    )
    # 1h & 4h down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 95.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 90.0)
    )
    # 1h & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 95.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 1h & 4h down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 90.0)
    )
    # 1h & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 80.0)
    )
    # 1h & 4h down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 85.0)
    )
    # 1h & 4h down move, 1d still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 90.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 50.0)
    )
    # 1h & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 85.0) | (df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 85.0)
    )
    # 1h down move, 4h still high, 1d high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0)
    )
    # 1h & 4h down move, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 80.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 75.0)
    )
    # 1h & 4h down move, 15m still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 80.0) | (df["RSI_3_4h"] < 80.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0)
    )
    # 1h & 4h down move, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_1h"] < 75.0) | (df["RSI_3_4h"] < 90.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 75.0)
    )
    # 1h & 4h down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 70.0) | (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0)
    )
    # 1h down move, 1h still not low enough, 4h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 4h down move, 15m still high, 1h still not low enough
    short_entry_logic.append(
      (df["RSI_3_4h"] < 85.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 80.0)
    )
    # 4h down move, 15m still high, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 75.0)
    )
    # 4h down move, 1h still not low enough, 1d still high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 50.0)
    )
    # 15m & 1h still high, 4h high
    short_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_15m"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 10.0)
    )
    # 15m still high, 1h & 1d high
    short_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_15m"] > 60.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
      | (df["STOCHRSIk_14_14_3_3_1d"] > 30.0)
    )
    # 15m & 4h high
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0))
    # 15m high, 1h & 4h still not low enough
    short_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_15m"] > 30.0)
      | (df["STOCHRSIk_14_14_3_3_1h"] > 75.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 75.0)
    )
    # 15m & 4h high
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0))
    # 1h & 4h still high, 1d high
    short_entry_logic.append(
      (df["STOCHRSIk_14_14_3_3_1h"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
      | (df["STOCHRSIk_14_14_3_3_1d"] > 50.0)
    )
    # 1h & 4h high
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_1h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 10.0))
    # 1h & 4h high
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_1h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0))
    # 4h & 1d high
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_4h"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 20.0))
    # 1d red, 1d high
    short_entry_logic.append((df["change_pct_1d"] < 5.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 20.0))
    # 1d P&D, 1d high
    short_entry_logic.append(
      (df["change_pct_1d"] < 10.0)
      | (df["change_pct_1d"].shift(288) > -10.0)
      | (df["STOCHRSIk_14_14_3_3_1d"] > 50.0)
    )

    # Logic
    short_entry_logic.append(df["RSI_4"] > 54.0)
    short_entry_logic.append(df["RSI_20"] > df["RSI_20"].shift(1))
    short_entry_logic.append(df["close"] > df["SMA_16"] * 1.042)
