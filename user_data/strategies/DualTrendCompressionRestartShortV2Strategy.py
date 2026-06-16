from __future__ import annotations

import numpy as np
from pandas import DataFrame

from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy


class DualTrendCompressionRestartShortV2Strategy(DualTrendCompressionRestartShortV1Strategy):
    """
    V2 short strategy built from the V1 dual-trend compression restart logic.

    V1 is kept unchanged. V2 keeps the same double-trend core, then adds:
    - a cleaner pair universe based on robustness tests,
    - entry filters to avoid overextended/high-volatility shorts,
    - a slightly faster 8% ROI target to reduce giveback.
    """

    minimal_roi = {"0": 0.08}

    trade_pair_allowlist = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "ADA/USDT:USDT",
        "SUI/USDT:USDT",
        "ZEC/USDT:USDT",
        "TAO/USDT:USDT",
    }

    max_entry_atr_pct = 0.065
    min_return_24h = -0.16
    pullback_close_position_max_v2 = 0.34
    compression_volume_multiplier_v2 = 1.45
    compression_min_return_24h = -0.12

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        if "enter_short" not in dataframe:
            return dataframe

        entry = dataframe["enter_short"] == 1
        if not entry.any():
            return dataframe

        atr_ok = dataframe["atr_pct"] <= self.max_entry_atr_pct
        not_too_extended = dataframe["return_24h"] >= self.min_return_24h
        pullback_quality = (
            (dataframe["enter_tag"] != "short_pullback_restart")
            | (dataframe["close_position"] <= self.pullback_close_position_max_v2)
        )
        compression_quality = (
            (dataframe["enter_tag"] != "short_compression_breakdown")
            | (
                (dataframe["volume"] > dataframe["volume_ma20"] * self.compression_volume_multiplier_v2)
                & (dataframe["return_24h"] >= self.compression_min_return_24h)
            )
        )
        keep = atr_ok & not_too_extended & pullback_quality & compression_quality
        clear = entry & ~keep
        dataframe.loc[clear, ["enter_short", "enter_tag"]] = (0, None)
        dataframe.loc[clear, ["enter_initial_stop", "enter_risk_pct"]] = np.nan
        return dataframe
