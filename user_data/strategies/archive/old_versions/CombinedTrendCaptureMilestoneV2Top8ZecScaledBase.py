from typing import Optional

import pandas as pd
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import stoploss_from_absolute

from CombinedTrendCaptureOptStrategy import CombinedTrendCaptureOptStrategy


class CombinedTrendCaptureMilestoneV2Top8ZecScaledBase(CombinedTrendCaptureOptStrategy):
    allowed_pairs = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "XRP/USDT:USDT",
        "ADA/USDT:USDT",
        "TRX/USDT:USDT",
        "ZEC/USDT:USDT",
    }

    higher_timeframe = "1d"
    higher_suffix = "_1d"
    base_tag = "1h"
    higher_tag = "1d"

    stake_multipliers = {
        "long_1d_center_compression": 1.35,
        "short_1d_center_compression": 1.15,
        "short_1h_center": 0.80,
    }

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
        multiplier = self.stake_multipliers.get(entry_tag or "", 1.0)
        weighted_stake = proposed_stake * multiplier
        if min_stake is not None:
            weighted_stake = max(weighted_stake, min_stake)
        return min(weighted_stake, max_stake)

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if metadata["pair"] not in self.allowed_pairs:
            return dataframe

        suffix = self.higher_suffix
        hourly_long_context = (
            self._bool_series(dataframe, f"restart_ready_long{suffix}")
            & self._bool_series(dataframe, f"daily_momentum_long{suffix}")
        )
        hourly_short_context = self._bool_series(dataframe, f"restart_ready_short{suffix}")
        triangle_long = self._bool_series(dataframe, "triangle_breakout_long")
        compression_long = self._bool_series(dataframe, "compression_breakout_long")
        center_short = self._bool_series(dataframe, "center_breakout_short")
        compression_short = self._bool_series(dataframe, "compression_breakout_short")
        triangle_long_htf = self._bool_series(dataframe, f"triangle_breakout_long{suffix}")
        center_long_htf = self._bool_series(dataframe, f"center_breakout_long{suffix}")
        triangle_short_htf = self._bool_series(dataframe, f"triangle_breakout_short{suffix}")
        center_short_htf = self._bool_series(dataframe, f"center_breakout_short{suffix}")
        htf_long_context = self._bool_series(dataframe, f"restart_ready_long{suffix}")
        htf_short_context = self._bool_series(dataframe, f"restart_ready_short{suffix}")

        htf_long_signal = htf_long_context & (triangle_long_htf | center_long_htf)
        htf_short_signal = htf_short_context & (triangle_short_htf | center_short_htf)

        htf_long_trigger = htf_long_signal & ~htf_long_signal.shift(1).eq(True)
        htf_short_trigger = htf_short_signal & ~htf_short_signal.shift(1).eq(True)

        strong_hourly_long_triangle = (
            hourly_long_context
            & triangle_long
            & self._bool_series(dataframe, "range_tight")
            & self._bool_series(dataframe, "ema_slow_slope_up")
            & (dataframe["rsi"] > int(self.hourly_long_rsi.value))
            & self._bool_series(dataframe, f"breakout_above_recent{suffix}")
        )

        if bool(self.enable_long_1h_triangle.value):
            dataframe.loc[
                strong_hourly_long_triangle,
                ["enter_long", "enter_tag"],
            ] = (1, f"long_{self.base_tag}_triangle")

        if bool(self.enable_long_1d_triangle.value):
            dataframe.loc[
                htf_long_trigger & triangle_long_htf,
                ["enter_long", "enter_tag"],
            ] = (1, f"long_{self.higher_tag}_triangle")

        if bool(self.enable_long_1d_center.value):
            dataframe.loc[
                htf_long_trigger & center_long_htf,
                ["enter_long", "enter_tag"],
            ] = (1, f"long_{self.higher_tag}_center_compression")

        if bool(self.enable_short_1h_center.value):
            dataframe.loc[
                hourly_short_context & center_short,
                ["enter_short", "enter_tag"],
            ] = (1, f"short_{self.base_tag}_center")

        if bool(self.enable_short_1h_compression.value):
            dataframe.loc[
                hourly_short_context & compression_short,
                ["enter_short", "enter_tag"],
            ] = (1, f"short_{self.base_tag}_compression")

        if bool(self.enable_short_1d_triangle.value):
            dataframe.loc[
                htf_short_trigger & triangle_short_htf,
                ["enter_short", "enter_tag"],
            ] = (1, f"short_{self.higher_tag}_triangle")

        if bool(self.enable_short_1d_center.value):
            dataframe.loc[
                htf_short_trigger & center_short_htf,
                ["enter_short", "enter_tag"],
            ] = (1, f"short_{self.higher_tag}_center_compression")

        short_quality = (
            self._bool_series(dataframe, f"daily_momentum_short{suffix}")
            & self._bool_series(dataframe, f"ema_slow_slope_down{suffix}")
            & (dataframe["close"] < dataframe["ema_fast"])
            & (dataframe[f"close{suffix}"] < dataframe[f"ema_fast{suffix}"])
        )

        low_quality_short = dataframe.get("enter_tag", "").eq(f"short_{self.base_tag}_center") & ~short_quality
        dataframe.loc[low_quality_short, ["enter_short", "enter_tag"]] = (0, None)

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
        if not self.dp:
            return self.stoploss

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return self.stoploss

        candle = dataframe.iloc[-1]
        tag = trade.enter_tag or ""
        is_higher_scope = f"_{self.higher_tag}_" in tag
        suffix = self.higher_suffix if is_higher_scope else ""

        if trade.is_short:
            structure_stop = candle.get(f"structure_stop_short{suffix}")
            capped_stop = trade.open_rate * 1.02
            stop_price = capped_stop
            if pd.notna(structure_stop):
                stop_price = min(float(structure_stop), capped_stop)
        else:
            structure_stop = candle.get(f"structure_stop_long{suffix}")
            capped_stop = trade.open_rate * 0.98
            stop_price = capped_stop
            if pd.notna(structure_stop):
                stop_price = max(float(structure_stop), capped_stop)

        return stoploss_from_absolute(
            stop_price,
            current_rate,
            is_short=trade.is_short,
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
        if not self.dp:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe.empty:
            return None

        candle = dataframe.iloc[-1]
        tag = trade.enter_tag or ""
        is_higher_scope = f"_{self.higher_tag}_" in tag
        suffix = self.higher_suffix if is_higher_scope else ""
        scope = self.higher_tag if is_higher_scope else self.base_tag

        stop_long = candle.get(f"structure_stop_long{suffix}")
        stop_short = candle.get(f"structure_stop_short{suffix}")

        if trade.is_short:
            if bool(candle.get(f"uptrend{self.higher_suffix}", False)):
                return f"trend_flip_short_{self.higher_tag}"
            if is_higher_scope:
                if bool(candle.get(f"center_up{self.higher_suffix}", False)) and candle["close"] > candle.get(
                    f"ema_fast{self.higher_suffix}", candle["close"]
                ):
                    return f"structural_exit_short_{self.higher_tag}"
            else:
                if bool(candle.get("center_up", False)) and candle["close"] > candle.get("ema_fast", candle["close"]):
                    return f"structural_exit_short_{self.base_tag}"

            if pd.notna(stop_short) and candle["close"] > stop_short:
                return f"swing_exit_short_{scope}"
            return None

        if bool(candle.get(f"downtrend{self.higher_suffix}", False)):
            return f"trend_flip_long_{self.higher_tag}"
        if is_higher_scope:
            if bool(candle.get(f"center_down{self.higher_suffix}", False)) and candle["close"] < candle.get(
                f"ema_fast{self.higher_suffix}", candle["close"]
            ):
                return f"structural_exit_long_{self.higher_tag}"
        else:
            if bool(candle.get("center_down", False)) and candle["close"] < candle.get("ema_fast", candle["close"]):
                return f"structural_exit_long_{self.base_tag}"

        if pd.notna(stop_long) and candle["close"] < stop_long:
            return f"swing_exit_long_{scope}"

        return None
