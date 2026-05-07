"""BTC informative dataframe builders extracted from NFI X7."""

import logging
import time

log = logging.getLogger(__name__)


def add_btc_prefix(dataframe):
    """Prefix BTC informative columns while keeping Freqtrade's date column."""

    ignore_columns = ["date"]
    dataframe.rename(columns=lambda s: f"btc_{s}" if s not in ignore_columns else s, inplace=True)
    return dataframe


def btc_info_indicators(strategy, btc_info_pair: str, btc_info_timeframe: str, metadata: dict):
    """Load and prefix BTC informative candles for one timeframe."""

    tik = time.perf_counter()
    btc_info = strategy.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    add_btc_prefix(btc_info)
    tok = time.perf_counter()
    log.debug(
        f"[{metadata['pair']}] btc_info_{btc_info_timeframe}_indicators took: {tok - tik:0.4f} seconds."
    )
    return btc_info


def btc_info_switcher(strategy, btc_info_pair: str, btc_info_timeframe: str, metadata: dict):
    """Switch BTC informative timeframe exactly like the original NFI strategy."""

    if btc_info_timeframe in {"1d", "4h", "1h", "15m", "5m"}:
        return btc_info_indicators(strategy, btc_info_pair, btc_info_timeframe, metadata)

    raise RuntimeError(f"{btc_info_timeframe} not supported as informative timeframe for BTC pair.")
