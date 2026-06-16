from __future__ import annotations

import numpy as np
import pandas as pd
from pandas import DataFrame

from DualTrendCompressionRestartLongCandidates import DualTrendCompressionRestartLongBase


class DualTrendCompressionRestartLongV1Strategy(DualTrendCompressionRestartLongBase):
    """
    Long-only V1 for the dual-trend compression restart idea.

    This version keeps the same dual-trend pullback restart skeleton used in the
    signal audit, but narrows it to the pairs and filters that held up better in
    both recent and full-sample backtests.
    """

    can_short = False
    enable_long_pullback_restart = True
    enable_long_compression_breakout = False
    require_btc_trend_up_for_longs = True

    minimal_roi = {"0": 0.05}

    long_close_position_min = 0.72
    max_entry_atr_pct = 0.05
    max_return_24h = 0.12
    min_return_24h = -0.02
    max_pullback_depth_v2 = 0.05

    trade_pair_allowlist = {
        "BNB/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "ZEC/USDT:USDT",
    }

    def _entry_candle(self, pair: str, trade):
        if not self.dp:
            return None
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None
        trade_time = pd.Timestamp(trade.open_date_utc)
        if trade_time.tzinfo is None:
            trade_time = trade_time.tz_localize("UTC")
        candidates = dataframe[dataframe["date"] < trade_time]
        if candidates.empty:
            candidates = dataframe[dataframe["date"] <= trade_time]
        if candidates.empty:
            return None
        return candidates.iloc[-1]

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        if "enter_long" not in dataframe:
            return dataframe

        entry = dataframe["enter_long"] == 1
        if not entry.any():
            return dataframe

        keep = (
            (dataframe["atr_pct"] <= self.max_entry_atr_pct)
            & dataframe["return_24h"].between(self.min_return_24h, self.max_return_24h)
            & (dataframe["pullback_depth_long"] <= self.max_pullback_depth_v2)
            & (dataframe["close"] > dataframe["ema50_4h"])
        )
        clear = entry & ~keep
        dataframe.loc[clear, ["enter_long", "enter_tag"]] = (0, None)
        dataframe.loc[clear, ["enter_initial_stop", "enter_risk_pct"]] = np.nan
        return dataframe
