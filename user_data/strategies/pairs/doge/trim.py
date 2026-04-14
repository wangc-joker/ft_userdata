def short_1h_center_multiplier(candle, bull: bool, bear: bool) -> float:
    return 0.88 if bear else 0.78 if bull else 1.0
