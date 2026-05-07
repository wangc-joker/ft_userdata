"""NFI long entry condition #161."""

import numpy as np

def append_long_161(df, long_entry_logic, allowed_empty_candles_288) -> None:
    """Append NFI long condition #161, the scalp-mode long entry."""
    # Protections
    long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
    long_entry_logic.append(df["protections_long_global"] == True)

    # 5m down move, 15m high
    long_entry_logic.append((df["RSI_3"] > 15.0) | (df["AROONU_14_15m"] < 80.0))
    # 15m & 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_15m"] > 25.0) | (df["RSI_3_1h"] > 35.0) | (df["AROONU_14_4h"] < 70.0))
    # 15m & 4h down move, 4h still high
    long_entry_logic.append((df["RSI_3_15m"] > 25.0) | (df["RSI_3_4h"] > 50.0) | (df["AROONU_14_4h"] < 50.0))
    # 15m down move, 15m high
    long_entry_logic.append((df["RSI_3_15m"] > 25.0) | (df["AROONU_14_15m"] < 80.0))
    # 15m down move, 4h still high, 1d high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 25.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0) | (df["AROONU_14_1d"] < 90.0)
    )
    # 15m & 1h down move, 15m still high
    long_entry_logic.append((df["RSI_3_15m"] > 30.0) | (df["RSI_3_1h"] > 60.0) | (df["AROONU_14_15m"] < 50.0))
    # 15m down move, 15m & 4h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 30.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # 15m & 4h down move, 4h high
    long_entry_logic.append((df["RSI_3_15m"] > 35.0) | (df["RSI_3_4h"] > 60.0) | (df["AROONU_14_4h"] < 80.0))
    # 15m & 1h down move, 1h high
    long_entry_logic.append((df["RSI_3_15m"] > 40.0) | (df["RSI_3_1h"] > 40.0) | (df["AROONU_14_1h"] < 70.0))
    # 15m & 1h down move, 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 40.0) | (df["RSI_3_1h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 15m & 1h down move, 4h high
    long_entry_logic.append((df["RSI_3_15m"] > 40.0) | (df["RSI_3_1h"] > 60.0) | (df["AROONU_14_4h"] < 80.0))
    # 15m & 4h down move, 15m high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 40.0) | (df["RSI_3_4h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0)
    )
    # 15m & 4h down move, 15m high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 40.0) | (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 70.0)
    )
    # 15m down move, 15m & 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 40.0) | (df["AROONU_14_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 15m down move, 15m & 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 15m down move, 4h still high, 1d overbought
    long_entry_logic.append((df["RSI_3_15m"] > 40.0) | (df["AROONU_14_4h"] < 50.0) | (df["ROC_9_1d"] < 100.0))
    # 15m & 1h down move, 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 45.0) | (df["RSI_3_1h"] > 45.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
    )
    # 15m down move, 15m high, 1d overbought
    long_entry_logic.append((df["RSI_3_15m"] > 45.0) | (df["AROONU_14_15m"] < 60.0) | (df["ROC_9_1d"] < 50.0))
    # 15m down move, 15m high, 4h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 45.0) | (df["AROONU_14_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # 15m down move, 15m still not low enough, 4h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 45.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # 15m down move, 15m & 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 45.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 45.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
    )
    # 15m down move, 15m still not low enough, 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 30.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0)
    )
    # 15m down move, 15m still high, 1d overbought
    long_entry_logic.append((df["RSI_3_15m"] > 50.0) | (df["AROONU_14_15m"] < 50.0) | (df["ROC_9_1d"] < 50.0))
    # 15m down move, 15m still high, 1h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 55.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0)
    )
    # 15m down move, 15m still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 55.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["AROONU_14_4h"] < 85.0)
    )
    # 15m down move, 15m & 1h still high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 55.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 1h down move, 4h still high, 1d high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 25.0) | (df["AROONU_14_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0)
    )
    # 1h & 4h down move, 1h still high
    long_entry_logic.append((df["RSI_3_1h"] > 30.0) | (df["RSI_3_4h"] > 65.0) | (df["AROONU_14_1h"] < 50.0))
    long_entry_logic.append(
      (df["RSI_3_1h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0)
    )
    # 1h & 4h down move, 4h still high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 35.0) | (df["RSI_3_4h"] > 55.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # 1h & 4h down move, 4h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 35.0) | (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0)
    )
    # 1h down move, 15m & 1h still high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 1h down move, 1h still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0)
    )
    # 1h down move, 1h high
    long_entry_logic.append((df["RSI_3_1h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 60.0))
    # 1h down move, 4h & 1d high
    long_entry_logic.append((df["RSI_3_1h"] > 40.0) | (df["AROONU_14_4h"] < 85.0) | (df["AROONU_14_1d"] < 90.0))
    # 1h down move, 1h still high, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_1h"] < 50.0) | (df["AROONU_14_4h"] < 90.0))
    # 1h down move, 1h still high, 1d high
    long_entry_logic.append((df["RSI_3_1h"] > 45.0) | (df["AROONU_14_1h"] < 50.0) | (df["AROONU_14_1d"] < 90.0))
    # 1h down move, 1h high
    long_entry_logic.append((df["RSI_3_1h"] > 45.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 60.0))
    # 1h & 4h down move, 15m high
    long_entry_logic.append((df["RSI_3_1h"] > 50.0) | (df["RSI_3_4h"] > 60.0) | (df["AROONU_14_15m"] < 70.0))
    # 1h down move, 15m still high, 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 50.0) | (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_4h"] < 80.0))
    # 1h down move, 15m high, 1h still high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 50.0) | (df["AROONU_14_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0)
    )
    # 1h down move, 15m still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 80.0)
    )
    # 1h down move, 15m & 1h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 60.0) | (df["AROONU_14_1h"] < 60.0)
    )
    # 1h down move, 1h & 1d high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 50.0) | (df["AROONU_14_1h"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0)
    )
    # 1h down move, 4h still high, 1d high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 90.0)
    )
    # 1h down move, 1h still high, 1d high
    long_entry_logic.append((df["RSI_3_1h"] > 50.0) | (df["AROONU_14_1h"] < 50.0) | (df["AROONU_14_1d"] < 90.0))
    # 1h down move, 4h overbought
    long_entry_logic.append((df["RSI_3_1h"] > 50.0) | (df["ROC_9_4h"] < 40.0))
    # 1h down move, 1h & 4h high
    long_entry_logic.append((df["RSI_3_1h"] > 55.0) | (df["AROONU_14_1h"] < 70.0) | (df["AROONU_14_4h"] < 100.0))
    # 1h down move, 5m up move, 1h still high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["RSI_3"] < 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0)
    )
    # 1h down move, 15m still not low enough, 4h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["AROONU_14_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0)
    )
    # 1h down move, 15m still not low enough, 1h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 30.0) | (df["AROONU_14_1h"] < 70.0)
    )
    # 1h down move, 15m still not low enough, 1h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 30.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 60.0)
    )
    # 1h down move, 15m & 4h still high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0)
    )
    # 1h down move, 15m & 1h high
    long_entry_logic.append((df["RSI_3_1h"] > 60.0) | (df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_1h"] < 90.0))
    # 1h down move, 1h still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["AROONU_14_1h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 90.0)
    )
    # 1h down move, 1h high, 4h still high
    long_entry_logic.append((df["RSI_3_1h"] > 60.0) | (df["AROONU_14_1h"] < 80.0) | (df["AROONU_14_4h"] < 40.0))
    # 1h down move, 1h still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0) | (df["AROONU_14_4h"] < 70.0)
    )
    # 1h down move, 1h & 1d high
    long_entry_logic.append(
      (df["RSI_3_1h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["AROONU_14_1d"] < 90.0)
    )
    # 1h down move, 4h & 1d high
    long_entry_logic.append((df["RSI_3_1h"] > 60.0) | (df["RSI_14_4h"] < 70.0) | (df["RSI_14_1d"] < 80.0))
    # 15m & 1h & 4h down move, 4h high
    long_entry_logic.append(
      (df["RSI_3_15m"] > 50.0) | (df["RSI_3_1h"] > 65.0) | (df["RSI_3_4h"] > 65.0) | (df["AROONU_14_4h"] < 85.0)
    )
    # 4h down move, 15m high
    long_entry_logic.append((df["RSI_3_4h"] > 20.0) | (df["AROONU_14_15m"] < 80.0))
    # 4h down move, 1h high
    long_entry_logic.append((df["RSI_3_4h"] > 25.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0))
    # 4h down move, 15m & 4h still high
    long_entry_logic.append((df["RSI_3_4h"] > 30.0) | (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_4h"] < 50.0))
    # 4h down move, 15m still high, 1d overbought
    long_entry_logic.append(
      (df["RSI_3_4h"] > 30.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["ROC_9_1d"] < 10.0)
    )
    # 4h down move, 1h & 4h still high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0) | (df["AROONU_14_4h"] < 50.0)
    )
    # 4h down move, 1d high & overbought
    long_entry_logic.append(
      (df["RSI_3_4h"] > 35.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0) | (df["ROC_9_1d"] < 40.0)
    )
    # 4h down move, 15m & 1h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 40.0) | (df["AROONU_14_15m"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0)
    )
    # 4h down move, 1d high & overbought
    long_entry_logic.append((df["RSI_3_4h"] > 40.0) | (df["AROONU_14_1d"] < 80.0) | (df["ROC_9_1d"] < 20.0))
    # 4h down move, 15m still high, 1h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 80.0)
    )
    # 4h down move, 1h & 4h still high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0) | (df["RSI_14_4h"] < 50.0)
    )
    # 4h down move, 1h still high, 4h still moving down
    long_entry_logic.append(
      (df["RSI_3_4h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0) | (df["CCI_20_change_pct_4h"] > -0.0)
    )
    # 4h down move, 1d high & overbought
    long_entry_logic.append(
      (df["RSI_3_4h"] > 40.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0) | (df["ROC_9_1d"] < 10.0)
    )
    # 4h down move, 1h high, 4h still high
    long_entry_logic.append((df["RSI_3_4h"] > 45.0) | (df["AROONU_14_1h"] < 70.0) | (df["AROONU_14_4h"] < 50.0))
    # 4h down move, 15m high, 4h still high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 50.0) | (df["AROONU_14_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 40.0)
    )
    # 4h down move, 15m still high, 1h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 40.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0)
    )
    # 4h down move, 15m & 4h still high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["AROONU_14_4h"] < 50.0)
    )
    # 4h down move, 15m high, 4h still not low enough
    long_entry_logic.append(
      (df["RSI_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 30.0)
    )
    # 4h down move, 1h still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 50.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 50.0) | (df["AROONU_14_4h"] < 70.0)
    )
    # 4h down move, 15m & 1d high
    long_entry_logic.append((df["RSI_3_4h"] > 50.0) | (df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_1d"] < 90.0))
    # 4h down move, 1d high & overbought
    long_entry_logic.append((df["RSI_3_4h"] > 50.0) | (df["AROONU_14_1d"] < 90.0) | (df["ROC_9_1d"] < 20.0))
    # 4h down move, 15m & 4h high
    long_entry_logic.append((df["RSI_3_4h"] > 60.0) | (df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_4h"] < 70.0))
    # 4h down move, 15m high, 4h still high
    long_entry_logic.append((df["RSI_3_4h"] > 60.0) | (df["AROONU_14_15m"] < 80.0) | (df["AROONU_14_4h"] < 40.0))
    # 4h down move, 15m still high, 1h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["AROONU_14_1h"] < 70.0)
    )
    # 4h down move, 15m still high, 4h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 50.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 70.0)
    )
    # 4h down move, 15m & 4h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 60.0)
    )
    # 4h down move, 1h & 4h high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 70.0) | (df["AROONU_14_4h"] < 70.0)
    )
    # 4h down move, 4h still high, 1d high
    long_entry_logic.append(
      (df["RSI_3_4h"] > 60.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0) | (df["STOCHRSIk_14_14_3_3_1d"] < 80.0)
    )
    # 15m still high, 1d high & overbought
    long_entry_logic.append(
      (df["AROONU_14_15m"] < 50.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] < 100.0)
    )
    # 15m high, 4h high
    long_entry_logic.append((df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_4h"] < 85.0))
    # 15m & 1d high, 1d overbought
    long_entry_logic.append((df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_1d"] < 90.0) | (df["ROC_9_1d"] < 20.0))
    # 15m & 1d high, 4h overbought
    long_entry_logic.append(
      (df["AROONU_14_15m"] < 70.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_4h"] < 10.0)
    )
    # 15m high, 4h still high
    long_entry_logic.append((df["AROONU_14_15m"] < 80.0) | (df["STOCHRSIk_14_14_3_3_4h"] < 50.0))
    # 4h & 1d high, 1d overbought
    long_entry_logic.append(
      (df["AROONU_14_4h"] < 100.0) | (df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] < 20.0)
    )
    # 4h high, 4h overbought
    long_entry_logic.append((df["AROONU_14_4h"] < 70.0) | (df["ROC_9_4h"] < 40.0))
    # 4h high, 1d overbought
    long_entry_logic.append((df["AROONU_14_4h"] < 70.0) | (df["ROC_9_1d"] < 40.0))
    # 1d high, 4h overbought
    long_entry_logic.append((df["AROONU_14_1d"] < 90.0) | (df["ROC_9_4h"] < 40.0))
    # 1d high & overbought
    long_entry_logic.append((df["AROONU_14_1d"] < 100.0) | (df["ROC_9_1d"] < 200.0))
    # 15m high, 1h still high
    long_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] < 70.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 40.0))
    # 15m & 4h high
    long_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] < 70.0) | (df["AROONU_14_4h"] < 70.0))
    # 15m high, 1d overbought
    long_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] < 70.0) | (df["ROC_9_1d"] < 10.0))
    # 15m high, 1h still not low enough
    long_entry_logic.append((df["STOCHRSIk_14_14_3_3_15m"] < 80.0) | (df["STOCHRSIk_14_14_3_3_1h"] < 30.0))
    # 1d high, 4h overbought
    long_entry_logic.append((df["STOCHRSIk_14_14_3_3_1d"] < 80.0) | (df["ROC_9_4h"] < 40.0))
    # 1d high & overbought
    long_entry_logic.append((df["STOCHRSIk_14_14_3_3_1d"] < 90.0) | (df["ROC_9_1d"] < 30.0))
    # 4h & 1d overbought
    long_entry_logic.append((df["ROC_9_4h"] < 40.0) | (df["ROC_9_1d"] < 40.0))
    # 1d green with top wick, 1d overbought
    long_entry_logic.append(
      (df["change_pct_1d"] < 25.0) | (df["top_wick_pct_1d"] < 25.0) | (df["ROC_9_1d"] < 50.0)
    )

    # Logic
    long_entry_logic.append(df["RSI_14"] < 50.0)
    long_entry_logic.append(df["AROONU_14_15m"] < 90.0)
    long_entry_logic.append(df["STOCHRSIk_14_14_3_3_15m"] < 90.0)
    long_entry_logic.append(
      (df["SMA_21"].shift(1) < df["SMA_200"].shift(1).infer_objects(copy=False).fillna(value=np.nan))
      & df["SMA_200"].shift(1).notna()
    )
    long_entry_logic.append(
      (df["SMA_21"] > df["SMA_200"].infer_objects(copy=False).fillna(value=np.nan)) & df["SMA_200"].notna()
    )
    long_entry_logic.append(
      (df["close"] > df["EMA_200_1h"].infer_objects(copy=False).fillna(value=np.nan)) & df["EMA_200_1h"].notna()
    )
    long_entry_logic.append(
      (df["close"] > df["EMA_200_4h"].infer_objects(copy=False).fillna(value=np.nan)) & df["EMA_200_4h"].notna()
    )
    long_entry_logic.append(df["BBB_20_2.0"] > 1.5)
    long_entry_logic.append(df["BBB_20_2.0_1h"] > 6.0)

