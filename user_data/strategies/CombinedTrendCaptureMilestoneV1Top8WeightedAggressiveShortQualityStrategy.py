from pandas import DataFrame

from CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy import (
    CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy,
)


class CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveShortQualityStrategy(
    CombinedTrendCaptureMilestoneV1Top8WeightedAggressiveStrategy
):
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        short_quality = (
            self._bool_series(dataframe, "daily_momentum_short_1d")
            & self._bool_series(dataframe, "ema_slow_slope_down_1d")
            & (dataframe["close"] < dataframe["ema_fast"])
            & (dataframe["close_1d"] < dataframe["ema_fast_1d"])
        )

        low_quality_short = dataframe.get("enter_tag", "").eq("short_1h_center") & ~short_quality
        dataframe.loc[low_quality_short, ["enter_short", "enter_tag"]] = (0, None)

        return dataframe
