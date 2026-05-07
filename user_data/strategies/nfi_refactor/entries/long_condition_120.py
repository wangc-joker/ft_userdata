"""NFI long entry condition #120."""

def append_long_120(
    strategy,
    df,
    long_entry_logic,
    num_open_long_grind_mode,
    is_pair_long_grind_mode,
) -> None:
    """Append NFI long condition #120, the grind-mode long entry."""
    # Protections
    long_entry_logic.append(num_open_long_grind_mode < strategy.grind_mode_max_slots)
    long_entry_logic.append(df["protections_long_global"] == True)
    long_entry_logic.append(is_pair_long_grind_mode)
    long_entry_logic.append(df["RSI_3"] <= 50.0)
    long_entry_logic.append(df["RSI_3_15m"] >= 20.0)
    long_entry_logic.append(df["RSI_3_1h"] >= 10.0)
    long_entry_logic.append(df["RSI_3_4h"] >= 10.0)
    long_entry_logic.append(df["RSI_14_1h"] < 80.0)
    long_entry_logic.append(df["RSI_14_4h"] < 80.0)
    long_entry_logic.append(df["RSI_14_1d"] < 80.0)
    long_entry_logic.append(df["AROONU_14_1d"] < 100.0)
    long_entry_logic.append(df["STOCHRSIk_14_14_3_3_1d"] < 90.0)

    # Logic
    long_entry_logic.append(
        (df["STOCHRSIk_14_14_3_3"] < 20.0)
        & (df["WILLR_14"] < -80.0)
        & (df["AROONU_14"] < 25.0)
        & (df["close"] < (df["EMA_20"] * 0.978))
    )

