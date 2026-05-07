from functools import reduce

from pandas import DataFrame
from freqtrade.persistence import Trade

from nfi_refactor.entries.long_conditions import (
    append_long_1,
    append_long_2,
    append_long_3,
    append_long_4,
    append_long_5,
    append_long_6,
    append_long_21,
    append_long_120,
    append_long_141,
    append_long_142,
    append_long_143,
    append_long_144,
    append_long_145,
    append_long_101,
    append_long_102,
    append_long_103,
    append_long_104,
    append_long_161,
    append_long_162,
    append_long_163,
    append_long_41,
    append_long_42,
    append_long_43,
    append_long_44,
    append_long_45,
    append_long_46,
    append_long_61,
    append_long_62,
    append_long_63,
)
from nfi_refactor.entries.short_conditions import (
    append_short_501,
    append_short_502,
    append_short_503,
    append_short_504,
    append_short_541,
    append_short_542,
    append_short_543,
    append_short_641,
    append_short_642,
    append_short_661,
)


# Entry signal factory extracted from NostalgiaForInfinityX7.
# Keep this mechanically equivalent until entry-side parity work is complete.

def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
    long_entry_conditions = []
    short_entry_conditions = []

    df.loc[:, "enter_tag"] = ""
    df.loc[:, "enter_long"] = 0
    df.loc[:, "enter_short"] = 0

    is_backtest = self.dp.runmode.value in ["backtest", "hyperopt", "plot", "webserver"]
    # the number of free slots
    current_free_slots = self.config["max_open_trades"]
    if not is_backtest:
      current_free_slots = self.config["max_open_trades"] - Trade.get_open_trade_count()
    # Grind mode
    num_open_long_grind_mode = 0
    is_pair_long_grind_mode = metadata["pair"].split("/")[0] in self.grind_mode_coins
    if not is_backtest:
      open_trades = Trade.get_trades_proxy(is_open=True)
      for open_trade in open_trades:
        enter_tag = open_trade.enter_tag
        if enter_tag is not None:
          enter_tags = enter_tag.split()
          if all(c in self.long_grind_mode_tags for c in enter_tags):
            num_open_long_grind_mode += 1
    # Top Coins mode
    is_pair_long_top_coins_mode = metadata["pair"].split("/")[0] in self.top_coins_mode_coins
    is_pair_short_top_coins_mode = metadata["pair"].split("/")[0] in self.top_coins_mode_coins
    # if BTC/ETH stake
    is_btc_stake = self.config["stake_currency"] in self.btc_stakes
    allowed_empty_candles_288 = 144 if is_btc_stake else 60

    ###############################################################################################

    # LONG ENTRY CONDITIONS STARTS HERE

    ###############################################################################################

    #
    #  /$$       /$$$$$$ /$$   /$$ /$$$$$$        /$$$$$$$$/$$   /$$/$$$$$$$$/$$$$$$$$/$$$$$$$
    # | $$      /$$__  $| $$$ | $$/$$__  $$      | $$_____| $$$ | $|__  $$__| $$_____| $$__  $$
    # | $$     | $$  \ $| $$$$| $| $$  \__/      | $$     | $$$$| $$  | $$  | $$     | $$  \ $$
    # | $$     | $$  | $| $$ $$ $| $$ /$$$$      | $$$$$  | $$ $$ $$  | $$  | $$$$$  | $$$$$$$/
    # | $$     | $$  | $| $$  $$$| $$|_  $$      | $$__/  | $$  $$$$  | $$  | $$__/  | $$__  $$
    # | $$     | $$  | $| $$\  $$| $$  \ $$      | $$     | $$\  $$$  | $$  | $$     | $$  \ $$
    # | $$$$$$$|  $$$$$$| $$ \  $|  $$$$$$/      | $$$$$$$| $$ \  $$  | $$  | $$$$$$$| $$  | $$
    # |________/\______/|__/  \__/\______/       |________|__/  \__/  |__/  |________|__/  |__/
    #

    for enabled_long_entry_signal in self.long_entry_signal_params:
      long_entry_condition_index = int(enabled_long_entry_signal.split("_")[3])
      item_buy_protection_list = [True]
      if self.long_entry_signal_params[f"{enabled_long_entry_signal}"]:
        # Long Entry Conditions Starts Here
        # -----------------------------------------------------------------------------------------
        long_entry_logic = []
        long_entry_logic.append(reduce(lambda x, y: x & y, item_buy_protection_list))

        # Condition #1 - Normal mode (Long).
        if long_entry_condition_index == 1:
          append_long_1(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #2 - Normal mode (Long).
        if long_entry_condition_index == 2:
          append_long_2(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #3 - Normal mode (Long).
        if long_entry_condition_index == 3:
          append_long_3(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #4 - Normal mode (Long).
        if long_entry_condition_index == 4:
          append_long_4(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #5 - Normal mode (Long).
        if long_entry_condition_index == 5:
          append_long_5(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #6 - Normal mode (Long).
        if long_entry_condition_index == 6:
          append_long_6(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #21 - Pump mode (Long).
        if long_entry_condition_index == 21:
          append_long_21(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #41 - Quick mode (Long).
        if long_entry_condition_index == 41:
          append_long_41(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #42 - Quick mode (Long).
        if long_entry_condition_index == 42:
          append_long_42(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #43 - Quick mode (Long).
        if long_entry_condition_index == 43:
          append_long_43(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #44 - Quick mode (Long).
        if long_entry_condition_index == 44:
          append_long_44(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #45 - Quick mode (Long).
        if long_entry_condition_index == 45:
          append_long_45(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #46 - Quick mode (Long).
        if long_entry_condition_index == 46:
          append_long_46(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #61 - Rebuy mode (Long).
        if long_entry_condition_index == 61:
          append_long_61(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #62 - Rebuy mode (Long).
        if long_entry_condition_index == 62:
          append_long_62(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #63 - Rebuy mode (Long).
        if long_entry_condition_index == 63:
          append_long_63(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #101 - Rapid mode (Long).
        if long_entry_condition_index == 101:
          append_long_101(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #102 - Rapid mode (Long).
        if long_entry_condition_index == 102:
          append_long_102(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #103 - Rapid mode (Long).
        if long_entry_condition_index == 103:
          append_long_103(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #104 - Rapid mode (Long).
        if long_entry_condition_index == 104:
          append_long_104(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #120 - Grind mode (Long).
        if long_entry_condition_index == 120:
          append_long_120(
            self,
            df,
            long_entry_logic,
            num_open_long_grind_mode,
            is_pair_long_grind_mode,
          )

        # Condition #141 - Top Coins mode (Long).
        if long_entry_condition_index == 141:
          append_long_141(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
            is_pair_long_top_coins_mode,
          )

        # Condition #142 - Top Coins mode (Long).
        if long_entry_condition_index == 142:
          append_long_142(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
            is_pair_long_top_coins_mode,
          )

        # Condition #143 - Top Coins mode (Long).
        if long_entry_condition_index == 143:
          append_long_143(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
            is_pair_long_top_coins_mode,
          )

        # Condition #144 - Top Coins mode (Long).
        if long_entry_condition_index == 144:
          append_long_144(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
            is_pair_long_top_coins_mode,
          )

        # Condition #145 - Top Coins mode (Long).
        if long_entry_condition_index == 145:
          append_long_145(
            df,
            long_entry_logic,
            allowed_empty_candles_288,
            is_pair_long_top_coins_mode,
          )

        # Condition #161 - Scalp mode (Long).
        if long_entry_condition_index == 161:
          append_long_161(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #162 - Scalp mode (Long).
        if long_entry_condition_index == 162:
          append_long_162(df, long_entry_logic, allowed_empty_candles_288)

        # Condition #163 - Scalp mode (Long).
        if long_entry_condition_index == 163:
          append_long_163(df, long_entry_logic, allowed_empty_candles_288)

        ###############################################################################################

        # LONG ENTRY CONDITIONS ENDS HERE

        ###############################################################################################

        long_entry_logic.append(df["volume"] > 0)
        item_long_entry = reduce(lambda x, y: x & y, long_entry_logic)
        df.loc[item_long_entry, "enter_tag"] += f"{long_entry_condition_index} "
        long_entry_conditions.append(item_long_entry)
        df.loc[:, "enter_long"] = item_long_entry.astype(int)

    if long_entry_conditions:
      df.loc[:, "enter_long"] = reduce(lambda x, y: x | y, long_entry_conditions).astype(int)

    ###############################################################################################

    # SHORT ENTRY CONDITIONS STARTS HERE

    ###############################################################################################

    #   ______  __    __  ______  _______ ________        ________ __    __ ________ ________ _______
    #  /      \|  \  |  \/      \|       |        \      |        |  \  |  |        |        |       \
    # |  $$$$$$| $$  | $|  $$$$$$| $$$$$$$\$$$$$$$$      | $$$$$$$| $$\ | $$\$$$$$$$| $$$$$$$| $$$$$$$\
    # | $$___\$| $$__| $| $$  | $| $$__| $$ | $$         | $$__   | $$$\| $$  | $$  | $$__   | $$__| $$
    #  \$$    \| $$    $| $$  | $| $$    $$ | $$         | $$  \  | $$$$\ $$  | $$  | $$  \  | $$    $$
    #  _\$$$$$$| $$$$$$$| $$  | $| $$$$$$$\ | $$         | $$$$$  | $$\$$ $$  | $$  | $$$$$  | $$$$$$$\
    # |  \__| $| $$  | $| $$__/ $| $$  | $$ | $$         | $$_____| $$ \$$$$  | $$  | $$_____| $$  | $$
    #  \$$    $| $$  | $$\$$    $| $$  | $$ | $$         | $$     | $$  \$$$  | $$  | $$     | $$  | $$
    #   \$$$$$$ \$$   \$$ \$$$$$$ \$$   \$$  \$$          \$$$$$$$$\$$   \$$   \$$   \$$$$$$$$\$$   \$$
    #

    for enabled_short_entry_signal in self.short_entry_signal_params:
      short_entry_condition_index = int(enabled_short_entry_signal.split("_")[3])
      item_short_buy_protection_list = [True]
      if self.short_entry_signal_params[f"{enabled_short_entry_signal}"]:
        # Short Entry Conditions Starts Here
        # -----------------------------------------------------------------------------------------
        # IMPORTANT: Short Condition Descriptions are not for shorts. These are for longs but completely mirrored opposite side
        # Please dont change these comment descriptions. With these descriptions we are comparing long/short positions.

        short_entry_logic = []
        short_entry_logic.append(reduce(lambda x, y: x & y, item_short_buy_protection_list))

        # Condition #501 - Normal mode (Short).
        if short_entry_condition_index == 501:
          append_short_501(
            df,
            short_entry_logic,
            allowed_empty_candles_288,
          )

        # Condition #502 - Normal mode (Short).
        if short_entry_condition_index == 502:
          append_short_502(df, short_entry_logic, allowed_empty_candles_288)

        # Condition #503 - Normal mode (Short).
        if short_entry_condition_index == 503:
          append_short_503(df, short_entry_logic, allowed_empty_candles_288)

        # Condition #504 - Normal mode (Short).
        if short_entry_condition_index == 504:
          append_short_504(df, short_entry_logic, allowed_empty_candles_288)

        # Condition #541 - Quick mode (Short).
        if short_entry_condition_index == 541:
          append_short_541(df, short_entry_logic, allowed_empty_candles_288)

        # Condition #542 - Quick mode (Short).
        if short_entry_condition_index == 542:
          append_short_542(df, short_entry_logic, allowed_empty_candles_288)

        # Condition #543 - Rapid mode (Short).
        if short_entry_condition_index == 543:
          append_short_543(df, short_entry_logic, allowed_empty_candles_288)

        # # Condition #620 - Grind mode (Short).
        # if short_entry_condition_index == 620:
        #   # Protections
        #   short_entry_logic.append(num_open_short_grind_mode < self.grind_mode_max_slots)
        #   short_entry_logic.append(is_pair_short_grind_mode)
        #   short_entry_logic.append(df["RSI_3"] <= 40.0)
        #   short_entry_logic.append(df["RSI_3_15m"] >= 10.0)
        #   short_entry_logic.append(df["RSI_3_1h"] >= 5.0)
        #   short_entry_logic.append(df["RSI_3_4h"] >= 5.0)
        #   short_entry_logic.append(df["RSI_14_1h"] < 85.0)
        #   short_entry_logic.append(df["RSI_14_4h"] < 85.0)
        #   short_entry_logic.append(df["RSI_14_1d"] < 85.0)
        #   short_entry_logic.append(df["close_max_48"] >= (df["close"] * 1.10))

        #   # Logic
        #   short_entry_logic.append(df["STOCHRSIk_14_14_3_3"] > 80.0)
        #   short_entry_logic.append(df["WILLR_14"] > -20.0)
        #   short_entry_logic.append(df["AROOND_14"] < 25.0)

        # Condition #641 - Top Coins mode (Short).
        if short_entry_condition_index == 641:
          append_short_641(df, short_entry_logic, allowed_empty_candles_288, is_pair_short_top_coins_mode)

        # Condition #642 - Top Coins mode (Short).
        if short_entry_condition_index == 642:
          append_short_642(df, short_entry_logic, allowed_empty_candles_288, is_pair_short_top_coins_mode)

        # Condition #661 - Scalp mode (Short).
        if short_entry_condition_index == 661:
          append_short_661(df, short_entry_logic, allowed_empty_candles_288)

        ###############################################################################################

        # SHORT ENTRY CONDITIONS ENDS HERE

        ###############################################################################################

        short_entry_logic.append(df["volume"] > 0)
        item_short_entry = reduce(lambda x, y: x & y, short_entry_logic)
        df.loc[item_short_entry, "enter_tag"] += f"{short_entry_condition_index} "
        short_entry_conditions.append(item_short_entry)
        df.loc[:, "enter_short"] = item_short_entry.astype(int)

    if short_entry_conditions:
      df.loc[:, "enter_short"] = reduce(lambda x, y: x | y, short_entry_conditions).astype(int)

    return df
