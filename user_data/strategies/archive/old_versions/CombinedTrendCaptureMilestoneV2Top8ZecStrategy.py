from .CombinedTrendCaptureMilestoneV2Strategy import CombinedTrendCaptureMilestoneV2Strategy


class CombinedTrendCaptureMilestoneV2Top8ZecStrategy(CombinedTrendCaptureMilestoneV2Strategy):
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
