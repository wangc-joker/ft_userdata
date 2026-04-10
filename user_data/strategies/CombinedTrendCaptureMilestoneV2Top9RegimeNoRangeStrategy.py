from pandas import DataFrame

from CombinedTrendCaptureMilestoneV2Top9RegimeStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeStrategy,
)


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeStrategy
):
    """
    Keep the bull/bear regime layer, but disable range-reversion entries.
    This isolates the value of the market-state logic itself.
    """

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)

        range_tags = dataframe["enter_tag"].fillna("").isin(
            {"long_range_1h_revert", "short_range_1h_revert"}
        )
        dataframe.loc[range_tags, ["enter_long", "enter_short", "enter_tag"]] = (0, 0, None)
        return dataframe
