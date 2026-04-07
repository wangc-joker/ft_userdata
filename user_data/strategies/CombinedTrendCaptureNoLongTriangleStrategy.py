from pandas import DataFrame

from CombinedTrendCaptureOptStrategy import CombinedTrendCaptureOptStrategy


class CombinedTrendCaptureNoLongTriangleStrategy(CombinedTrendCaptureOptStrategy):
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        dataframe.loc[
            dataframe.get("enter_tag", "").eq("long_1d_triangle"),
            ["enter_long", "enter_tag"],
        ] = (0, None)
        return dataframe
