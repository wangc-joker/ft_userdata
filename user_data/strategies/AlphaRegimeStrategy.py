import logging
from datetime import datetime
from typing import Optional

import talib.abstract as ta
from freqtrade.persistence import Trade
from freqtrade.strategy import merge_informative_pair
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

from alpha_modules.exit_manager import ExitManager
from alpha_modules.market_regime import MarketRegime
from alpha_modules.risk_manager import RiskManager
from alpha_modules.signals.trend_pullback import TrendPullbackSignal
from alpha_modules.state_store import StateStore


log = logging.getLogger(__name__)


class AlphaRegimeStrategy(IStrategy):
    """
    First runnable skeleton for the NFI Alpha project.

    Design intent:
    - Keep the strategy class as an orchestrator.
    - Put entry ideas into signal modules.
    - Put market/risk/exit decisions into dedicated modules.
    - Keep room for persistent runtime state and future FreqAI scoring.
    """

    INTERFACE_VERSION = 3

    timeframe = "5m"
    informative_timeframe = "1h"
    pair_context_timeframes = ["15m", "1h"]
    market_timeframes = ["1h", "4h"]
    startup_candle_count = 240
    process_only_new_candles = True

    can_short = True

    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = True

    minimal_roi = {
        "0": 100.0,
    }

    stoploss = -0.08
    trailing_stop = False

    def version(self) -> str:
        return "0.5.0"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.state_store = StateStore(namespace="alpha_regime")
        self.market_regime = MarketRegime()
        self.risk_manager = RiskManager()
        self.exit_manager = ExitManager()
        self.signal_modules = [
            TrendPullbackSignal(),
        ]

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        informative_pairs = [
            ("BTC/USDT:USDT", timeframe)
            for timeframe in self.market_timeframes
        ]
        for pair_context_timeframe in self.pair_context_timeframes:
            informative_pairs.extend([(pair, pair_context_timeframe) for pair in pairs])
        return informative_pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_20"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["ema_200"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi_14"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["atr_14"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["volume_mean_30"] = dataframe["volume"].rolling(30).mean()

        dataframe = self.market_regime.add_indicators(dataframe, metadata)
        for market_timeframe in self.market_timeframes:
            dataframe = self._merge_reference_market(dataframe, "BTC/USDT:USDT", "btc", market_timeframe)
        for pair_context_timeframe in self.pair_context_timeframes:
            dataframe = self._merge_pair_context(dataframe, metadata["pair"], pair_context_timeframe)
        dataframe = self.market_regime.add_market_context(dataframe, metadata)

        for signal in self.signal_modules:
            dataframe = signal.add_indicators(dataframe, metadata)

        dataframe = self.risk_manager.add_filters(dataframe, metadata)
        dataframe = self.exit_manager.add_indicators(dataframe, metadata)
        return dataframe

    def _merge_reference_market(self, dataframe: DataFrame, pair: str, prefix: str, timeframe: str) -> DataFrame:
        informative = self.dp.get_pair_dataframe(pair=pair, timeframe=timeframe)
        if informative.empty:
            return dataframe

        informative[f"{prefix}_close"] = informative["close"]
        informative[f"{prefix}_ema_50"] = ta.EMA(informative, timeperiod=50)
        informative[f"{prefix}_ema_200"] = ta.EMA(informative, timeperiod=200)
        informative[f"{prefix}_rsi_14"] = ta.RSI(informative, timeperiod=14)
        informative[f"{prefix}_roc_3"] = informative[f"{prefix}_close"].pct_change(3)
        informative[f"{prefix}_roc_12"] = informative[f"{prefix}_close"].pct_change(12)
        informative[f"{prefix}_regime_ok"] = (
            (informative[f"{prefix}_close"] > informative[f"{prefix}_ema_200"])
            & (informative[f"{prefix}_ema_50"] > informative[f"{prefix}_ema_200"])
            & (informative[f"{prefix}_rsi_14"] > 42)
        ).astype(int)
        informative[f"{prefix}_bear_regime"] = (
            (informative[f"{prefix}_close"] < informative[f"{prefix}_ema_200"])
            & (informative[f"{prefix}_ema_50"] < informative[f"{prefix}_ema_200"])
            & (informative[f"{prefix}_rsi_14"] < 58)
        ).astype(int)

        informative = informative[
            [
                "date",
                f"{prefix}_close",
                f"{prefix}_ema_50",
                f"{prefix}_ema_200",
                f"{prefix}_rsi_14",
                f"{prefix}_roc_3",
                f"{prefix}_roc_12",
                f"{prefix}_regime_ok",
                f"{prefix}_bear_regime",
            ]
        ]

        dataframe = merge_informative_pair(
            dataframe,
            informative,
            self.timeframe,
            timeframe,
            ffill=True,
        )

        informative_date_column = f"date_{timeframe}"
        if informative_date_column in dataframe.columns:
            dataframe = dataframe.drop(columns=[informative_date_column])

        return dataframe

    def _merge_pair_context(self, dataframe: DataFrame, pair: str, timeframe: str) -> DataFrame:
        informative = self.dp.get_pair_dataframe(pair=pair, timeframe=timeframe)
        if informative.empty:
            dataframe[f"pair_context_ok_{timeframe}"] = 1
            return dataframe

        informative["pair_close"] = informative["close"]
        informative["pair_ema_20"] = ta.EMA(informative, timeperiod=20)
        informative["pair_ema_50"] = ta.EMA(informative, timeperiod=50)
        informative["pair_ema_200"] = ta.EMA(informative, timeperiod=200)
        informative["pair_rsi_14"] = ta.RSI(informative, timeperiod=14)
        informative["pair_roc_3"] = informative["pair_close"].pct_change(3)
        informative["pair_roc_6"] = informative["pair_close"].pct_change(6)
        informative["pair_context_ok"] = (
            (informative["pair_close"] > informative["pair_ema_200"] * 0.97)
            & (informative["pair_rsi_14"] > 38)
            & (informative["pair_roc_3"] > -0.05)
        ).astype(int)

        informative = informative[
            [
                "date",
                "pair_close",
                "pair_ema_20",
                "pair_ema_50",
                "pair_ema_200",
                "pair_rsi_14",
                "pair_roc_3",
                "pair_roc_6",
                "pair_context_ok",
            ]
        ]

        dataframe = merge_informative_pair(
            dataframe,
            informative,
            self.timeframe,
            timeframe,
            ffill=True,
        )

        informative_date_column = f"date_{timeframe}"
        if informative_date_column in dataframe.columns:
            dataframe = dataframe.drop(columns=[informative_date_column])

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["enter_long"] = 0
        dataframe["enter_short"] = 0
        dataframe["enter_tag"] = ""
        dataframe["alpha_long_entry_priority"] = 0
        dataframe["alpha_long_entry_score"] = 0
        dataframe["alpha_short_entry_priority"] = 0
        dataframe["alpha_short_entry_score"] = 0

        for signal in self.signal_modules:
            dataframe = signal.generate_entry(dataframe, metadata)
            score_column = signal.score_column
            tag = signal.entry_tag
            priority = signal.priority
            min_score = signal.min_score

            long_entry_mask = (
                (dataframe[signal.long_signal_column] == 1)
                & (dataframe[score_column] >= min_score)
                & (dataframe["alpha_allow_long"] == 1)
                & (priority > dataframe["alpha_long_entry_priority"])
            )

            dataframe.loc[long_entry_mask, "enter_long"] = 1
            dataframe.loc[long_entry_mask, "enter_tag"] = tag
            dataframe.loc[long_entry_mask, "alpha_long_entry_priority"] = priority
            dataframe.loc[long_entry_mask, "alpha_long_entry_score"] = dataframe.loc[long_entry_mask, score_column]

            short_entry_mask = (
                (dataframe[signal.short_signal_column] == 1)
                & (dataframe[score_column] >= min_score)
                & (dataframe["alpha_allow_short"] == 1)
                & (priority > dataframe["alpha_short_entry_priority"])
            )

            dataframe.loc[short_entry_mask, "enter_short"] = 1
            dataframe.loc[short_entry_mask, "enter_tag"] = tag
            dataframe.loc[short_entry_mask, "alpha_short_entry_priority"] = priority
            dataframe.loc[short_entry_mask, "alpha_short_entry_score"] = dataframe.loc[short_entry_mask, score_column]

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        dataframe["exit_short"] = 0
        dataframe["exit_tag"] = ""

        long_exit_mask = self.exit_manager.vector_long_exit_mask(dataframe)
        dataframe.loc[long_exit_mask, "exit_long"] = 1
        dataframe.loc[long_exit_mask, "exit_tag"] = "alpha_vector_exit"

        short_exit_mask = self.exit_manager.vector_short_exit_mask(dataframe)
        dataframe.loc[short_exit_mask, "exit_short"] = 1
        dataframe.loc[short_exit_mask, "exit_tag"] = "alpha_vector_exit"
        return dataframe

    def custom_stake_amount(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_stake: float,
        min_stake: Optional[float],
        max_stake: float,
        leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
        if dataframe.empty:
            return proposed_stake

        last_candle = dataframe.iloc[-1]
        if side == "short":
            weight = float(last_candle.get("alpha_short_market_weight", 0.65))
        else:
            weight = float(last_candle.get("alpha_long_market_weight", 0.65))

        weighted_stake = proposed_stake * weight
        if min_stake is not None:
            weighted_stake = max(weighted_stake, min_stake)
        return min(weighted_stake, max_stake)

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> Optional[str]:
        return self.exit_manager.custom_exit(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            state_store=self.state_store,
        )
