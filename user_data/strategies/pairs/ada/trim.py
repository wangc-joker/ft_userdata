def short_1h_center_multiplier(candle, bull: bool, bear: bool) -> float:
    return 0.96 if bear else 0.88 if bull else 1.0
