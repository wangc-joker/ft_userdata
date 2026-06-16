from __future__ import annotations

from datetime import timedelta
from typing import Optional

import numpy as np
from pandas import DataFrame

from freqtrade.persistence import Trade

from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy


class DualTrendCompressionRestartShortV2Base(DualTrendCompressionRestartShortV1Strategy):
    """
    Experimental V2 base.

    V1 is intentionally left untouched. These candidates keep the dual-trend
    short framework and test whitelist, entry-quality, and exit changes.
    """

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


class DualTrendCompressionRestartShortV2WhitelistOnly(DualTrendCompressionRestartShortV2Base):
    """
    Candidate A: only remove the weakest V1 pairs: TRX, LINK, NEAR.
    """


class DualTrendCompressionRestartShortV2PullbackWhitelist(DualTrendCompressionRestartShortV2Base):
    """
    Candidate B: whitelist shrink plus pullback-only entries.
    """

    enable_short_compression_breakdown = False


class DualTrendCompressionRestartShortV2QualityFilter(DualTrendCompressionRestartShortV2Base):
    """
    Candidate C: whitelist shrink plus entry quality filters.
    """

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


class DualTrendCompressionRestartShortV2QualityExit(DualTrendCompressionRestartShortV2QualityFilter):
    """
    Candidate D: quality-filter entries plus faster stale exits.
    """

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        candle = self._current_candle(pair)
        if candle is None:
            return None

        age = current_time - trade.open_date_utc
        if age > timedelta(hours=48) and current_profit < -0.005:
            return "v2_stale_loss_48h"
        if age > timedelta(hours=96) and current_profit < 0.005:
            return "v2_stale_flat_96h"
        if age > timedelta(hours=168) and current_profit < 0.025:
            return "v2_stale_low_profit_168h"

        if bool(candle.get("trend_up_4h", False)) and current_profit < 0.03:
            return "trend_flip_short"
        return None


class DualTrendCompressionRestartShortV2QualityRoi8(DualTrendCompressionRestartShortV2QualityFilter):
    """
    Candidate E: quality-filter entries with an 8% fixed ROI target.
    """

    minimal_roi = {"0": 0.08}
