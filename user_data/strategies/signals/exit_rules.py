from typing import Optional

from freqtrade.persistence import Trade


def resolve_custom_exit(
    strategy,
    pair: str,
    trade: Trade,
    current_time,
    current_rate: float,
    current_profit: float,
    **kwargs,
) -> Optional[str]:
    if not strategy.dp:
        return None

    dataframe, _ = strategy.dp.get_analyzed_dataframe(pair, strategy.timeframe)
    if dataframe.empty:
        return None

    candle = dataframe.iloc[-1]
    tag = trade.enter_tag or ""
    scope = "1d" if "_1d_" in tag else "1h"
    suffix = "_1d" if scope == "1d" else ""

    stop_long = candle.get(f"structure_stop_long{suffix}")
    stop_short = candle.get(f"structure_stop_short{suffix}")

    if trade.is_short:
        if bool(candle.get("uptrend_1d", False)):
            return "trend_flip_short"
        if scope == "1d":
            if bool(candle.get("center_up_1d", False)) and candle["close"] > candle.get(
                "ema_fast_1d", candle["close"]
            ):
                return "structure_exit_short_1d"
        else:
            if bool(candle.get("center_up", False)) and candle["close"] > candle.get(
                "ema_fast", candle["close"]
            ):
                return "structure_exit_short_1h"

        if stop_short is not None and candle["close"] > stop_short:
            return f"swing_exit_short_{scope}"
        return None

    if bool(candle.get("downtrend_1d", False)):
        return "trend_flip_long"
    if scope == "1d":
        if bool(candle.get("center_down_1d", False)) and candle["close"] < candle.get(
            "ema_fast_1d", candle["close"]
        ):
            return "structure_exit_long_1d"
    else:
        if bool(candle.get("center_down", False)) and candle["close"] < candle.get(
            "ema_fast", candle["close"]
        ):
            return "structure_exit_long_1h"

    if stop_long is not None and candle["close"] < stop_long:
        return f"swing_exit_long_{scope}"

    return None
