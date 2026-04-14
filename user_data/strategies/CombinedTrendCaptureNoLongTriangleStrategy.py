from pandas import DataFrame

from CombinedTrendCaptureOptStrategy import CombinedTrendCaptureOptStrategy
from signals.filters import remove_long_triangle_entries


class CombinedTrendCaptureNoLongTriangleStrategy(CombinedTrendCaptureOptStrategy):
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        return remove_long_triangle_entries(dataframe)
