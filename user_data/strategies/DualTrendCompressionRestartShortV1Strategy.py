from __future__ import annotations

from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, informative, stoploss_from_absolute


class DualTrendCompressionRestartShortV1Strategy(IStrategy):
    """
    Short-only V1 implementation of the dual-trend compression restart idea.

    This intentionally starts with only the two short signals that looked best
    in the offline audit:
    - short_pullback_restart
    - short_compression_breakdown

    It does not implement partial take-profit yet. The first goal is to run a
    clean Freqtrade backtest for entry quality, structural stoploss, and basic
    stale/trend-flip exits.
    """

    INTERFACE_VERSION = 3

    timeframe = "1h"
    can_short = True
    process_only_new_candles = True
    startup_candle_count = 1000

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True
    use_custom_stoploss = True
    position_adjustment_enable = False

    minimal_roi = {"0": 0.10}
    stoploss = -0.06
    max_open_trades = 3

    trend_ema_fast_4h = 50
    trend_ema_slow_4h = 200
    trend_slope_lookback_4h = 3

    atr_period_1h = 14
    volume_ma_window_1h = 20
    compression_window = 12
    compression_half_window = 6
    pretrend_window = 24

    compression_atr_multiplier = 3.0
    volume_breakout_multiplier = 1.2
    breakout_buffer = 0.001
    stop_atr_buffer = 0.2

    min_stop_distance = 0.005
    max_stop_distance = 0.05
    pullback_min_depth = 0.008
    pullback_max_depth = 0.08
    low_zone_buffer = 1.035

    candle_body_min = 0.35
    short_close_position_max = 0.40

    risk_per_trade = 0.0075
    max_position_value_pct = 0.35
    leverage_value = 1.0
    use_btc_filter = True
    enable_short_pullback_restart = True
    enable_short_compression_breakdown = True

    trade_pair_allowlist = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "ADA/USDT:USDT",
        "LINK/USDT:USDT",
        "NEAR/USDT:USDT",
        "SUI/USDT:USDT",
        "TRX/USDT:USDT",
        "ZEC/USDT:USDT",
        "TAO/USDT:USDT",
    }

    @property
    def protections(self):
        return [
            {"method": "CooldownPeriod", "stop_duration_candles": 3},
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 60,
                "trade_limit": 2,
                "stop_duration_candles": 14,
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 96,
                "trade_limit": 10,
                "stop_duration_candles": 24,
                "max_allowed_drawdown": 0.10,
            },
        ]

    @staticmethod
    def _ema(series: pd.Series, period: int) -> pd.Series:
        return series.ewm(span=period, adjust=False, min_periods=period).mean()

    @staticmethod
    def _atr(dataframe: DataFrame, period: int) -> pd.Series:
        prev_close = dataframe["close"].shift(1)
        true_range = pd.concat(
            [
                dataframe["high"] - dataframe["low"],
                (dataframe["high"] - prev_close).abs(),
                (dataframe["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    @staticmethod
    def _merge_btc_context(dataframe: DataFrame, btc_dataframe: DataFrame) -> DataFrame:
        left = dataframe.sort_values("date")
        right = btc_dataframe[["date", "trend_up", "trend_down"]].rename(
            columns={
                "trend_up": "btc_trend_up_4h",
                "trend_down": "btc_trend_down_4h",
            }
        ).sort_values("date")
        return pd.merge_asof(left, right, on="date", direction="backward")

    def _add_4h_trend(self, dataframe: DataFrame) -> DataFrame:
        dataframe = dataframe.copy()
        dataframe["ema50"] = self._ema(dataframe["close"], self.trend_ema_fast_4h)
        dataframe["ema200"] = self._ema(dataframe["close"], self.trend_ema_slow_4h)
        dataframe["trend_up"] = (
            (dataframe["close"] > dataframe["ema50"])
            & (dataframe["ema50"] > dataframe["ema200"])
            & (dataframe["ema50"] > dataframe["ema50"].shift(self.trend_slope_lookback_4h))
        )
        dataframe["trend_down"] = (
            (dataframe["close"] < dataframe["ema50"])
            & (dataframe["ema50"] < dataframe["ema200"])
            & (dataframe["ema50"] < dataframe["ema50"].shift(self.trend_slope_lookback_4h))
        )
        return dataframe

    @informative("4h")
    def populate_indicators_4h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return self._add_4h_trend(dataframe)

    def informative_pairs(self):
        if not self.use_btc_filter:
            return []
        return [("BTC/USDT:USDT", "4h")]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        cw = self.compression_window
        hw = self.compression_half_window
        pw = self.pretrend_window

        dataframe["atr"] = self._atr(dataframe, self.atr_period_1h)
        dataframe["atr_ref"] = dataframe["atr"].shift(1)
        dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]
        dataframe["volume_ma20"] = dataframe["volume"].shift(1).rolling(self.volume_ma_window_1h).mean()
        dataframe["vol_ok"] = dataframe["volume"] > dataframe["volume_ma20"] * self.volume_breakout_multiplier

        dataframe["compression_high"] = dataframe["high"].shift(1).rolling(cw).max()
        dataframe["compression_low"] = dataframe["low"].shift(1).rolling(cw).min()
        dataframe["compression_width"] = dataframe["compression_high"] - dataframe["compression_low"]
        dataframe["compression_width_pct"] = dataframe["compression_width"] / dataframe["close"]
        dataframe["compression_ok"] = dataframe["compression_width"] < dataframe["atr_ref"] * self.compression_atr_multiplier
        dataframe["breakout_short"] = dataframe["close"] < dataframe["compression_low"] * (1 - self.breakout_buffer)

        dataframe["high_max_first_half"] = dataframe["high"].shift(hw + 1).rolling(hw).max()
        dataframe["high_max_last_half"] = dataframe["high"].shift(1).rolling(hw).max()
        dataframe["close_mean_first_half"] = dataframe["close"].shift(hw + 1).rolling(hw).mean()
        dataframe["close_mean_last_half"] = dataframe["close"].shift(1).rolling(hw).mean()
        dataframe["center_down"] = (
            (dataframe["high_max_last_half"] < dataframe["high_max_first_half"])
            & (dataframe["close_mean_last_half"] < dataframe["close_mean_first_half"])
        )

        dataframe["return_24h"] = dataframe["close"].shift(1) / dataframe["close"].shift(pw + 1) - 1
        dataframe["atr_pct_24h"] = dataframe["atr_pct"].shift(1).rolling(pw).mean()
        dataframe["pretrend_threshold"] = np.maximum(0.02, 1.5 * dataframe["atr_pct_24h"])
        dataframe["pretrend_down"] = dataframe["return_24h"] < -dataframe["pretrend_threshold"]

        dataframe["recent_low_24"] = dataframe["low"].shift(1).rolling(pw).min()
        dataframe["pullback_high_12"] = dataframe["high"].shift(1).rolling(cw).max()
        dataframe["pullback_depth_short"] = (dataframe["pullback_high_12"] - dataframe["recent_low_24"]) / dataframe["recent_low_24"]
        dataframe["pullback_seen_short"] = dataframe["pullback_depth_short"].between(
            self.pullback_min_depth,
            self.pullback_max_depth,
        )
        dataframe["near_low_zone"] = dataframe["compression_high"] <= dataframe["recent_low_24"] * self.low_zone_buffer

        candle_range = dataframe["high"] - dataframe["low"]
        dataframe["body_pct_of_range"] = (dataframe["close"] - dataframe["open"]).abs() / candle_range.replace(0, np.nan)
        dataframe["close_position"] = (dataframe["close"] - dataframe["low"]) / candle_range.replace(0, np.nan)
        dataframe["candle_quality_short"] = (
            (candle_range > 0)
            & (dataframe["body_pct_of_range"] >= self.candle_body_min)
            & (dataframe["close_position"] <= self.short_close_position_max)
        )

        dataframe["short_compression_stop"] = dataframe["compression_high"] + self.stop_atr_buffer * dataframe["atr_ref"]
        dataframe["short_pullback_stop"] = dataframe["pullback_high_12"] + self.stop_atr_buffer * dataframe["atr_ref"]
        dataframe = dataframe.copy()
        dataframe["short_compression_risk_pct"] = (dataframe["short_compression_stop"] - dataframe["close"]) / dataframe["close"]
        dataframe["short_pullback_risk_pct"] = (dataframe["short_pullback_stop"] - dataframe["close"]) / dataframe["close"]
        dataframe["short_compression_risk_pct_ok"] = dataframe["short_compression_risk_pct"].between(
            self.min_stop_distance,
            self.max_stop_distance,
        )
        dataframe["short_pullback_risk_pct_ok"] = dataframe["short_pullback_risk_pct"].between(
            self.min_stop_distance,
            self.max_stop_distance,
        )

        dataframe["btc_filter_short_ok"] = True
        if self.use_btc_filter and self.dp and metadata["pair"] != "BTC/USDT:USDT":
            btc_4h = self.dp.get_pair_dataframe(pair="BTC/USDT:USDT", timeframe="4h")
            if btc_4h is not None and not btc_4h.empty:
                btc_4h = self._add_4h_trend(btc_4h.copy())
                dataframe = self._merge_btc_context(dataframe, btc_4h)
                dataframe["btc_filter_short_ok"] = ~dataframe["btc_trend_up_4h"].fillna(False)

        dataframe["enter_initial_stop"] = np.nan
        dataframe["enter_risk_pct"] = np.nan
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if metadata["pair"] not in self.trade_pair_allowlist:
            return dataframe

        trend_down = dataframe.get("trend_down_4h", pd.Series(False, index=dataframe.index)).fillna(False)
        ema50_4h = dataframe.get("ema50_4h", pd.Series(np.nan, index=dataframe.index))
        btc_filter = dataframe.get("btc_filter_short_ok", pd.Series(True, index=dataframe.index)).fillna(True)
        pullback_intact_short = dataframe["pullback_high_12"] <= ema50_4h * 1.01
        base_filter = (
            trend_down
            & dataframe["compression_ok"]
            & dataframe["center_down"]
            & dataframe["breakout_short"]
            & dataframe["vol_ok"]
            & dataframe["candle_quality_short"]
            & btc_filter
            & (dataframe["volume"] > 0)
        )

        short_pullback_restart = (
            self.enable_short_pullback_restart
            & base_filter
            & dataframe["pullback_seen_short"]
            & pullback_intact_short
            & dataframe["short_pullback_risk_pct_ok"]
        )
        short_compression_breakdown = (
            self.enable_short_compression_breakdown
            & base_filter
            & dataframe["pretrend_down"]
            & dataframe["near_low_zone"]
            & dataframe["short_compression_risk_pct_ok"]
        )

        dataframe.loc[short_pullback_restart, ["enter_short", "enter_tag"]] = (1, "short_pullback_restart")
        dataframe.loc[short_pullback_restart, "enter_initial_stop"] = dataframe.loc[
            short_pullback_restart,
            "short_pullback_stop",
        ]
        dataframe.loc[short_pullback_restart, "enter_risk_pct"] = dataframe.loc[
            short_pullback_restart,
            "short_pullback_risk_pct",
        ]

        dataframe.loc[short_compression_breakdown, ["enter_short", "enter_tag"]] = (1, "short_compression_breakdown")
        dataframe.loc[short_compression_breakdown, "enter_initial_stop"] = dataframe.loc[
            short_compression_breakdown,
            "short_compression_stop",
        ]
        dataframe.loc[short_compression_breakdown, "enter_risk_pct"] = dataframe.loc[
            short_compression_breakdown,
            "short_compression_risk_pct",
        ]
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def _current_candle(self, pair: str) -> Optional[pd.Series]:
        if not self.dp:
            return None
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None
        return dataframe.iloc[-1]

    def _entry_candle(self, pair: str, trade: Trade) -> Optional[pd.Series]:
        if not self.dp:
            return None
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None
        trade_time = pd.Timestamp(trade.open_date_utc)
        if trade_time.tzinfo is None:
            trade_time = trade_time.tz_localize("UTC")
        candidates = dataframe[dataframe["date"] <= trade_time]
        if candidates.empty:
            return None
        return candidates.iloc[-1]

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: Optional[float],
        max_stake: float,
        leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        candle = self._current_candle(pair)
        if candle is None:
            return 0.0
        risk_pct = float(candle.get("enter_risk_pct", np.nan))
        initial_stop = float(candle.get("enter_initial_stop", np.nan))
        if (
            not np.isfinite(risk_pct)
            or not np.isfinite(initial_stop)
            or risk_pct <= 0
            or risk_pct < self.min_stop_distance
            or risk_pct > self.max_stop_distance
        ):
            return 0.0

        if self.wallets:
            account_equity = float(self.wallets.get_total_stake_amount())
        else:
            account_equity = proposed_stake * max(1, self.max_open_trades)
        risk_capital = account_equity * self.risk_per_trade
        position_value_by_risk = risk_capital / risk_pct
        position_value_cap = account_equity * self.max_position_value_pct
        stake = min(position_value_by_risk, position_value_cap, max_stake)
        if min_stake is not None and stake < min_stake:
            return 0.0
        return max(0.0, stake)

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
        candle = self._entry_candle(pair, trade)
        if candle is None:
            return self.stoploss
        tag = trade.enter_tag or ""
        stop_col = "short_compression_stop" if tag == "short_compression_breakdown" else "short_pullback_stop"
        initial_stop = float(candle.get(stop_col, np.nan))
        capped_stop = trade.open_rate * (1 + self.max_stop_distance)
        stop_price = capped_stop if not np.isfinite(initial_stop) else min(initial_stop, capped_stop)
        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=True,
            leverage=trade.leverage,
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
        candle = self._current_candle(pair)
        if candle is None:
            return None

        age = current_time - trade.open_date_utc
        if age > timedelta(hours=72) and current_profit < 0:
            return "stale_loss_72h"
        if age > timedelta(hours=120) and current_profit < 0.01:
            return "stale_flat_120h"
        if age > timedelta(hours=240) and current_profit < 0.03:
            return "stale_low_profit_240h"

        if bool(candle.get("trend_up_4h", False)) and current_profit < 0.03:
            return "trend_flip_short"
        return None

    def leverage(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        return min(self.leverage_value, max_leverage)


class DualTrendCompressionRestartShortPullbackOnlyV1Strategy(DualTrendCompressionRestartShortV1Strategy):
    """
    Backtest helper that keeps only short_pullback_restart entries enabled.
    """

    enable_short_compression_breakdown = False


class DualTrendCompressionRestartShortCompressionOnlyV1Strategy(DualTrendCompressionRestartShortV1Strategy):
    """
    Backtest helper that keeps only short_compression_breakdown entries enabled.
    """

    enable_short_pullback_restart = False
