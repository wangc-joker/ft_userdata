"""Indicator pipeline extracted from NostalgiaForInfinityX7.

This module keeps the original `populate_indicators` orchestration together for
parity. It merges BTC informative data, pair informative data, base timeframe
indicators, and the original global protection columns.
"""

import logging
import time

import numpy as np
from freqtrade.strategy import merge_informative_pair
from pandas import DataFrame
from nfi_refactor.protections.global_protections import apply_global_protections

log = logging.getLogger(__name__)
def populate_indicators(strategy, df: DataFrame, metadata: dict) -> DataFrame:
  tik = time.perf_counter()
  """
      --> BTC informative indicators
      ___________________________________________________________________________________________
      """
  if strategy.config["stake_currency"] in [
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
  ]:
    if ("trading_mode" in strategy.config) and (strategy.config["trading_mode"] in ["futures", "margin"]):
      btc_info_pair = f"BTC/{strategy.config['stake_currency']}:{strategy.config['stake_currency']}"
    else:
      btc_info_pair = f"BTC/{strategy.config['stake_currency']}"
  else:
    if ("trading_mode" in strategy.config) and (strategy.config["trading_mode"] in ["futures", "margin"]):
      btc_info_pair = "BTC/USDT:USDT"
    else:
      btc_info_pair = "BTC/USDT"

  for btc_info_timeframe in strategy.btc_info_timeframes:
    btc_informative = strategy.btc_info_switcher(btc_info_pair, btc_info_timeframe, metadata)
    df = merge_informative_pair(df, btc_informative, strategy.timeframe, btc_info_timeframe, ffill=True)
    # Customize what we drop - in case we need to maintain some BTC informative ohlcv data
    # Default drop all
    drop_columns = {
      "1d": [f"btc_{s}_{btc_info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
      "4h": [f"btc_{s}_{btc_info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
      "1h": [f"btc_{s}_{btc_info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
      "15m": [f"btc_{s}_{btc_info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
      "5m": [f"btc_{s}_{btc_info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
    }.get(
      btc_info_timeframe,
      [f"{s}_{btc_info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
    )
    drop_columns.append(f"date_{btc_info_timeframe}")
    df.drop(columns=df.columns.intersection(drop_columns), inplace=True)

  """
      --> Indicators on informative timeframes
      ___________________________________________________________________________________________
      """
  for info_timeframe in strategy.info_timeframes:
    info_indicators = strategy.info_switcher(metadata, info_timeframe)
    df = merge_informative_pair(df, info_indicators, strategy.timeframe, info_timeframe, ffill=True)
    # Customize what we drop - in case we need to maintain some informative timeframe ohlcv data
    # Default drop all except base timeframe ohlcv data
    drop_columns = {
      "1d": [f"{s}_{info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
      "4h": [f"{s}_{info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
      "1h": [f"{s}_{info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
      "15m": [f"{s}_{info_timeframe}" for s in ["date", "high", "low", "volume"]],
    }.get(info_timeframe, [f"{s}_{info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]])
    df.drop(columns=df.columns.intersection(drop_columns), inplace=True)

  """
      --> The indicators for the base timeframe  (5m)
      ___________________________________________________________________________________________
      """
  df = strategy.base_tf_5m_indicators(metadata, df)

  # df["zlma_50_1h"] = df["zlma_50_1h"].astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
  # df["CTI_20_1d"] = df["CTI_20_1d"].astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
  # df["WILLR_480_1h"] = df["WILLR_480_1h"].astype(np.float64).replace(to_replace=[np.nan, None], value=(-50.0))
  # df["WILLR_480_4h"] = df["WILLR_480_4h"].astype(np.float64).replace(to_replace=[np.nan, None], value=(-50.0))
  # df["RSI_14_1d"] = df["RSI_14_1d"].astype(np.float64).replace(to_replace=[np.nan, None], value=(50.0))
  df["RSI_14_1h"] = df["RSI_14_1h"].astype(np.float64).replace(to_replace=[np.nan, None], value=(50.0))

  df = apply_global_protections(df)

  tok = time.perf_counter()
  log.debug(f"[{metadata['pair']}] Populate indicators took a total of: {tok - tik:0.4f} seconds.")

  return df

# Confirm Trade Entry
