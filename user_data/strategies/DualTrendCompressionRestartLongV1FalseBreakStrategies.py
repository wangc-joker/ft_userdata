from __future__ import annotations

from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade

from DualTrendCompressionRestartLongV1ValidationStrategies import (
    DualTrendCompressionRestartLongPullbackOnlyV1Strategy,
)
from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy


class _LongFalseBreakMixin(DualTrendCompressionRestartLongPullbackOnlyV1Strategy):
    fast_exit_hours: Optional[int] = None
    fast_exit_need_half_r = False
    roi_value = 0.05

    minimal_roi = {"0": 0.05}

    @staticmethod
    def _clear_entries(dataframe: DataFrame, mask: pd.Series) -> None:
        if not isinstance(mask, pd.Series):
            if not bool(mask):
                return
            mask = pd.Series(True, index=dataframe.index)
        dataframe.loc[mask, ["enter_long", "enter_tag"]] = (0, None)
        dataframe.loc[mask, ["enter_initial_stop", "enter_risk_pct"]] = np.nan

    def _risk_ratio(self, pair: str, trade: Trade) -> float:
        candle = self._entry_candle(pair, trade)
        if candle is not None:
            stop = float(candle.get("long_pullback_stop", np.nan))
            if np.isfinite(stop) and trade.open_rate > stop:
                return (trade.open_rate - stop) / trade.open_rate
        risk = abs(float(trade.initial_stop_loss_pct or 0.0))
        return risk if np.isfinite(risk) and risk > 0 else self.max_stop_distance

    def _entry_compression_high(self, pair: str, trade: Trade) -> Optional[float]:
        candle = self._entry_candle(pair, trade)
        if candle is None:
            return None
        compression_high = float(candle.get("compression_high", np.nan))
        return compression_high if np.isfinite(compression_high) else None

    def _post_entry_window(self, pair: str, trade: Trade, current_time) -> Optional[DataFrame]:
        if not self.dp:
            return None
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None
        start = pd.Timestamp(trade.open_date_utc)
        end = pd.Timestamp(current_time)
        if start.tzinfo is None:
            start = start.tz_localize("UTC")
        if end.tzinfo is None:
            end = end.tz_localize("UTC")
        return dataframe[(dataframe["date"] >= start) & (dataframe["date"] <= end)]

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
        if candle is not None and self.fast_exit_hours is not None:
            age = current_time - trade.open_date_utc
            compression_high = self._entry_compression_high(pair, trade)
            if (
                compression_high is not None
                and age <= timedelta(hours=self.fast_exit_hours)
                and float(candle.get("close", current_rate)) < compression_high
            ):
                return f"false_break_{self.fast_exit_hours}h"

            if self.fast_exit_need_half_r and age >= timedelta(hours=6):
                window = self._post_entry_window(pair, trade, current_time)
                risk = self._risk_ratio(pair, trade)
                if window is not None and not window.empty and risk > 0:
                    max_favorable = (float(window["high"].max()) - trade.open_rate) / trade.open_rate
                    if max_favorable < 0.5 * risk and current_profit < 0:
                        return "no_half_r_6h_loss"

        return super().custom_exit(pair, trade, current_time, current_rate, current_profit, **kwargs)


class DualTrendCompressionRestartLongPullbackConfirmNextV1Strategy(_LongFalseBreakMixin):
    """
    B: the original breakout signal must be followed by another close above the
    original compression high.
    """

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        enter_long = dataframe.get("enter_long", pd.Series(0, index=dataframe.index))
        enter_tag = dataframe.get("enter_tag", pd.Series(None, index=dataframe.index))
        original = (enter_long == 1) & (enter_tag == "long_pullback_restart")
        prev_signal = original.shift(1).fillna(False)
        confirm_quality = (
            dataframe["candle_quality_long"].fillna(False)
            & dataframe["long_pullback_risk_pct_ok"].fillna(False)
            & (dataframe["volume"] > 0)
        )
        confirmed = prev_signal & (dataframe["close"] > dataframe["compression_high"].shift(1)) & confirm_quality

        self._clear_entries(dataframe, enter_long == 1)
        dataframe.loc[confirmed, ["enter_long", "enter_tag"]] = (1, "long_pullback_confirm_next")
        dataframe.loc[confirmed, "enter_initial_stop"] = dataframe.loc[confirmed, "long_pullback_stop"]
        dataframe.loc[confirmed, "enter_risk_pct"] = dataframe.loc[confirmed, "long_pullback_risk_pct"]
        return dataframe


class DualTrendCompressionRestartLongPullbackRetestConfirmV1Strategy(_LongFalseBreakMixin):
    """
    C: after the original breakout, wait 1-6 candles for a controlled retest of
    compression_high or EMA20, then require renewed strength.
    """

    retest_max_candles = 6
    retest_tolerance = 0.003
    retest_break_tolerance = 0.005

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        dataframe["ema20"] = self._ema(dataframe["close"], 20)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        original = (dataframe.get("enter_long", 0) == 1) & (dataframe.get("enter_tag") == "long_pullback_restart")
        confirmed = pd.Series(False, index=dataframe.index)

        for bars in range(1, self.retest_max_candles + 1):
            signal = original.shift(bars).fillna(False)
            compression_level = dataframe["compression_high"].shift(bars)
            ema20_level = dataframe["ema20"].shift(bars)
            level = pd.concat([compression_level, ema20_level], axis=1).max(axis=1)

            lows_after_signal = dataframe["low"].shift(1).rolling(bars).min() if bars > 1 else dataframe["low"]
            touched = lows_after_signal <= level * (1 + self.retest_tolerance)
            held = lows_after_signal >= level * (1 - self.retest_break_tolerance)
            renewed_strength = (
                (dataframe["close"] > dataframe["open"])
                & (dataframe["close"] > dataframe["high"].shift(1))
                & (dataframe["close"] > compression_level)
            )
            confirmed |= signal & touched & held & renewed_strength

        self._clear_entries(dataframe, dataframe.get("enter_long", 0) == 1)
        dataframe.loc[confirmed, ["enter_long", "enter_tag"]] = (1, "long_pullback_retest_confirm")
        dataframe.loc[confirmed, "enter_initial_stop"] = dataframe.loc[confirmed, "long_pullback_stop"]
        dataframe.loc[confirmed, "enter_risk_pct"] = dataframe.loc[confirmed, "long_pullback_risk_pct"]
        return dataframe


class DualTrendCompressionRestartLongPullbackFastExit3hV1Strategy(_LongFalseBreakMixin):
    fast_exit_hours = 3


class DualTrendCompressionRestartLongPullbackFastExit6hV1Strategy(_LongFalseBreakMixin):
    fast_exit_hours = 6


class DualTrendCompressionRestartLongPullbackNoHalfR6hV1Strategy(_LongFalseBreakMixin):
    fast_exit_need_half_r = True


class DualTrendCompressionRestartLongPullbackFastExit3hRoi6V1Strategy(DualTrendCompressionRestartLongPullbackFastExit3hV1Strategy):
    minimal_roi = {"0": 0.06}


class DualTrendCompressionRestartLongPullbackFastExit6hRoi6V1Strategy(DualTrendCompressionRestartLongPullbackFastExit6hV1Strategy):
    minimal_roi = {"0": 0.06}


class DualTrendCompressionRestartLongPullbackNoHalfR6hRoi6V1Strategy(DualTrendCompressionRestartLongPullbackNoHalfR6hV1Strategy):
    minimal_roi = {"0": 0.06}


class _LongRelativeStrengthBase(_LongFalseBreakMixin):
    min_rs_24h = -0.01
    require_rs_72h = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        dataframe["pair_return_72h"] = dataframe["close"].shift(1) / dataframe["close"].shift(73) - 1
        if self.dp and metadata["pair"] != "BTC/USDT:USDT":
            btc = self.dp.get_pair_dataframe(pair="BTC/USDT:USDT", timeframe=self.timeframe)
            if btc is not None and not btc.empty:
                btc = btc.copy().sort_values("date")
                btc["btc_return_24h"] = btc["close"].shift(1) / btc["close"].shift(25) - 1
                btc["btc_return_72h"] = btc["close"].shift(1) / btc["close"].shift(73) - 1
                dataframe = pd.merge_asof(
                    dataframe.sort_values("date"),
                    btc[["date", "btc_return_24h", "btc_return_72h"]].sort_values("date"),
                    on="date",
                    direction="backward",
                )
        if "btc_return_24h" not in dataframe:
            dataframe["btc_return_24h"] = 0.0
        if "btc_return_72h" not in dataframe:
            dataframe["btc_return_72h"] = 0.0
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        entry = dataframe.get("enter_long", 0) == 1
        rs_ok = dataframe["return_24h"] > dataframe["btc_return_24h"].fillna(0.0) + self.min_rs_24h
        if self.require_rs_72h:
            rs_ok &= dataframe["pair_return_72h"] > dataframe["btc_return_72h"].fillna(0.0)
        self._clear_entries(dataframe, entry & ~rs_ok)
        return dataframe


class DualTrendCompressionRestartLongPullbackRS24Minus1V1Strategy(_LongRelativeStrengthBase):
    min_rs_24h = -0.01


class DualTrendCompressionRestartLongPullbackRS24BeatBtcV1Strategy(_LongRelativeStrengthBase):
    min_rs_24h = 0.0


class DualTrendCompressionRestartLongPullbackRS24And72BeatBtcV1Strategy(_LongRelativeStrengthBase):
    min_rs_24h = 0.0
    require_rs_72h = True


class DualTrendCompressionRestartLongPullbackStrongSlopeV1Strategy(_LongFalseBreakMixin):
    min_pair_ema50_4h_slope = 0.002

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        entry = dataframe.get("enter_long", 0) == 1
        slope = dataframe["ema50_4h"] / dataframe["ema50_4h"].shift(12) - 1
        self._clear_entries(dataframe, entry & ~(slope > self.min_pair_ema50_4h_slope))
        return dataframe


class DualTrendCompressionRestartLongPullbackBtc1dSlopeV1Strategy(_LongFalseBreakMixin):
    def informative_pairs(self):
        pairs = super().informative_pairs()
        if self.use_btc_filter:
            pairs = list(set(pairs + [("BTC/USDT:USDT", "1d")]))
        return pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        if self.dp and metadata["pair"] != "BTC/USDT:USDT":
            btc_1d = self.dp.get_pair_dataframe(pair="BTC/USDT:USDT", timeframe="1d")
            if btc_1d is not None and not btc_1d.empty:
                btc_1d = btc_1d.copy().sort_values("date")
                btc_1d["btc_ema50_1d"] = self._ema(btc_1d["close"], 50)
                btc_1d["btc_1d_ema50_slope_up"] = btc_1d["btc_ema50_1d"] > btc_1d["btc_ema50_1d"].shift(1)
                dataframe = pd.merge_asof(
                    dataframe.sort_values("date"),
                    btc_1d[["date", "btc_1d_ema50_slope_up"]].sort_values("date"),
                    on="date",
                    direction="backward",
                )
        if "btc_1d_ema50_slope_up" not in dataframe:
            dataframe["btc_1d_ema50_slope_up"] = True
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        entry = dataframe.get("enter_long", 0) == 1
        self._clear_entries(dataframe, entry & ~dataframe["btc_1d_ema50_slope_up"].fillna(False))
        return dataframe


class DualTrendCompressionRestartLongPullbackEma50Distance08V1Strategy(_LongFalseBreakMixin):
    max_ema50_4h_distance = 0.08

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        entry = dataframe.get("enter_long", 0) == 1
        distance = dataframe["close"] / dataframe["ema50_4h"] - 1
        self._clear_entries(dataframe, entry & ~(distance <= self.max_ema50_4h_distance))
        return dataframe


class DualTrendCompressionRestartLongPullbackEma50Distance05V1Strategy(DualTrendCompressionRestartLongPullbackEma50Distance08V1Strategy):
    max_ema50_4h_distance = 0.05


class DTLV1CurrentRoi5(_LongFalseBreakMixin):
    pass


class DTLV1CurrentRoi6(_LongFalseBreakMixin):
    minimal_roi = {"0": 0.06}


class DTLV1ConfirmNext(DualTrendCompressionRestartLongPullbackConfirmNextV1Strategy):
    pass


class DTLV1RetestConfirm(DualTrendCompressionRestartLongPullbackRetestConfirmV1Strategy):
    pass


class DTLV1Fast3Roi5(DualTrendCompressionRestartLongPullbackFastExit3hV1Strategy):
    pass


class DTLV1Fast6Roi5(DualTrendCompressionRestartLongPullbackFastExit6hV1Strategy):
    pass


class DTLV1NoHalfR6Roi5(DualTrendCompressionRestartLongPullbackNoHalfR6hV1Strategy):
    pass


class DTLV1Fast3Roi6(DualTrendCompressionRestartLongPullbackFastExit3hRoi6V1Strategy):
    pass


class DTLV1Fast6Roi6(DualTrendCompressionRestartLongPullbackFastExit6hRoi6V1Strategy):
    pass


class DTLV1NoHalfR6Roi6(DualTrendCompressionRestartLongPullbackNoHalfR6hRoi6V1Strategy):
    pass


class DTLV1RSMinus1(DualTrendCompressionRestartLongPullbackRS24Minus1V1Strategy):
    pass


class DTLV1RSBeat24(DualTrendCompressionRestartLongPullbackRS24BeatBtcV1Strategy):
    pass


class DTLV1RSBeat24And72(DualTrendCompressionRestartLongPullbackRS24And72BeatBtcV1Strategy):
    pass


class DTLV1StrongSlope(DualTrendCompressionRestartLongPullbackStrongSlopeV1Strategy):
    pass


class DTLV1Btc1dSlope(DualTrendCompressionRestartLongPullbackBtc1dSlopeV1Strategy):
    pass


class DTLV1EmaDist08(DualTrendCompressionRestartLongPullbackEma50Distance08V1Strategy):
    pass


class DTLV1EmaDist05(DualTrendCompressionRestartLongPullbackEma50Distance05V1Strategy):
    pass


class DTLV1ConfirmStrong(DTLV1ConfirmNext):
    min_pair_ema50_4h_slope = 0.002

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        entry = dataframe.get("enter_long", 0) == 1
        slope = dataframe["ema50_4h"] / dataframe["ema50_4h"].shift(12) - 1
        self._clear_entries(dataframe, entry & ~(slope > self.min_pair_ema50_4h_slope))
        return dataframe


class LongV1ConfirmStrongRoi5Strategy(DTLV1ConfirmStrong):
    """
    Formal Long V1 confirm-strong version:
    pullback restart only, next-candle confirmation, strong pair 4h EMA50 slope,
    BTC 4h uptrend filter, no fast false-break exit, no partial take-profit.
    """

    minimal_roi = {"0": 0.05}
    fast_exit_hours = None
    fast_exit_need_half_r = False
    position_adjustment_enable = False
    enable_long_pullback_restart = True
    enable_long_compression_breakout = False
    require_btc_trend_up_for_longs = True


class LongV1ConfirmStrongRoi6Strategy(LongV1ConfirmStrongRoi5Strategy):
    minimal_roi = {"0": 0.06}


class LongV1ConfirmStrongRoi5Full13Strategy(LongV1ConfirmStrongRoi5Strategy):
    """
    Validation helper: keep the same LongV1ConfirmStrong Roi5 rules, but allow
    the full 13-pair dualtrend universe used by the short-side bot.
    """

    trade_pair_allowlist = DualTrendCompressionRestartShortV1Strategy.trade_pair_allowlist


class _ShortPullbackLongConfirmStrongBase(LongV1ConfirmStrongRoi5Strategy):
    """
    Combined validation helper.

    Short side keeps the short pullback-only rules and a 10% ROI custom target.
    Long side keeps LongV1ConfirmStrong with the class-specific ROI target.
    """

    can_short = True
    minimal_roi = {"0": 1.0}
    short_roi_value = 0.10
    long_roi_value = 0.05
    enable_short_pullback_restart = True
    enable_short_compression_breakdown = False
    long_trade_pair_allowlist = LongV1ConfirmStrongRoi5Strategy.trade_pair_allowlist
    trade_pair_allowlist = DualTrendCompressionRestartShortV1Strategy.trade_pair_allowlist

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = DualTrendCompressionRestartShortV1Strategy.populate_entry_trend(self, dataframe, metadata)

        original_allowlist = self.trade_pair_allowlist
        try:
            self.trade_pair_allowlist = self.long_trade_pair_allowlist
            dataframe = DTLV1ConfirmStrong.populate_entry_trend(self, dataframe, metadata)
        finally:
            self.trade_pair_allowlist = original_allowlist
        return dataframe

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
        if getattr(trade, "is_short", False):
            return DualTrendCompressionRestartShortV1Strategy.custom_stoploss(
                self,
                pair,
                trade,
                current_time,
                current_rate,
                current_profit,
                after_fill,
                **kwargs,
            )
        return LongV1ConfirmStrongRoi5Strategy.custom_stoploss(
            self,
            pair,
            trade,
            current_time,
            current_rate,
            current_profit,
            after_fill,
            **kwargs,
        )

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        if getattr(trade, "is_short", False):
            if current_profit >= self.short_roi_value:
                return "short_roi_10"
            return DualTrendCompressionRestartShortV1Strategy.custom_exit(
                self,
                pair,
                trade,
                current_time,
                current_rate,
                current_profit,
                **kwargs,
            )

        if current_profit >= self.long_roi_value:
            return f"long_roi_{int(self.long_roi_value * 100)}"
        return DTLV1ConfirmStrong.custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs)


class ShortPullbackLongV1ConfirmStrongRoi5Strategy(_ShortPullbackLongConfirmStrongBase):
    long_roi_value = 0.05


class ShortPullbackLongV1ConfirmStrongRoi6Strategy(_ShortPullbackLongConfirmStrongBase):
    long_roi_value = 0.06


class DTLV1ConfirmEmaDist08(DTLV1ConfirmNext):
    max_ema50_4h_distance = 0.08

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        entry = dataframe.get("enter_long", 0) == 1
        distance = dataframe["close"] / dataframe["ema50_4h"] - 1
        self._clear_entries(dataframe, entry & ~(distance <= self.max_ema50_4h_distance))
        return dataframe


class DTLV1ConfirmRS24And72(DTLV1ConfirmNext):
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)
        dataframe["pair_return_72h"] = dataframe["close"].shift(1) / dataframe["close"].shift(73) - 1
        if self.dp and metadata["pair"] != "BTC/USDT:USDT":
            btc = self.dp.get_pair_dataframe(pair="BTC/USDT:USDT", timeframe=self.timeframe)
            if btc is not None and not btc.empty:
                btc = btc.copy().sort_values("date")
                btc["btc_return_24h"] = btc["close"].shift(1) / btc["close"].shift(25) - 1
                btc["btc_return_72h"] = btc["close"].shift(1) / btc["close"].shift(73) - 1
                dataframe = pd.merge_asof(
                    dataframe.sort_values("date"),
                    btc[["date", "btc_return_24h", "btc_return_72h"]].sort_values("date"),
                    on="date",
                    direction="backward",
                )
        if "btc_return_24h" not in dataframe:
            dataframe["btc_return_24h"] = 0.0
        if "btc_return_72h" not in dataframe:
            dataframe["btc_return_72h"] = 0.0
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        entry = dataframe.get("enter_long", 0) == 1
        rs_ok = (
            (dataframe["return_24h"] > dataframe["btc_return_24h"].fillna(0.0))
            & (dataframe["pair_return_72h"] > dataframe["btc_return_72h"].fillna(0.0))
        )
        self._clear_entries(dataframe, entry & ~rs_ok)
        return dataframe
