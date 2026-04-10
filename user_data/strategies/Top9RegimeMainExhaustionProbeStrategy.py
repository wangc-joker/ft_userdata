from pandas import DataFrame

from Top9RegimeMainBreakoutProbeStrategy import Top9RegimeMainBreakoutProbeStrategy


class Top9RegimeMainExhaustionProbeStrategy(Top9RegimeMainBreakoutProbeStrategy):
    """
    Add a bear-exhaustion state:
    - daily downtrend has weakened after a large decline
    - daily price stops making lower lows and the trading center lifts
    - hourly breakout longs are only allowed in core pairs when this state exists
    - hourly shorts are de-risked while exhaustion is active
    """

    breakout_core_pairs = {
        "BTC/USDT:USDT",
        "SOL/USDT:USDT",
        "BNB/USDT:USDT",
        "ZEC/USDT:USDT",
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_indicators(dataframe, metadata)

        dataframe["daily_low_7"] = dataframe["low_1d"].rolling(7).min()
        dataframe["daily_low_prev_7"] = dataframe["daily_low_7"].shift(7)
        dataframe["daily_high_7"] = dataframe["high_1d"].rolling(7).max()
        dataframe["daily_center_5"] = (
            (dataframe["high_1d"] + dataframe["low_1d"] + dataframe["close_1d"]) / 3.0
        ).rolling(5).mean()
        dataframe["daily_center_10"] = dataframe["daily_center_5"].shift(5)
        dataframe["daily_not_making_new_lows"] = (
            dataframe["daily_low_7"] >= dataframe["daily_low_prev_7"] * 0.995
        )
        dataframe["daily_center_lifting"] = (
            dataframe["daily_center_5"] > dataframe["daily_center_10"] * 1.01
        )
        dataframe["daily_reclaim_slow"] = dataframe["close_1d"] >= dataframe["ema_slow_1d"] * 0.99
        dataframe["daily_bounce_from_low"] = (
            dataframe["close_1d"] >= dataframe["daily_low_7"] * 1.05
        )
        dataframe["daily_rsi_recovery"] = dataframe["rsi_1d"] >= 46
        dataframe["daily_not_breaking_down"] = (
            dataframe["close_1d"] >= dataframe["daily_low_7"] * 1.01
        )

        dataframe["bear_exhaustion_1d"] = (
            dataframe["daily_not_making_new_lows"].eq(True)
            & dataframe["daily_center_lifting"].eq(True)
            & dataframe["daily_bounce_from_low"].eq(True)
            & dataframe["daily_rsi_recovery"].eq(True)
            & dataframe["daily_not_breaking_down"].eq(True)
            & ~dataframe["downtrend_1d"].eq(True)
            | (
                dataframe["downtrend_1d"].eq(True)
                & dataframe["daily_not_making_new_lows"].eq(True)
                & dataframe["daily_center_lifting"].eq(True)
                & dataframe["daily_bounce_from_low"].eq(True)
                & dataframe["daily_rsi_recovery"].eq(True)
                & dataframe["daily_reclaim_slow"].eq(True)
            )
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        if metadata["pair"] not in self.breakout_core_pairs:
            block_breakout = dataframe["enter_tag"].eq("long_1h_highbase_breakout")
            dataframe.loc[block_breakout, ["enter_long", "enter_tag"]] = (0, None)

        return dataframe

    def custom_stake_amount(
        self,
        pair: str,
        current_time,
        current_rate: float,
        proposed_stake: float,
        min_stake,
        max_stake: float,
        leverage: float,
        entry_tag,
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

        if candle.get("bear_exhaustion_1d", False):
            if entry_tag == "short_1h_center":
                stake *= 0.72
            elif entry_tag == "short_1d_center_compression":
                stake *= 0.82
            elif entry_tag == "long_1h_highbase_breakout":
                stake *= 1.08

        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

    def custom_stoploss(
        self,
        pair: str,
        trade,
        current_time,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ):
        if (trade.enter_tag or "") == "long_1h_highbase_breakout" and self.dp:
            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if not dataframe.empty:
                candle = dataframe.iloc[-1]
                center_floor = candle.get("trade_floor_6")
                hard_stop = trade.open_rate * 0.98
                stop_price = hard_stop
                if center_floor is not None and center_floor == center_floor:
                    stop_price = max(float(center_floor), hard_stop)
                from freqtrade.strategy import stoploss_from_absolute

                return stoploss_from_absolute(
                    stop_price,
                    current_rate,
                    is_short=trade.is_short,
                    leverage=trade.leverage,
                )

        return super().custom_stoploss(
            pair=pair,
            trade=trade,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit,
            after_fill=after_fill,
            **kwargs,
        )
