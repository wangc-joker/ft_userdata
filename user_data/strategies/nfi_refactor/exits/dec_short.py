"""DEC short exit signal router extracted from NFI."""

from nfi_refactor.exits.dec_short_band_0 import short_exit_dec_band_0
from nfi_refactor.exits.dec_short_band_1 import short_exit_dec_band_1
from nfi_refactor.exits.dec_short_band_2 import short_exit_dec_band_2
from nfi_refactor.exits.dec_short_band_3 import short_exit_dec_band_3
from nfi_refactor.exits.dec_short_band_4 import short_exit_dec_band_4
from nfi_refactor.exits.dec_short_band_5 import short_exit_dec_band_5
from nfi_refactor.exits.dec_short_band_6 import short_exit_dec_band_6
from nfi_refactor.exits.dec_short_band_7 import short_exit_dec_band_7
from nfi_refactor.exits.dec_short_band_8 import short_exit_dec_band_8
from nfi_refactor.exits.dec_short_band_9 import short_exit_dec_band_9
from nfi_refactor.exits.dec_short_band_10 import short_exit_dec_band_10
from nfi_refactor.exits.dec_short_band_11 import short_exit_dec_band_11
from nfi_refactor.exits.dec_short_band_12 import short_exit_dec_band_12

DEC_SHORT_BAND_HELPERS = [
  short_exit_dec_band_0,
  short_exit_dec_band_1,
  short_exit_dec_band_2,
  short_exit_dec_band_3,
  short_exit_dec_band_4,
  short_exit_dec_band_5,
  short_exit_dec_band_6,
  short_exit_dec_band_7,
  short_exit_dec_band_8,
  short_exit_dec_band_9,
  short_exit_dec_band_10,
  short_exit_dec_band_11,
  short_exit_dec_band_12,
]

def short_exit_dec(
    strategy,
    mode_name: str,
    current_profit: float,
    max_profit: float,
    max_loss: float,
    last_candle,
    previous_candle_1,
    previous_candle_2,
    previous_candle_3,
    previous_candle_4,
    previous_candle_5,
    trade: "Trade",
    current_time: "datetime",
    buy_tag,
  ) -> tuple:
    for helper in DEC_SHORT_BAND_HELPERS:
      should_exit, exit_reason = helper(
      strategy,
      mode_name,
      current_profit,
      max_profit,
      max_loss,
      last_candle,
      previous_candle_1,
      previous_candle_2,
      previous_candle_3,
      previous_candle_4,
      previous_candle_5,
      trade,
      current_time,
      buy_tag,
    )
      if should_exit:
        return should_exit, exit_reason

    #  Here ends exit signal conditions for short_exit_dec

    return False, None

