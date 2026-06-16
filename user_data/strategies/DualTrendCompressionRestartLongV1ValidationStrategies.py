from __future__ import annotations

from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import stoploss_from_absolute

from DualTrendCompressionRestartLongV1Strategy import DualTrendCompressionRestartLongV1Strategy


class DualTrendCompressionRestartLongPullbackOnlyV1Strategy(DualTrendCompressionRestartLongV1Strategy):
    enable_long_pullback_restart = True
    enable_long_compression_breakout = False


class DualTrendCompressionRestartLongCompressionOnlyV1Strategy(DualTrendCompressionRestartLongV1Strategy):
    enable_long_pullback_restart = False
    enable_long_compression_breakout = True


class DualTrendCompressionRestartLongCombinedV1Strategy(DualTrendCompressionRestartLongV1Strategy):
    enable_long_pullback_restart = True
    enable_long_compression_breakout = True


class DualTrendCompressionRestartLongPullbackBtcCurrentV1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    """
    Current Long V1 BTC filter: non-BTC longs require BTC 4h uptrend.
    """


class DualTrendCompressionRestartLongPullbackBtcNotDownV1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    """
    Looser base filter: non-BTC longs are allowed when BTC 4h is not downtrend.
    """

    require_btc_trend_up_for_longs = False


class DualTrendCompressionRestartLongPullbackBtc4h1dV1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    """
    Stronger BTC filter: BTC 4h uptrend and BTC 1d close above EMA50.
    """

    def informative_pairs(self):
        pairs = super().informative_pairs()
        if self.use_btc_filter:
            pairs = list(set(pairs + [("BTC/USDT:USDT", "1d")]))
        return pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        if self.use_btc_filter and self.dp and metadata["pair"] != "BTC/USDT:USDT":
            btc_1d = self.dp.get_pair_dataframe(pair="BTC/USDT:USDT", timeframe="1d")
            if btc_1d is not None and not btc_1d.empty:
                btc_1d = btc_1d.copy().sort_values("date")
                btc_1d["btc_ema50_1d"] = self._ema(btc_1d["close"], 50)
                btc_1d["btc_1d_above_ema50"] = btc_1d["close"] > btc_1d["btc_ema50_1d"]
                dataframe = pd.merge_asof(
                    dataframe.sort_values("date"),
                    btc_1d[["date", "btc_1d_above_ema50"]].sort_values("date"),
                    on="date",
                    direction="backward",
                )
                dataframe["btc_1d_above_ema50"] = dataframe["btc_1d_above_ema50"].fillna(False)
            else:
                dataframe["btc_1d_above_ema50"] = False
        else:
            dataframe["btc_1d_above_ema50"] = True
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        if metadata["pair"] == "BTC/USDT:USDT" or "enter_long" not in dataframe:
            return dataframe
        clear = (dataframe["enter_long"] == 1) & ~dataframe["btc_1d_above_ema50"].fillna(False)
        dataframe.loc[clear, ["enter_long", "enter_tag"]] = (0, None)
        dataframe.loc[clear, ["enter_initial_stop", "enter_risk_pct"]] = np.nan
        return dataframe


class DualTrendCompressionRestartLongPullbackStop03V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    max_stop_distance = 0.03


class DualTrendCompressionRestartLongPullbackStop04V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    max_stop_distance = 0.04


class DualTrendCompressionRestartLongPullbackStop05V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    max_stop_distance = 0.05


class DualTrendCompressionRestartLongPullbackRoi03V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    minimal_roi = {"0": 0.03}


class DualTrendCompressionRestartLongPullbackRoi04V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    minimal_roi = {"0": 0.04}


class DualTrendCompressionRestartLongPullbackRoi05V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    minimal_roi = {"0": 0.05}


class DualTrendCompressionRestartLongPullbackRoi06V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    minimal_roi = {"0": 0.06}


class _LongPartialBase(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    minimal_roi = {"0": 0.20}
    position_adjustment_enable = True

    tp1_r = 1.0
    tp1_reduce = 0.5
    tp2_r: Optional[float] = None
    tp2_reduce = 0.0

    def _risk_ratio(self, trade: Trade) -> float:
        risk = abs(float(trade.initial_stop_loss_pct or 0.0))
        if not np.isfinite(risk) or risk <= 0:
            risk = self.max_stop_distance
        return risk

    def _get_flag(self, trade: Trade, key: str) -> bool:
        try:
            return bool(trade.get_custom_data(key, default=False))
        except Exception:
            return False

    def _set_flag(self, trade: Trade, key: str) -> bool:
        try:
            trade.set_custom_data(key, True)
            return True
        except Exception:
            return False

    def adjust_trade_position(
        self,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        min_stake: Optional[float],
        max_stake: float,
        current_entry_rate: float,
        current_exit_rate: float,
        current_entry_profit: float,
        current_exit_profit: float,
        **kwargs,
    ):
        risk = self._risk_ratio(trade)
        if current_profit >= self.tp1_r * risk and not self._get_flag(trade, "long_tp1_done"):
            if self._set_flag(trade, "long_tp1_done"):
                return -(trade.stake_amount * self.tp1_reduce)
            return None
        if (
            self.tp2_r is not None
            and current_profit >= self.tp2_r * risk
            and not self._get_flag(trade, "long_tp2_done")
        ):
            if self._set_flag(trade, "long_tp2_done"):
                return -(trade.stake_amount * self.tp2_reduce)
        return None

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> Optional[float]:
        base = super().custom_stoploss(pair, trade, current_time, current_rate, current_profit, after_fill, **kwargs)
        if self._get_flag(trade, "long_tp1_done"):
            return stoploss_from_absolute(
                trade.open_rate,
                current_rate,
                is_short=False,
                leverage=trade.leverage,
            )
        return base

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        base_exit = super().custom_exit(pair, trade, current_time, current_rate, current_profit, **kwargs)
        if base_exit:
            return base_exit
        if current_time - trade.open_date_utc > timedelta(hours=240) and current_profit > 0:
            return "partial_runner_timeout"
        return None


class DualTrendCompressionRestartLongPullbackPartial50V1Strategy(_LongPartialBase):
    tp1_r = 1.0
    tp1_reduce = 0.5
    tp2_r = None


class DualTrendCompressionRestartLongPullbackPartial3030V1Strategy(_LongPartialBase):
    tp1_r = 1.0
    tp1_reduce = 0.3
    tp2_r = 2.0
    tp2_reduce = 0.3


class DualTrendCompressionRestartLongPullbackFullPositivePairsV1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    trade_pair_allowlist = {
        "BNB/USDT:USDT",
        "DOGE/USDT:USDT",
        "ZEC/USDT:USDT",
    }


class DualTrendCompressionRestartLongPullbackRecentPositivePairsV1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    trade_pair_allowlist = {
        "BNB/USDT:USDT",
        "DOGE/USDT:USDT",
        "ZEC/USDT:USDT",
        "XRP/USDT:USDT",
    }


class DualTrendCompressionRestartLongPullbackDropWorst1V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    trade_pair_allowlist = {
        "BNB/USDT:USDT",
        "DOGE/USDT:USDT",
        "ZEC/USDT:USDT",
    }


class DualTrendCompressionRestartLongPullbackDropWorst2V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    trade_pair_allowlist = {
        "BNB/USDT:USDT",
        "DOGE/USDT:USDT",
    }


class DualTrendCompressionRestartLongPullbackTop8V1Strategy(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    trade_pair_allowlist = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "ADA/USDT:USDT",
        "LINK/USDT:USDT",
    }
