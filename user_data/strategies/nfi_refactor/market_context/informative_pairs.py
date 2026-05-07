"""Informative pair construction for the NFI refactor.

Freqtrade uses this list to know which extra pair/timeframe candles must be
cached before indicator calculation. This module mirrors NFI X7 behavior.
"""

FIAT_STAKE_CURRENCIES = {
    "USDT",
    "BUSD",
    "USDC",
    "DAI",
    "TUSD",
    "FDUSD",
    "PAX",
    "USD",
    "EUR",
    "GBP",
    "TRY",
}

LEVERAGED_TRADING_MODES = {"futures", "margin"}


def build_btc_info_pair(config: dict) -> str:
    """Return the BTC informative pair name used by the original NFI strategy."""

    stake_currency = config["stake_currency"]
    trading_mode = config.get("trading_mode")
    is_leveraged = trading_mode in LEVERAGED_TRADING_MODES

    if stake_currency in FIAT_STAKE_CURRENCIES:
        if is_leveraged:
            return f"BTC/{stake_currency}:{stake_currency}"
        return f"BTC/{stake_currency}"

    if is_leveraged:
        return "BTC/USDT:USDT"
    return "BTC/USDT"


def build_informative_pairs(
    pairs: list[str],
    config: dict,
    info_timeframes: list[str],
    btc_info_timeframes: list[str],
) -> list[tuple[str, str]]:
    """Build pair/timeframe tuples exactly like NostalgiaForInfinityX7."""

    informative_pairs: list[tuple[str, str]] = []
    for info_timeframe in info_timeframes:
        informative_pairs.extend((pair, info_timeframe) for pair in pairs)

    btc_info_pair = build_btc_info_pair(config)
    informative_pairs.extend((btc_info_pair, timeframe) for timeframe in btc_info_timeframes)

    return informative_pairs
