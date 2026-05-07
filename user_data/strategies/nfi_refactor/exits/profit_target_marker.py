from __future__ import annotations

"""Profit target marker helper extracted from NFI."""

def mark_profit_target(
    strategy,
    mode_name: str,
    pair: str,
    sell: bool,
    signal_name: str,
    trade,
    current_time,
    current_rate: float,
    current_profit: float,
    last_candle,
    previous_candle_1,
) -> tuple:
    if sell and (signal_name is not None):
        return pair, signal_name

    return None, None


