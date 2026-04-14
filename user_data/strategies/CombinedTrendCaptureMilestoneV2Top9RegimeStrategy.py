from typing import Optional

import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade

from CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy import (
    CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy,
)
from core.market_state.regime import classify_daily_regime, classify_intraday_regime, recent_trade_multiplier


class CombinedTrendCaptureMilestoneV2Top9RegimeStrategy(
    CombinedTrendCaptureMilestoneV2Top9DogeLiteStrategy
):
    """
    Internal regime base:
    - classify bull / bear / range from 1d structure
    - bias stake weights by market state
    - optionally support range mean-reversion entries in child strategies
    """

    core_bull_pairs = {"BTC/USDT:USDT", "SOL/USDT:USDT", "BNB/USDT:USDT", "ZEC/USDT:USDT"}

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        bull, bear, _ = classify_daily_regime(dataframe)
        tags = dataframe["enter_tag"].fillna("")

        weak_bull_short = tags.eq("short_1h_center") & bull & ~dataframe["daily_momentum_short_1d"].eq(True)
        dataframe.loc[weak_bull_short, ["enter_short", "enter_tag"]] = (0, None)

        weak_bear_long = (
            tags.eq("long_1d_center_compression")
            & bear
            & ~dataframe["daily_momentum_long_1d"].eq(True)
        )
        dataframe.loc[weak_bear_long, ["enter_long", "enter_tag"]] = (0, None)

        return dataframe

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
        bull, bear, _ = classify_intraday_regime(candle)

        multiplier = 1.0
        if entry_tag == "long_1d_center_compression":
            multiplier *= 1.12 if bull else (0.86 if bear else 0.94)
            if pair in self.core_bull_pairs:
                multiplier *= 1.05
            elif pair in {"ETH/USDT:USDT", "XRP/USDT:USDT", "ADA/USDT:USDT", "TRX/USDT:USDT"}:
                multiplier *= 0.95
        elif entry_tag == "short_1d_center_compression":
            multiplier *= 1.12 if bear else (0.86 if bull else 0.95)
            if pair == "DOGE/USDT:USDT":
                multiplier *= 0.88
        elif entry_tag == "short_1h_center":
            multiplier *= 1.04 if bear else (0.76 if bull else 0.88)
            if pair == "DOGE/USDT:USDT":
                multiplier *= 0.88
            if pair == "ZEC/USDT:USDT":
                multiplier *= 0.94

        multiplier *= recent_trade_multiplier(current_time, entry_tag, pair)
        stake *= multiplier

        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        return super().custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            **kwargs,
        )
