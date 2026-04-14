from pandas import DataFrame

from CombinedTrendCaptureMilestoneV2Top9RegimeStrategy import (
    CombinedTrendCaptureMilestoneV2Top9RegimeStrategy,
)
from signals.filters import remove_range_reversion_entries


class CombinedTrendCaptureMilestoneV2Top9RegimeNoRangeStrategy(
    CombinedTrendCaptureMilestoneV2Top9RegimeStrategy
):
    """
    Keep the bull/bear regime layer, but disable range-reversion entries.
    This isolates the value of the market-state logic itself.
    """

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        return remove_range_reversion_entries(dataframe)
