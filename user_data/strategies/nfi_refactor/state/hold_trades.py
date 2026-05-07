"""Hold-trades support extracted from NFI.

This live/dry-run helper lets an operator keep selected trades open until a
configured profit threshold is reached.
"""

import logging
import pathlib
import sys

from nfi_refactor.state.cache import HoldsCache

log = logging.getLogger(__name__)


def _strategy_file_path(strategy) -> pathlib.Path:
    strategy_module = sys.modules.get(strategy.__class__.__module__)
    if strategy_module is not None and getattr(strategy_module, "__file__", None):
        return pathlib.Path(strategy_module.__file__)
    return pathlib.Path(__file__)


def get_hold_trades_config_file(strategy):
    proper_holds_file_path = strategy.config["user_data_dir"].resolve() / "nfi-hold-trades.json"
    if proper_holds_file_path.is_file():
        return proper_holds_file_path

    strat_file_path = _strategy_file_path(strategy)
    hold_trades_config_file_resolve = strat_file_path.resolve().parent / "hold-trades.json"
    if hold_trades_config_file_resolve.is_file():
        log.warning(
            "Please move %s to %s which is now the expected path for the holds file",
            hold_trades_config_file_resolve,
            proper_holds_file_path,
        )
        return hold_trades_config_file_resolve

    hold_trades_config_file_absolute = strat_file_path.absolute().parent / "hold-trades.json"
    if hold_trades_config_file_absolute.is_file():
        log.warning(
            "Please move %s to %s which is now the expected path for the holds file",
            hold_trades_config_file_absolute,
            proper_holds_file_path,
        )
        return hold_trades_config_file_absolute


def load_hold_trades_config(strategy):
    if strategy.hold_trades_cache is None:
        hold_trades_config_file = strategy.get_hold_trades_config_file()
        if hold_trades_config_file:
            log.warning("Loading hold support data from %s", hold_trades_config_file)
            strategy.hold_trades_cache = HoldsCache(hold_trades_config_file)

    if strategy.hold_trades_cache:
        strategy.hold_trades_cache.load()


def should_hold_trade(strategy, trade, rate: float, sell_reason: str) -> bool:
    if strategy.config["runmode"].value not in ("live", "dry_run"):
        return False

    if not strategy.hold_support_enabled:
        return False

    strategy.load_hold_trades_config()

    if not strategy.hold_trades_cache:
        return False

    if not strategy.hold_trades_cache.data:
        return False

    hold_trade = False

    trade_ids: dict = strategy.hold_trades_cache.data.get("trade_ids")
    if trade_ids and trade.id in trade_ids:
        trade_profit_ratio = trade_ids[trade.id]
        filled_entries = trade.select_filled_orders(trade.entry_side)
        filled_exits = trade.select_filled_orders(trade.exit_side)
        profit_stake, profit_ratio, profit_current_stake_ratio, profit_init_ratio = strategy.calc_total_profit(
            trade, filled_entries, filled_exits, rate
        )
        current_profit_ratio = profit_init_ratio
        if sell_reason == "force_sell":
            formatted_profit_ratio = f"{trade_profit_ratio * 100}%"
            formatted_current_profit_ratio = f"{current_profit_ratio * 100}%"
            log.warning(
                "Force selling %s even though the current profit of %s < %s",
                trade,
                formatted_current_profit_ratio,
                formatted_profit_ratio,
            )
            return False
        elif current_profit_ratio >= trade_profit_ratio:
            formatted_profit_ratio = f"{trade_profit_ratio * 100}%"
            formatted_current_profit_ratio = f"{current_profit_ratio * 100}%"
            log.warning(
                "Selling %s because the current profit of %s >= %s",
                trade,
                formatted_current_profit_ratio,
                formatted_profit_ratio,
            )
            return False

        hold_trade = True

    trade_pairs: dict = strategy.hold_trades_cache.data.get("trade_pairs")
    if trade_pairs and trade.pair in trade_pairs:
        trade_profit_ratio = trade_pairs[trade.pair]
        filled_entries = trade.select_filled_orders(trade.entry_side)
        filled_exits = trade.select_filled_orders(trade.exit_side)
        profit_stake, profit_ratio, profit_current_stake_ratio, profit_init_ratio = strategy.calc_total_profit(
            trade, filled_entries, filled_exits, rate
        )
        current_profit_ratio = profit_init_ratio
        if sell_reason == "force_sell":
            formatted_profit_ratio = f"{trade_profit_ratio * 100}%"
            formatted_current_profit_ratio = f"{current_profit_ratio * 100}%"
            log.warning(
                "Force selling %s even though the current profit of %s < %s",
                trade,
                formatted_current_profit_ratio,
                formatted_profit_ratio,
            )
            return False
        elif current_profit_ratio >= trade_profit_ratio:
            formatted_profit_ratio = f"{trade_profit_ratio * 100}%"
            formatted_current_profit_ratio = f"{current_profit_ratio * 100}%"
            log.warning(
                "Selling %s because the current profit of %s >= %s",
                trade,
                formatted_current_profit_ratio,
                formatted_profit_ratio,
            )
            return False

        hold_trade = True

    return hold_trade
