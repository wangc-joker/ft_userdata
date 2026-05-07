"""Mode tag constants extracted from NostalgiaForInfinityX7.

These constants are intentionally not wired into the strategy yet. During
parity refactor, we first extract stable definitions and then migrate behavior
in small, testable steps.
"""

LONG_NORMAL_MODE_TAGS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
LONG_PUMP_MODE_TAGS = ["21", "22", "23", "24", "25", "26"]
LONG_QUICK_MODE_TAGS = ["41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53"]
LONG_REBUY_MODE_TAGS = ["61", "62", "63"]
LONG_HIGH_PROFIT_MODE_TAGS = ["81", "82"]
LONG_RAPID_MODE_TAGS = ["101", "102", "103", "104", "105", "106", "107", "108", "109", "110"]
LONG_GRIND_MODE_TAGS = ["120"]
LONG_BTC_MODE_TAGS = ["121"]
LONG_TOP_COINS_MODE_TAGS = ["141", "142", "143", "144", "145"]
LONG_SCALP_MODE_TAGS = ["161", "162", "163"]

SHORT_NORMAL_MODE_TAGS = ["501", "502"]
SHORT_PUMP_MODE_TAGS = ["521", "522", "523", "524", "525", "526"]
SHORT_QUICK_MODE_TAGS = ["541", "542", "543", "544", "545", "546", "547", "548", "549", "550"]
SHORT_REBUY_MODE_TAGS = ["561"]
SHORT_HIGH_PROFIT_MODE_TAGS = ["581", "582"]
SHORT_RAPID_MODE_TAGS = ["601", "602", "603", "604", "605", "606", "607", "608", "609", "610"]
SHORT_GRIND_MODE_TAGS = ["620"]
SHORT_TOP_COINS_MODE_TAGS = ["641", "642"]
SHORT_SCALP_MODE_TAGS = ["661"]

MODE_NAMES = {
    "long_normal": "long_normal",
    "long_pump": "long_pump",
    "long_quick": "long_quick",
    "long_rebuy": "long_rebuy",
    "long_high_profit": "long_hp",
    "long_rapid": "long_rapid",
    "long_grind": "long_grind",
    "long_btc": "long_btc",
    "long_top_coins": "long_tc",
    "long_scalp": "long_scalp",
    "short_normal": "short_normal",
    "short_pump": "short_pump",
    "short_quick": "short_quick",
    "short_rebuy": "short_rebuy",
    "short_high_profit": "short_hp",
    "short_rapid": "short_rapid",
    "short_top_coins": "short_tc",
    "short_scalp": "short_scalp",
}

LONG_TAG_GROUPS = {
    "normal": LONG_NORMAL_MODE_TAGS,
    "pump": LONG_PUMP_MODE_TAGS,
    "quick": LONG_QUICK_MODE_TAGS,
    "rebuy": LONG_REBUY_MODE_TAGS,
    "high_profit": LONG_HIGH_PROFIT_MODE_TAGS,
    "rapid": LONG_RAPID_MODE_TAGS,
    "grind": LONG_GRIND_MODE_TAGS,
    "btc": LONG_BTC_MODE_TAGS,
    "top_coins": LONG_TOP_COINS_MODE_TAGS,
    "scalp": LONG_SCALP_MODE_TAGS,
}

SHORT_TAG_GROUPS = {
    "normal": SHORT_NORMAL_MODE_TAGS,
    "pump": SHORT_PUMP_MODE_TAGS,
    "quick": SHORT_QUICK_MODE_TAGS,
    "rebuy": SHORT_REBUY_MODE_TAGS,
    "high_profit": SHORT_HIGH_PROFIT_MODE_TAGS,
    "rapid": SHORT_RAPID_MODE_TAGS,
    "grind": SHORT_GRIND_MODE_TAGS,
    "top_coins": SHORT_TOP_COINS_MODE_TAGS,
    "scalp": SHORT_SCALP_MODE_TAGS,
}
