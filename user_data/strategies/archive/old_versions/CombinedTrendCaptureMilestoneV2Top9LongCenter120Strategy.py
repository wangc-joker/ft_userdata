from .CombinedTrendCaptureMilestoneV2Top9Strategy import CombinedTrendCaptureMilestoneV2Top9Strategy


class CombinedTrendCaptureMilestoneV2Top9LongCenter120Strategy(
    CombinedTrendCaptureMilestoneV2Top9Strategy
):
    """
    Top9 experiment:
    Slightly reduce the extra stake boost on long_1d_center_compression.
    """

    stake_multipliers = {
        "long_1d_center_compression": 1.20,
        "short_1d_center_compression": 1.15,
        "short_1h_center": 0.80,
    }
