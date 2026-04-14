from pandas import DataFrame


def remove_range_reversion_entries(dataframe: DataFrame) -> DataFrame:
    range_tags = dataframe["enter_tag"].fillna("").isin(
        {"long_range_1h_revert", "short_range_1h_revert"}
    )
    dataframe.loc[range_tags, ["enter_long", "enter_short", "enter_tag"]] = (0, 0, None)
    return dataframe


def remove_long_triangle_entries(dataframe: DataFrame) -> DataFrame:
    long_triangle = dataframe["enter_tag"].fillna("").eq("long_1d_triangle")
    dataframe.loc[long_triangle, ["enter_long", "enter_tag"]] = (0, None)
    return dataframe
