"""DEC long exit signal router extracted from NFI."""

from nfi_refactor.exits.dec_long_band_0 import long_exit_dec_band_0
from nfi_refactor.exits.dec_long_band_1 import long_exit_dec_band_1
from nfi_refactor.exits.dec_long_band_2 import long_exit_dec_band_2
from nfi_refactor.exits.dec_long_band_3 import long_exit_dec_band_3
from nfi_refactor.exits.dec_long_band_4 import long_exit_dec_band_4
from nfi_refactor.exits.dec_long_band_5 import long_exit_dec_band_5
from nfi_refactor.exits.dec_long_band_6 import long_exit_dec_band_6
from nfi_refactor.exits.dec_long_band_7 import long_exit_dec_band_7
from nfi_refactor.exits.dec_long_band_8 import long_exit_dec_band_8
from nfi_refactor.exits.dec_long_band_9 import long_exit_dec_band_9
from nfi_refactor.exits.dec_long_band_10 import long_exit_dec_band_10
from nfi_refactor.exits.dec_long_band_11 import long_exit_dec_band_11
from nfi_refactor.exits.dec_long_band_12 import long_exit_dec_band_12

DEC_LONG_BAND_HELPERS = [
  long_exit_dec_band_0,
  long_exit_dec_band_1,
  long_exit_dec_band_2,
  long_exit_dec_band_3,
  long_exit_dec_band_4,
  long_exit_dec_band_5,
  long_exit_dec_band_6,
  long_exit_dec_band_7,
  long_exit_dec_band_8,
  long_exit_dec_band_9,
  long_exit_dec_band_10,
  long_exit_dec_band_11,
  long_exit_dec_band_12,
]

def long_exit_dec(
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
    for helper in DEC_LONG_BAND_HELPERS:
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

    #  Here ends exit signal conditions for long_exit_dec

    return False, None

