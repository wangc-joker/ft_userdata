from typing import Any

import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade

from CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy import (
    CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9AdaptiveGovernedStrategy(
    CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy
):
    """
    Add 3 higher-level layers on top of the current Top9 candidate:
    1. market regime bias
    2. pair-specific branch governance
    3. adaptive branch risk throttling using recent trade outcomes
    """

    pair_branch_multipliers = {
        ("BTC/USDT:USDT", "long_1d_center_compression"): 1.10,
        ("SOL/USDT:USDT", "long_1d_center_compression"): 1.12,
        ("BNB/USDT:USDT", "long_1d_center_compression"): 1.08,
        ("ZEC/USDT:USDT", "short_1d_center_compression"): 1.10,
        ("ADA/USDT:USDT", "short_1d_center_compression"): 1.08,
        ("TRX/USDT:USDT", "short_1d_center_compression"): 1.05,
        ("XRP/USDT:USDT", "short_1h_center"): 1.08,
        ("DOGE/USDT:USDT", "short_1d_center_compression"): 0.90,
        ("DOGE/USDT:USDT", "short_1h_center"): 0.75,
        ("ETH/USDT:USDT", "long_1d_center_compression"): 0.88,
        ("ETH/USDT:USDT", "short_1h_center"): 0.92,
        ("XRP/USDT:USDT", "long_1d_center_compression"): 0.82,
        ("TRX/USDT:USDT", "long_1d_center_compression"): 0.80,
        ("ADA/USDT:USDT", "long_1d_center_compression"): 0.90,
    }

    pair_blocked_tags = {
        ("DOGE/USDT:USDT", "long_1d_center_compression"),
    }

    @staticmethod
    def _is_true(value: Any) -> bool:
        return bool(value is True or value == 1)

    def _market_regime(self, candle: pd.Series) -> str:
        close_1d = candle.get("close_1d")
        ema_fast_1d = candle.get("ema_fast_1d")
        ema_slow_1d = candle.get("ema_slow_1d")
        rsi_1d = candle.get("rsi_1d")

        if any(pd.isna(v) for v in [close_1d, ema_fast_1d, ema_slow_1d, rsi_1d]):
            return "neutral"

        bullish = (
            close_1d > ema_fast_1d > ema_slow_1d
            and float(rsi_1d) >= 57
            and self._is_true(candle.get("ema_slow_slope_up_1d"))
        )
        bearish = (
            close_1d < ema_fast_1d < ema_slow_1d
            and float(rsi_1d) <= 45
            and self._is_true(candle.get("ema_slow_slope_down_1d"))
        )

        if bullish:
            return "bull"
        if bearish:
            return "bear"
        return "neutral"

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        regime_bull = (
            (dataframe["close_1d"] > dataframe["ema_fast_1d"])
            & (dataframe["ema_fast_1d"] > dataframe["ema_slow_1d"])
            & (dataframe["rsi_1d"] >= 57)
            & self._bool_series(dataframe, "ema_slow_slope_up_1d")
        )
        regime_bear = (
            (dataframe["close_1d"] < dataframe["ema_fast_1d"])
            & (dataframe["ema_fast_1d"] < dataframe["ema_slow_1d"])
            & (dataframe["rsi_1d"] <= 45)
            & self._bool_series(dataframe, "ema_slow_slope_down_1d")
        )
        regime_neutral = ~(regime_bull | regime_bear)

        # Market state layer: avoid obvious counter-regime trades and make the noisy
        # hourly short branch harder to trigger in neutral conditions.
        dataframe.loc[
            dataframe.get("enter_tag", "").eq("long_1d_center_compression") & regime_bear,
            ["enter_long", "enter_tag"],
        ] = (0, None)

        dataframe.loc[
            dataframe.get("enter_tag", "").eq("short_1d_center_compression") & regime_bull,
            ["enter_short", "enter_tag"],
        ] = (0, None)

        neutral_short_filter = (
            dataframe.get("enter_tag", "").eq("short_1h_center")
            & regime_neutral
            & (
                ~self._bool_series(dataframe, "daily_momentum_short_1d")
                | (dataframe["close"] > dataframe["ema_fast"])
                | (dataframe["atr_pct"] < dataframe["atr_pct"].rolling(24).median().fillna(0))
            )
        )
        dataframe.loc[neutral_short_filter, ["enter_short", "enter_tag"]] = (0, None)

        # Pair governance layer.
        pair = metadata["pair"]
        for blocked_pair, blocked_tag in self.pair_blocked_tags:
            if pair == blocked_pair:
                is_long = blocked_tag.startswith("long_")
                dataframe.loc[
                    dataframe.get("enter_tag", "").eq(blocked_tag),
                    ["enter_long" if is_long else "enter_short", "enter_tag"],
                ] = (0, None)

        return dataframe

    def _adaptive_tag_multiplier(self, entry_tag: str | None, current_time) -> float:
        if not entry_tag:
            return 1.0

        closed_trades = [
            trade
            for trade in Trade.get_trades_proxy(is_open=False)
            if trade.close_date_utc
            and trade.close_date_utc <= current_time
            and (trade.enter_tag or "") == entry_tag
        ]
        closed_trades.sort(key=lambda trade: trade.close_date_utc, reverse=True)

        sample = closed_trades[:6]
        if len(sample) < 4:
            return 1.0

        recent_profit = sum((trade.close_profit or 0.0) for trade in sample)
        last_three = sample[:3]
        loss_streak = len(last_three) == 3 and all((trade.close_profit or 0.0) < 0 for trade in last_three)

        if loss_streak:
            return 0.55
        if recent_profit < -0.03:
            return 0.72
        if recent_profit < 0:
            return 0.85
        return 1.0

    def _adaptive_pair_multiplier(self, pair: str, current_time) -> float:
        closed_trades = [
            trade
            for trade in Trade.get_trades_proxy(is_open=False)
            if trade.close_date_utc and trade.close_date_utc <= current_time and trade.pair == pair
        ]
        closed_trades.sort(key=lambda trade: trade.close_date_utc, reverse=True)

        sample = closed_trades[:5]
        if len(sample) < 4:
            return 1.0

        recent_profit = sum((trade.close_profit or 0.0) for trade in sample)
        if recent_profit < -0.04:
            return 0.82
        if recent_profit < 0:
            return 0.92
        return 1.0

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        stake = super().custom_stake_amount(
            pair=pair,
            current_time=current_time,
            current_rate=current_rate,
            proposed_stake=proposed_stake,
            min_stake=min_stake,
            max_stake=max_stake,
            leverage=leverage,
            entry_tag=entry_tag,
            side=side,
            **kwargs,
        )

        if not self.dp:
            return stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return stake

        candle = dataframe.iloc[-1]
        regime = self._market_regime(candle)

        regime_multiplier = 1.0
        if entry_tag == "long_1d_center_compression":
            if regime == "bull":
                regime_multiplier = 1.10
            elif regime == "neutral":
                regime_multiplier = 0.95
            else:
                regime_multiplier = 0.70
        elif entry_tag == "short_1d_center_compression":
            if regime == "bear":
                regime_multiplier = 1.08
            elif regime == "neutral":
                regime_multiplier = 0.95
            else:
                regime_multiplier = 0.72
        elif entry_tag == "short_1h_center":
            if regime == "bear":
                regime_multiplier = 1.0
            elif regime == "neutral":
                regime_multiplier = 0.82
            else:
                regime_multiplier = 0.60

        pair_branch_multiplier = self.pair_branch_multipliers.get((pair, entry_tag or ""), 1.0)
        adaptive_tag_multiplier = self._adaptive_tag_multiplier(entry_tag, current_time)
        adaptive_pair_multiplier = self._adaptive_pair_multiplier(pair, current_time)

        stake *= regime_multiplier
        stake *= pair_branch_multiplier
        stake *= adaptive_tag_multiplier
        stake *= adaptive_pair_multiplier

        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)
