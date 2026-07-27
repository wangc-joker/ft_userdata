from __future__ import annotations

from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, informative, stoploss_from_absolute


def _filled_bool(series: pd.Series, default: bool = False) -> pd.Series:
    """Normalize merged informative boolean columns without implicit downcasting."""
    return series.astype("boolean").fillna(default).astype(bool)


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
    max_entry_position_adjustment = 1

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
    breakeven_profit_threshold = 0.02
    breakeven_lock_profit = 0.001
    profit_lock_steps: tuple[tuple[float, float], ...] = ()
    partial_profit_steps: tuple[tuple[float, float], ...] = ()
    partial_trail_rules: tuple[tuple[float, float], ...] = ()
    partial_ladder_enabled = False
    partial_ladder_start_profit = 0.10
    partial_ladder_step_profit = 0.10
    partial_ladder_fraction = 0.50
    partial_ladder_fractions: tuple[float, ...] = ()
    partial_ladder_max_steps = 6
    partial_ladder_lock_first = 0.05
    partial_ladder_lock_step = 0.005
    partial_ladder_lock_max = 0.08
    partial_ladder_lock_values: tuple[float, ...] = ()
    partial_ladder_trail_gap_enabled = False
    partial_ladder_trail_gap_first = 0.05
    partial_ladder_trail_gap_step = 0.005
    partial_ladder_trail_gap_max = 0.10
    pyramiding_enabled = False
    pyramid_allowed_tags: tuple[str, ...] = ()
    pyramid_profit_threshold = 0.02
    pyramid_profit_cap = 0.05
    pyramid_stake_fraction = 0.50
    pyramid_max_additions = 1
    pyramid_use_structural_reinforcement = False
    pyramid_leg_breakeven_enabled = False
    pyramid_leg_breakeven_trigger_profit = 0.02
    pyramid_require_close_position_max: Optional[float] = None
    pyramid_require_body_pct_min: Optional[float] = None
    pyramid_require_ema20_distance_min: Optional[float] = None
    pyramid_reinforcement_require_volume = True
    pyramid_reinforcement_profit_floor = 0.008
    pyramid_reinforcement_profit_cap = 0.03
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
        dataframe["ema20_1h"] = self._ema(dataframe["close"], 20)
        dataframe["ema20_1h_prev"] = dataframe["ema20_1h"].shift(3)
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
                dataframe["btc_filter_short_ok"] = ~_filled_bool(dataframe["btc_trend_up_4h"])

        dataframe["short_reinforce_probe"] = (
            _filled_bool(dataframe.get("trend_down_4h", pd.Series(False, index=dataframe.index)))
            & _filled_bool(dataframe["center_down"])
            & (dataframe["close"] < dataframe["ema20_1h"])
            & (dataframe["ema20_1h"] < dataframe["ema20_1h_prev"])
            & (dataframe["close_position"] <= 0.55)
            & (dataframe["volume"] > 0)
        )

        dataframe["enter_initial_stop"] = np.nan
        dataframe["enter_risk_pct"] = np.nan
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if metadata["pair"] not in self.trade_pair_allowlist:
            return dataframe

        trend_down = _filled_bool(
            dataframe.get("trend_down_4h", pd.Series(False, index=dataframe.index))
        )
        ema50_4h = dataframe.get("ema50_4h", pd.Series(np.nan, index=dataframe.index))
        btc_filter = _filled_bool(
            dataframe.get("btc_filter_short_ok", pd.Series(True, index=dataframe.index)),
            default=True,
        )
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

    def _profit_lock_stop_price(self, trade: Trade, current_profit: float) -> Optional[float]:
        lock_profit = None
        for trigger_profit, locked_profit in sorted(self.profit_lock_steps, reverse=True):
            if current_profit >= trigger_profit:
                lock_profit = locked_profit
                break
        max_profit = current_profit
        if self.partial_trail_rules or self.partial_ladder_enabled:
            getter = getattr(trade, "get_custom_data", None)
            setter = getattr(trade, "set_custom_data", None)
            stored_max = getter(key="dualtrend_max_profit") if getter else None
            if stored_max is not None:
                max_profit = max(max_profit, float(stored_max))
            if setter:
                setter(key="dualtrend_max_profit", value=float(max_profit))
        if self.partial_trail_rules:
            for trigger_profit, trail_gap in sorted(self.partial_trail_rules, reverse=True):
                if max_profit >= trigger_profit:
                    trail_lock = max_profit - trail_gap
                    lock_profit = max(lock_profit or self.breakeven_lock_profit, trail_lock)
                    break
        if self.partial_ladder_enabled and max_profit >= self.partial_ladder_start_profit:
            ladder_steps = int(
                (max_profit - self.partial_ladder_start_profit)
                // self.partial_ladder_step_profit
            ) + 1
            ladder_steps = max(1, min(ladder_steps, self.partial_ladder_max_steps))
            if self.partial_ladder_trail_gap_enabled:
                trail_gap = self.partial_ladder_trail_gap_first + (
                    ladder_steps - 1
                ) * self.partial_ladder_trail_gap_step
                trail_gap = min(trail_gap, self.partial_ladder_trail_gap_max)
                ladder_lock = max_profit - trail_gap
            elif ladder_steps <= len(self.partial_ladder_lock_values):
                ladder_lock = self.partial_ladder_lock_values[ladder_steps - 1]
            else:
                ladder_lock = self.partial_ladder_lock_first + (ladder_steps - 1) * self.partial_ladder_lock_step
                ladder_lock = min(ladder_lock, self.partial_ladder_lock_max)
            lock_profit = max(lock_profit or self.breakeven_lock_profit, ladder_lock)
        if lock_profit is None:
            return None

        leverage = max(float(trade.leverage or 1.0), 1.0)
        price_move = lock_profit / leverage
        if trade.is_short:
            return trade.open_rate * (1 - price_move)
        return trade.open_rate * (1 + price_move)

    def _current_entry_signal_matches_trade(self, pair: str, trade: Trade) -> bool:
        candle = self._current_candle(pair)
        if candle is None:
            return False
        trade_tag = trade.enter_tag or ""
        candle_tag = candle.get("enter_tag", None)
        if candle_tag is None or trade_tag != str(candle_tag):
            return False
        if bool(getattr(trade, "is_short", False)):
            return bool(candle.get("enter_short", 0) == 1)
        return bool(candle.get("enter_long", 0) == 1)

    def _pyramid_extra_filters_pass(self, pair: str, trade: Trade) -> bool:
        candle = self._current_candle(pair)
        if candle is None:
            return False

        close_position_max = self.pyramid_require_close_position_max
        if close_position_max is not None:
            close_position = float(candle.get("close_position", np.nan))
            if not np.isfinite(close_position) or close_position > close_position_max:
                return False

        body_pct_min = self.pyramid_require_body_pct_min
        if body_pct_min is not None:
            body_pct = float(candle.get("body_pct_of_range", np.nan))
            if not np.isfinite(body_pct) or body_pct < body_pct_min:
                return False

        ema20_distance_min = self.pyramid_require_ema20_distance_min
        if ema20_distance_min is not None and bool(getattr(trade, "is_short", False)):
            close_price = float(candle.get("close", np.nan))
            ema20 = float(candle.get("ema20_1h", np.nan))
            if not np.isfinite(close_price) or not np.isfinite(ema20) or ema20 <= 0:
                return False
            ema20_distance = (ema20 - close_price) / ema20
            if ema20_distance < ema20_distance_min:
                return False

        return True

    def _manage_pyramid_leg_breakeven(
        self,
        trade: Trade,
        current_time,
        current_rate: float,
        min_stake: Optional[float],
    ) -> Optional[float]:
        if not self.pyramid_leg_breakeven_enabled:
            return None

        getter = getattr(trade, "get_custom_data", None)
        setter = getattr(trade, "set_custom_data", None)
        if getter is None or setter is None:
            return None

        additions_done = int(getter(key="dualtrend_pyramid_additions") or 0)
        if additions_done <= 0:
            return None

        for addition_index in range(1, additions_done + 1):
            addition_rate = getter(key=f"dualtrend_pyramid_addition_{addition_index}_rate")
            addition_stake = getter(key=f"dualtrend_pyramid_addition_{addition_index}_stake")
            if addition_rate is None or addition_stake is None:
                continue
            if getter(key=f"dualtrend_pyramid_addition_{addition_index}_breakeven_exited"):
                continue

            addition_rate = float(addition_rate)
            addition_stake = float(addition_stake)
            if addition_stake <= 0 or not np.isfinite(addition_rate) or addition_rate <= 0:
                continue

            if bool(getattr(trade, "is_short", False)):
                leg_profit = (addition_rate - current_rate) / addition_rate
                breakeven_reclaim = current_rate >= addition_rate
            else:
                leg_profit = (current_rate - addition_rate) / addition_rate
                breakeven_reclaim = current_rate <= addition_rate

            armed_key = f"dualtrend_pyramid_addition_{addition_index}_breakeven_armed"
            if not getter(key=armed_key) and leg_profit >= self.pyramid_leg_breakeven_trigger_profit:
                setter(key=armed_key, value=True)
                setter(
                    key=f"dualtrend_pyramid_addition_{addition_index}_breakeven_arm_time",
                    value=current_time.isoformat(),
                )
                setter(
                    key=f"dualtrend_pyramid_addition_{addition_index}_breakeven_arm_profit",
                    value=float(leg_profit),
                )

            if getter(key=armed_key) and breakeven_reclaim:
                stake_to_reduce = min(addition_stake, float(trade.stake_amount))
                if min_stake is not None and stake_to_reduce < min_stake:
                    continue
                setter(key=f"dualtrend_pyramid_addition_{addition_index}_breakeven_exited", value=True)
                setter(
                    key=f"dualtrend_pyramid_addition_{addition_index}_breakeven_exit_time",
                    value=current_time.isoformat(),
                )
                setter(
                    key=f"dualtrend_pyramid_addition_{addition_index}_breakeven_exit_rate",
                    value=float(current_rate),
                )
                return -stake_to_reduce

        return None

    def _short_pullback_reinforcement_signal(self, pair: str) -> bool:
        candle = self._current_candle(pair)
        if candle is None:
            return False

        if bool(candle.get("short_reinforce_probe", False)):
            return True

        trend_down = bool(candle.get("trend_down_4h", False))
        center_down = bool(candle.get("center_down", False))
        candle_quality = bool(candle.get("candle_quality_short", False))
        vol_ok = bool(candle.get("vol_ok", False))
        close_below_ema20 = bool(float(candle.get("close", np.nan)) < float(candle.get("ema20_1h", np.nan)))
        ema20_falling = bool(float(candle.get("ema20_1h", np.nan)) < float(candle.get("ema20_1h_prev", np.nan)))

        if self.pyramid_reinforcement_require_volume and not vol_ok:
            return False

        return bool(
            trend_down
            and center_down
            and candle_quality
            and close_below_ema20
            and ema20_falling
        )

    def _pyramid_stake_amount(
        self,
        trade: Trade,
        min_stake: Optional[float],
        max_stake: float,
    ) -> float:
        getter = getattr(trade, "get_custom_data", None)
        setter = getattr(trade, "set_custom_data", None)
        base_stake = None
        if getter is not None:
            stored = getter(key="dualtrend_initial_stake_amount")
            if stored is not None:
                base_stake = float(stored)
        if base_stake is None:
            base_stake = float(trade.stake_amount)
            if setter is not None:
                setter(key="dualtrend_initial_stake_amount", value=base_stake)

        stake = min(float(max_stake), base_stake * self.pyramid_stake_fraction)
        if min_stake is not None and stake < min_stake:
            return 0.0
        return max(0.0, stake)

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
        profit_lock_stop = self._profit_lock_stop_price(trade, current_profit)
        if profit_lock_stop is not None:
            stop_price = min(stop_price, profit_lock_stop)
        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=True,
            leverage=trade.leverage,
        )

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
    ) -> Optional[float]:
        getter = getattr(trade, "get_custom_data", None)
        setter = getattr(trade, "set_custom_data", None)
        if getter is None or setter is None:
            return None

        pyramid_leg_exit = self._manage_pyramid_leg_breakeven(
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            min_stake=min_stake,
        )
        if pyramid_leg_exit is not None:
            return pyramid_leg_exit

        if self.pyramiding_enabled:
            tag = trade.enter_tag or ""
            additions_done = int(getter(key="dualtrend_pyramid_additions") or 0)
            signal_matches = self._current_entry_signal_matches_trade(trade.pair, trade)
            if (
                additions_done < self.pyramid_max_additions
                and tag in self.pyramid_allowed_tags
                and current_profit >= self.pyramid_profit_threshold
                and current_profit <= self.pyramid_profit_cap
                and signal_matches
                and self._pyramid_extra_filters_pass(trade.pair, trade)
            ):
                stake_to_add = self._pyramid_stake_amount(
                    trade=trade,
                    min_stake=min_stake,
                    max_stake=max_stake,
                )
                if stake_to_add > 0:
                    next_addition = additions_done + 1
                    setter(key="dualtrend_pyramid_additions", value=next_addition)
                    setter(key=f"dualtrend_pyramid_addition_{next_addition}_time", value=current_time.isoformat())
                    setter(key=f"dualtrend_pyramid_addition_{next_addition}_profit", value=float(current_profit))
                    setter(key=f"dualtrend_pyramid_addition_{next_addition}_tag", value=tag)
                    setter(key=f"dualtrend_pyramid_addition_{next_addition}_rate", value=float(current_rate))
                    setter(key=f"dualtrend_pyramid_addition_{next_addition}_stake", value=float(stake_to_add))
                    return stake_to_add

        if not self.partial_profit_steps and not self.partial_ladder_enabled:
            return None

        if self.partial_ladder_enabled:
            done_steps = int(getter(key="dualtrend_ladder_done_steps") or 0)
            if done_steps >= self.partial_ladder_max_steps:
                return None
            trigger_profit = self.partial_ladder_start_profit + done_steps * self.partial_ladder_step_profit
            if current_profit >= trigger_profit:
                if done_steps < len(self.partial_ladder_fractions):
                    fraction = self.partial_ladder_fractions[done_steps]
                else:
                    fraction = self.partial_ladder_fraction
                stake_to_sell = float(trade.stake_amount) * fraction
                if min_stake is not None and fraction < 1.0 and stake_to_sell < min_stake:
                    return None
                next_steps = done_steps + 1
                setter(key="dualtrend_ladder_done_steps", value=next_steps)
                setter(key=f"dualtrend_ladder_step_{next_steps}_time", value=current_time.isoformat())
                setter(key=f"dualtrend_ladder_step_{next_steps}_profit", value=float(current_profit))
                return -stake_to_sell

        for trigger_profit, fraction in sorted(self.partial_profit_steps):
            key = f"dualtrend_partial_{trigger_profit:.4f}"
            if current_profit < trigger_profit or getter(key=key):
                continue
            stake_to_sell = float(trade.stake_amount) * fraction
            if min_stake is not None and stake_to_sell < min_stake:
                return None
            setter(key=key, value=True)
            setter(key=f"{key}_time", value=current_time.isoformat())
            setter(key=f"{key}_profit", value=float(current_profit))
            return -stake_to_sell

        return None

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
