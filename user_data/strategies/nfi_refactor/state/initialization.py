"""Strategy initialization helpers extracted from NFI."""

import logging
from datetime import datetime

from freqtrade.strategy.interface import IStrategy

from nfi_refactor.state.cache import Cache

log = logging.getLogger(__name__)

NFI_SAFE_PARAMETERS = [
    "num_cores_indicators_calc",
    "custom_fee_open_rate",
    "custom_fee_close_rate",
    "futures_mode_leverage",
    "futures_mode_leverage_rebuy_mode",
    "futures_mode_leverage_grind_mode",
    "futures_max_open_trades_long",
    "futures_max_open_trades_short",
    "stop_threshold_doom_spot",
    "stop_threshold_doom_futures",
    "stop_threshold_rapid_spot",
    "stop_threshold_rapid_futures",
    "stop_threshold_scalp_spot",
    "stop_threshold_scalp_futures",
    "derisk_enable",
    "stops_enable",
    "regular_mode_derisk_1_spot",
    "regular_mode_derisk_spot",
    "regular_mode_derisk_1_futures",
    "regular_mode_derisk_futures",
    "grind_mode_max_slots",
    "grind_mode_coins",
    "max_slippage",
]


def initialize_strategy(strategy, config: dict) -> None:
    if "ccxt_config" not in config["exchange"]:
        config["exchange"]["ccxt_config"] = {}
    if "ccxt_async_config" not in config["exchange"]:
        config["exchange"]["ccxt_async_config"] = {}

    options = {
        "brokerId": None,
        "broker": {"spot": None, "margin": None, "future": None, "delivery": None},
        "partner": {
            "spot": {"id": None, "key": None},
            "future": {"id": None, "key": None},
            "id": None,
            "key": None,
        },
    }

    config["exchange"]["ccxt_config"]["options"] = options
    config["exchange"]["ccxt_async_config"]["options"] = options
    IStrategy.__init__(strategy, config)

    if ("exit_profit_only" in strategy.config and strategy.config["exit_profit_only"]) or (
        "sell_profit_only" in strategy.config and strategy.config["sell_profit_only"]
    ):
        strategy.exit_profit_only = True

    is_config_advanced_mode = (
        "nfi_advanced_mode" in strategy.config and strategy.config["nfi_advanced_mode"] == True
    )
    if is_config_advanced_mode:
        log.warning("The advanced configuration mode is enabled. I hope you know what you are doing.")

    if "nfi_parameters" in strategy.config and type(strategy.config["nfi_parameters"]) is dict:
        for nfi_param in strategy.config["nfi_parameters"]:
            if nfi_param in ["long_entry_signal_params", "short_entry_signal_params"]:
                continue
            if (nfi_param in NFI_SAFE_PARAMETERS or is_config_advanced_mode) and hasattr(strategy, nfi_param):
                log.info(
                    f'Parameter {nfi_param} changed from "{getattr(strategy, nfi_param)}" to "{strategy.config["nfi_parameters"][nfi_param]}".'
                )
                setattr(strategy, nfi_param, strategy.config["nfi_parameters"][nfi_param])
            else:
                log.warning(f"Invalid or unsafe parameter: {nfi_param}.")

        strategy.update_signals_from_config(strategy.config["nfi_parameters"])

    for nfi_param in NFI_SAFE_PARAMETERS:
        if (nfi_param in strategy.config) and hasattr(strategy, nfi_param):
            setattr(strategy, nfi_param, strategy.config[nfi_param])

    if strategy.target_profit_cache is None:
        bot_name = ""
        if "bot_name" in strategy.config:
            bot_name = strategy.config["bot_name"] + "-"
        strategy.target_profit_cache = Cache(
            strategy.config["user_data_dir"]
            / (
                "nfix7-profit_max-"
                + bot_name
                + strategy.config["exchange"]["name"]
                + "-"
                + strategy.config["stake_currency"]
                + ("-(backtest)" if (strategy.config["runmode"].value == "backtest") else "")
                + ("-(hyperopt)" if (strategy.config["runmode"].value == "hyperopt") else "")
                + ".json"
            )
        )

    if strategy.config["exchange"]["name"] in ["okx", "okex"]:
        strategy.startup_candle_count = 480
    elif strategy.config["exchange"]["name"] in ["kraken"]:
        strategy.startup_candle_count = 710
    elif strategy.config["exchange"]["name"] in ["bybit"]:
        strategy.startup_candle_count = 199
    elif strategy.config["exchange"]["name"] in ["bitget"]:
        strategy.startup_candle_count = 499
    elif strategy.config["exchange"]["name"] in ["bingx"]:
        strategy.startup_candle_count = 499

    if ("trading_mode" in strategy.config) and (strategy.config["trading_mode"] in ["futures", "margin"]):
        strategy.is_futures_mode = True
        strategy.can_short = True

    strategy.target_profit_cache.save()
    strategy.update_signals_from_config(strategy.config)


def bot_loop_start(strategy, current_time, **kwargs) -> None:
    if strategy.config["runmode"].value not in ("live", "dry_run"):
        return IStrategy.bot_loop_start(strategy, datetime, **kwargs)

    if strategy.hold_support_enabled:
        strategy.load_hold_trades_config()

    return IStrategy.bot_loop_start(strategy, current_time, **kwargs)
