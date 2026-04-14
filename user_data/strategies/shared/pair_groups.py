from pairs.btc.profile import PAIR as BTC_PAIR
from pairs.eth.profile import PAIR as ETH_PAIR
from pairs.zec.profile import PAIR as ZEC_PAIR

LONG_REVERSAL_PAIRS_193 = {
    BTC_PAIR,
    ETH_PAIR,
}

SHORT_REVERSAL_PAIRS_193 = {
    BTC_PAIR,
    ETH_PAIR,
    "DOGE/USDT:USDT",
    "XRP/USDT:USDT",
    ZEC_PAIR,
}

LONG_REVERSAL_PAIRS_216 = {
    ZEC_PAIR,
}

SHORT_REVERSAL_PAIRS_216 = {
    BTC_PAIR,
    "TRX/USDT:USDT",
    "ADA/USDT:USDT",
    ETH_PAIR,
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT",
    ZEC_PAIR,
}

TOP9_MAIN_PAIRS = {
    BTC_PAIR,
    ETH_PAIR,
    "BNB/USDT:USDT",
    "SOL/USDT:USDT",
    "TRX/USDT:USDT",
    "ADA/USDT:USDT",
    ZEC_PAIR,
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT",
}
