"""Short entry condition #661 extracted from NFI."""

import numpy as np
import pandas as pd

def append_short_661(df, short_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI short condition #661, the scalp-mode short entry."""
    # Protections
    short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

    # 15m down move, 15m high
    short_entry_logic.append((df["RSI_3_15m"] < 75.0) | (df["AROOND_14_15m"] < 80.0))
    # 15m & 1h down move, 15m still high
    short_entry_logic.append((df["RSI_3_15m"] < 70.0) | (df["RSI_3_1h"] < 40.0) | (df["AROOND_14_15m"] < 50.0))
    # 15m down move, 15m & 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m & 1h down move, 1h high
    short_entry_logic.append((df["RSI_3_15m"] < 60.0) | (df["RSI_3_1h"] < 60.0) | (df["AROOND_14_1h"] < 70.0))
    # 15m & 1h down move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 60.0) | (df["RSI_3_1h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m & 1h down move, 4h high
    short_entry_logic.append((df["RSI_3_15m"] < 60.0) | (df["RSI_3_1h"] < 40.0) | (df["AROOND_14_4h"] < 80.0))
    # 15m & 4h down move, 15m high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 60.0) | (df["RSI_3_4h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0)
    )
    # 15m & 4h down move, 15m high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 60.0) | (df["RSI_3_4h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 30.0)
    )
    # 15m down move, 15m & 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 60.0) | (df["AROOND_14_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m down move, 15m & 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 15m down move, 4h still high, 1d overbought
    short_entry_logic.append((df["RSI_3_15m"] < 60.0) | (df["AROOND_14_4h"] < 50.0) | (df["ROC_9_1d"] > -100.0))
    # 15m down move, 15m high, 4h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 55.0) | (df["AROOND_14_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 15m down move, 15m & 1h still high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 55.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 55.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0)
    )
    # 15m down move, 15m still not low enough, 4h high
    short_entry_logic.append(
      (df["RSI_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 10.0)
    )
    # 1h down move, 4h still high, 1d high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 75.0) | (df["AROOND_14_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 10.0)
    )
    short_entry_logic.append(
      (df["RSI_3_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 10.0)
    )
    # 1h & 4h down move, 4h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 65.0) | (df["RSI_3_4h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0)
    )
    # 1h down move, 15m & 1h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 1h down move, 1h still high, 4h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 1h down move, 1h high
    short_entry_logic.append((df["RSI_3_1h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 40.0))
    # 1h down move, 4h & 1d high
    short_entry_logic.append((df["RSI_3_1h"] < 60.0) | (df["AROOND_14_4h"] < 85.0) | (df["AROOND_14_1d"] < 90.0))
    # 1h down move, 1h still high, 4h high
    short_entry_logic.append((df["RSI_3_1h"] < 55.0) | (df["AROOND_14_1h"] < 50.0) | (df["AROOND_14_4h"] < 90.0))
    # 1h down move, 1h high
    short_entry_logic.append((df["RSI_3_1h"] < 55.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 40.0))
    # 1h & 4h down move, 15m high
    short_entry_logic.append((df["RSI_3_1h"] < 50.0) | (df["RSI_3_4h"] < 40.0) | (df["AROOND_14_15m"] < 70.0))
    # 1h down move, 15m still high, 4h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 50.0) | (df["AROOND_14_15m"] < 50.0) | (df["AROOND_14_4h"] < 80.0)
    )
    # 1h down move, 15m high, 1h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 50.0) | (df["AROOND_14_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0)
    )
    # 1h down move, 15m still high, 4h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 20.0)
    )
    # 1h down move, 15m & 1h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 40.0) | (df["AROOND_14_1h"] < 60.0)
    )
    # 1h down move, 1h & 1d high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 50.0) | (df["AROOND_14_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 20.0)
    )
    # 1h down move, 4h still high, 1d high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 10.0)
    )
    # 1h down move, 5m up move, 1h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 40.0) | (df["RSI_3"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0)
    )
    # 1h down move, 15m still not low enough, 1h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["AROOND_14_1h"] < 70.0)
    )
    # 1h down move, 15m still not low enough, 1h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 40.0)
    )
    # 1h down move, 15m & 4h still high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0)
    )
    # 1h down move, 15m & 1h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 40.0) | (df["AROOND_14_15m"] < 70.0) | (df["AROOND_14_1h"] < 90.0)
    )
    # 1h down move, 1h still high, 4h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 40.0) | (df["AROOND_14_1h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 10.0)
    )
    # 1h down move, 1h high, 4h still high
    short_entry_logic.append((df["RSI_3_1h"] < 40.0) | (df["AROOND_14_1h"] < 80.0) | (df["AROOND_14_4h"] < 40.0))
    # 1h down move, 1h still high, 4h high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0) | (df["AROOND_14_4h"] < 70.0)
    )
    # 1h down move, 1h & 1d high
    short_entry_logic.append(
      (df["RSI_3_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0) | (df["AROOND_14_1d"] < 90.0)
    )
    # 1h down move, 4h & 1d high
    short_entry_logic.append((df["RSI_3_1h"] < 40.0) | (df["RSI_14_4h"] > 30.0) | (df["RSI_14_1d"] > 20.0))
    # 4h down move, 15m high
    short_entry_logic.append((df["RSI_3_4h"] < 80.0) | (df["AROOND_14_15m"] < 80.0))
    # 4h down move, 1h high
    short_entry_logic.append((df["RSI_3_4h"] < 75.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0))
    # 4h down move, 1h & 4h still high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 65.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["AROOND_14_4h"] < 50.0)
    )
    # 4h down move, 15m & 1h high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 60.0) | (df["AROOND_14_15m"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 4h down move, 15m still high, 1h high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 20.0)
    )
    # 4h down move, 1h still high, 4h still moving down
    short_entry_logic.append(
      (df["RSI_3_4h"] < 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["CCI_20_change_pct_4h"] < 0.0)
    )
    # 4h down move, 1h high, 4h still high
    short_entry_logic.append((df["RSI_3_4h"] < 55.0) | (df["AROOND_14_1h"] < 70.0) | (df["AROOND_14_4h"] < 50.0))
    # 4h down move, 15m high, 4h still high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 50.0) | (df["AROOND_14_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 60.0)
    )
    # 4h down move, 15m still high, 1h high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0)
    )
    # 4h down move, 15m & 4h still high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["AROOND_14_4h"] < 50.0)
    )
    # 4h down move, 15m high, 4h still not low enough
    short_entry_logic.append(
      (df["RSI_3_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 70.0)
    )
    # 4h down move, 1h still high, 4h high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 50.0) | (df["AROOND_14_4h"] < 70.0)
    )
    # 4h down move, 15m & 4h high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 40.0) | (df["AROOND_14_15m"] < 70.0) | (df["AROOND_14_4h"] < 70.0)
    )
    # 4h down move, 15m high, 4h still high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 40.0) | (df["AROOND_14_15m"] < 80.0) | (df["AROOND_14_4h"] < 40.0)
    )
    # 4h down move, 15m still high, 4h high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 30.0)
    )
    # 4h down move, 15m & 4h high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 40.0)
    )
    # 4h down move, 1h & 4h high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 30.0) | (df["AROOND_14_4h"] < 70.0)
    )
    # 4h down move, 4h still high, 1d high
    short_entry_logic.append(
      (df["RSI_3_4h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1d"] > 20.0)
    )
    # 15m high, 4h high
    short_entry_logic.append((df["AROOND_14_15m"] < 70.0) | (df["AROOND_14_4h"] < 85.0))
    # 15m high, 4h still high
    short_entry_logic.append((df["AROOND_14_15m"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] > 50.0))
    # 15m high, 1h still high
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 60.0))
    # 15m & 4h high
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] > 30.0) | (df["AROOND_14_4h"] < 70.0))
    # 15m high, 1h still not low enough
    short_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] > 20.0) | (df["STOCHRSIk_14_14_3_3_1h"] > 70.0))

    # Logic
    short_entry_logic.append(df["RSI_14"] > 50.0)
    short_entry_logic.append(df["AROOND_14_15m"] < 90.0)
    short_entry_logic.append(df["STOCHRSIk_14_14_3_3_15m"] > 10.0)
    if isinstance(df["SMA_200"].iloc[-1], np.float64):
      short_entry_logic.append(df["SMA_21"].shift(1) > df["SMA_200"].shift(1))
      short_entry_logic.append(df["SMA_21"] < df["SMA_200"])
    else:
      short_entry_logic.append(pd.Series([False]))
    if isinstance(df["EMA_200_1h"].iloc[-1], np.float64):
      short_entry_logic.append(df["close"] < df["EMA_200_1h"])
    else:
      short_entry_logic.append(pd.Series([False]))
    if isinstance(df["EMA_200_4h"].iloc[-1], np.float64):
      short_entry_logic.append(df["close"] < df["EMA_200_4h"])
    else:
      short_entry_logic.append(pd.Series([False]))
    short_entry_logic.append(df["BBB_20_2.0_1h"] > 4.0)
