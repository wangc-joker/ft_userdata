"""Entry confirmation helpers extracted from NostalgiaForInfinityX7."""

import logging
from datetime import datetime
from typing import Optional

from freqtrade.persistence import Trade

log = logging.getLogger(__name__)


def confirm_trade_entry(
    strategy,
    pair: str,
    order_type: str,
    amount: float,
    rate: float,
    time_in_force: str,
    current_time: datetime,
    entry_tag: Optional[str],
    side: str,
    **kwargs,
) -> bool:
    # Force Entry
    if entry_tag == "force_entry":
        return True

    # Mode configurations (dynamic structure)
    mode_configs = {
        "grind": {
            "tags": strategy.long_grind_mode_tags,
            "coins": strategy.grind_mode_coins,
            "max_slots": strategy.grind_mode_max_slots,
            "log_message": "grind mode",
        },
        "top_coins": {
            "tags": strategy.long_top_coins_mode_tags,
            "coins": strategy.top_coins_mode_coins,
            "log_message": "top coins mode",
        },
        "scalp": {
            "tags": strategy.long_scalp_mode_tags,
            "min_free_slots": strategy.min_free_slots_scalp_mode,
            "log_message": "scalp mode",
        },
    }

    # Mode Validation
    for mode, config in mode_configs.items():
        if all(c in config["tags"] for c in entry_tag.split()):
            if mode == "grind":
                return handle_grind_mode(pair, config, current_time)
            elif mode == "top_coins":
                return handle_top_coins_mode(pair, config, current_time)
            elif mode == "scalp":
                return handle_scalp_mode(strategy, pair, config, current_time)

    # Long/Short Slot Validation (only in futures mode)
    if strategy.is_futures_mode and (
        strategy.futures_max_open_trades_long != 0 or strategy.futures_max_open_trades_short != 0
    ):
        open_trades = Trade.get_trades_proxy(is_open=True)
        long_trades = sum(1 for t in open_trades if t.trade_direction == "long")
        short_trades = sum(1 for t in open_trades if t.trade_direction == "short")

        # Long trade limit validation
        if (
            side == "long"
            and strategy.futures_max_open_trades_long != 0
            and long_trades >= strategy.futures_max_open_trades_long
        ):
            log.info(
                f"[{current_time}] Cancelling entry for {pair} due to long trades reaching the max limit of {strategy.futures_max_open_trades_long}."
            )
            return False

        # Short trade limit validation
        if (
            side == "short"
            and strategy.futures_max_open_trades_short != 0
            and short_trades >= strategy.futures_max_open_trades_short
        ):
            log.info(
                f"[{current_time}] Cancelling entry for {pair} due to short trades reaching the max limit of {strategy.futures_max_open_trades_short}."
            )
            return False

    # Slippage Validation
    df, _ = strategy.dp.get_analyzed_dataframe(pair, strategy.timeframe)
    if len(df) >= 1:
        last_candle = df.iloc[-1].squeeze()
        if (side == "long" and rate > last_candle["close"]) or (side == "short" and rate < last_candle["close"]):
            slippage = (rate / last_candle["close"]) - 1.0
            if (side == "long" and slippage < strategy.max_slippage) or (
                side == "short" and slippage > -strategy.max_slippage
            ):
                return True
            else:
                log.warning(f"[{current_time}] Cancelling entry for {pair} due to slippage {(slippage * 100.0):.2f}%")
                return False

    return True


def handle_grind_mode(pair: str, config: dict, current_time: datetime) -> bool:
    is_pair_grind_mode = pair.split("/")[0] in config["coins"]
    if not is_pair_grind_mode:
        log.info(f"[{current_time}] Cancelling entry for {pair} due to not being in grind mode coins list.")
        return False

    open_trades = Trade.get_trades_proxy(is_open=True)
    num_open_grind_mode = sum(1 for t in open_trades if all(c in config["tags"] for c in t.enter_tag.split()))
    if num_open_grind_mode >= config["max_slots"]:
        log.info(f"[{current_time}] Cancelling entry for {pair} due to grind mode slots limit reached.")
        return False

    return True


def handle_top_coins_mode(pair: str, config: dict, current_time: datetime) -> bool:
    is_pair_top_coins_mode = pair.split("/")[0] in config["coins"]
    if not is_pair_top_coins_mode:
        log.info(f"[{current_time}] Cancelling entry for {pair} due to not being in top coins list.")
        return False
    return True


def handle_scalp_mode(strategy, pair: str, config: dict, current_time: datetime) -> bool:
    current_free_slots = strategy.config["max_open_trades"] - Trade.get_open_trade_count()
    if current_free_slots < config["min_free_slots"]:
        log.info(f"[{current_time}] Cancelling entry for {pair} due to insufficient free slots.")
        return False
    return True
