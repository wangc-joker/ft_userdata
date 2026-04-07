from DoubleShunStrategy import DoubleShunStrategy


class DoubleShunStrategyWithETH(DoubleShunStrategy):
    allowed_pairs = {
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
    }
