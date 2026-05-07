"""Long-side rebuy exit mode router."""

from datetime import datetime

# Keep this function mechanically equivalent until parity work is complete.
def long_exit_rebuy(
    self,
    pair: str,
    current_rate: float,
    profit_stake: float,
    profit_ratio: float,
    profit_current_stake_ratio: float,
    profit_init_ratio: float,
    max_profit: float,
    max_loss: float,
    filled_entries,
    filled_exits,
    last_candle,
    previous_candle_1,
    previous_candle_2,
    previous_candle_3,
    previous_candle_4,
    previous_candle_5,
    trade: "Trade",
    current_time: "datetime",
    enter_tags,
  ) -> tuple:
    is_backtest = self.is_backtest_mode()
    is_system_v3 = self.is_system_v3(trade)
    is_system_v3_1 = self.is_system_v3_1(trade)
    is_system_v3_2 = self.is_system_v3_2(trade)
    sell = False

    # Original sell signals
    sell, signal_name = self.long_exit_signals(
      self.long_rebuy_mode_name,
      profit_current_stake_ratio,
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
      enter_tags,
    )

    # Main sell signals
    if not sell:
      sell, signal_name = self.long_exit_main(
        self.long_rebuy_mode_name,
        profit_current_stake_ratio,
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
        enter_tags,
      )

    # Williams %R based sells
    if not sell:
      sell, signal_name = self.long_exit_williams_r(
        self.long_rebuy_mode_name,
        profit_current_stake_ratio,
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
        enter_tags,
      )

    # Downtrend/descending based sells
    if not sell:
      sell, signal_name = self.long_exit_dec(
        self.long_rebuy_mode_name,
        profit_current_stake_ratio,
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
        enter_tags,
      )

    # Stoplosses
    if not sell:
      if is_system_v3_2:
        if self.system_v3_2_stops_enable and (
          profit_stake
          < -(
            filled_entries[0].cost
            * (
              self.system_v3_2_stop_threshold_futures_rebuy
              if self.is_futures_mode
              else self.system_v3_2_stop_threshold_spot_rebuy
            )
            / trade.leverage
          )
        ):
          sell, signal_name = True, f"exit_{self.long_rebuy_mode_name}_stoploss_doom"
      elif is_system_v3_1:
        if profit_stake < -(
          filled_entries[0].cost
          * (
            self.system_v3_1_stop_threshold_futures_rebuy
            if self.is_futures_mode
            else self.system_v3_1_stop_threshold_spot_rebuy
          )
          / trade.leverage
        ):
          sell, signal_name = True, f"exit_{self.long_rebuy_mode_name}_stoploss_doom"
      elif is_system_v3:
        if profit_stake < -(
          filled_entries[0].cost
          * (
            self.system_v3_stop_threshold_futures_rebuy
            if self.is_futures_mode
            else self.system_v3_stop_threshold_spot_rebuy
          )
          / trade.leverage
        ):
          sell, signal_name = True, f"exit_{self.long_rebuy_mode_name}_stoploss_doom"
      else:
        if (
          profit_stake
          < -(
            filled_entries[0].cost
            * (self.stop_threshold_futures_rebuy if self.is_futures_mode else self.stop_threshold_spot_rebuy)
            / trade.leverage
          )
          # temporary
          and (trade.open_date_utc.replace(tzinfo=None) >= datetime(2024, 9, 13) or is_backtest)
        ):
          sell, signal_name = True, f"exit_{self.long_rebuy_mode_name}_stoploss_doom"

    # Profit Target Signal
    # Check if pair exist on target_profit_cache
    if self.target_profit_cache is not None and pair in self.target_profit_cache.data:
      previous_rate = self.target_profit_cache.data[pair]["rate"]
      previous_profit = self.target_profit_cache.data[pair]["profit"]
      previous_sell_reason = self.target_profit_cache.data[pair]["sell_reason"]
      previous_time_profit_reached = datetime.fromisoformat(self.target_profit_cache.data[pair]["time_profit_reached"])

      sell_max, signal_name_max = self.exit_profit_target(
        self.long_rebuy_mode_name,
        pair,
        trade,
        current_time,
        current_rate,
        profit_stake,
        profit_ratio,
        profit_current_stake_ratio,
        profit_init_ratio,
        last_candle,
        previous_candle_1,
        previous_rate,
        previous_profit,
        previous_sell_reason,
        previous_time_profit_reached,
        enter_tags,
      )
      if sell_max and signal_name_max is not None:
        return True, f"{signal_name_max}_m"
      if previous_sell_reason in [f"exit_{self.long_rebuy_mode_name}_stoploss_u_e"]:
        if profit_ratio > (previous_profit + 0.001):
          mark_pair, mark_signal = self.mark_profit_target(
            self.long_rebuy_mode_name,
            pair,
            True,
            previous_sell_reason,
            trade,
            current_time,
            current_rate,
            profit_ratio,
            last_candle,
            previous_candle_1,
          )
          if mark_pair:
            self._set_profit_target(pair, mark_signal, current_rate, profit_ratio, current_time)
      elif (profit_init_ratio > (previous_profit + 0.001)) and (
        previous_sell_reason not in [f"exit_{self.long_rebuy_mode_name}_stoploss_doom"]
      ):
        # Update the target, raise it.
        mark_pair, mark_signal = self.mark_profit_target(
          self.long_rebuy_mode_name,
          pair,
          True,
          previous_sell_reason,
          trade,
          current_time,
          current_rate,
          profit_init_ratio,
          last_candle,
          previous_candle_1,
        )
        if mark_pair:
          self._set_profit_target(pair, mark_signal, current_rate, profit_init_ratio, current_time)

    # Add the pair to the list, if a sell triggered and conditions met
    if sell and signal_name is not None:
      previous_profit = None
      if self.target_profit_cache is not None and pair in self.target_profit_cache.data:
        previous_profit = self.target_profit_cache.data[pair]["profit"]
      if signal_name in [
        f"exit_{self.long_rebuy_mode_name}_stoploss_doom",
        f"exit_{self.long_rebuy_mode_name}_stoploss_u_e",
      ]:
        mark_pair, mark_signal = self.mark_profit_target(
          self.long_rebuy_mode_name,
          pair,
          sell,
          signal_name,
          trade,
          current_time,
          current_rate,
          profit_ratio,
          last_candle,
          previous_candle_1,
        )
        if mark_pair:
          self._set_profit_target(pair, mark_signal, current_rate, profit_ratio, current_time)
        else:
          # Just sell it, without maximize
          return True, f"{signal_name}"
      elif (previous_profit is None) or (previous_profit < profit_init_ratio):
        mark_pair, mark_signal = self.mark_profit_target(
          self.long_rebuy_mode_name,
          pair,
          sell,
          signal_name,
          trade,
          current_time,
          current_rate,
          profit_init_ratio,
          last_candle,
          previous_candle_1,
        )
        if mark_pair:
          self._set_profit_target(pair, mark_signal, current_rate, profit_init_ratio, current_time)
        else:
          # Just sell it, without maximize
          return True, f"{signal_name}"
    else:
      if profit_init_ratio >= 0.005:
        previous_profit = None
        if self.target_profit_cache is not None and pair in self.target_profit_cache.data:
          previous_profit = self.target_profit_cache.data[pair]["profit"]
        if (previous_profit is None) or (previous_profit < profit_init_ratio):
          mark_signal = f"exit_profit_{self.long_rebuy_mode_name}_max"
          self._set_profit_target(pair, mark_signal, current_rate, profit_init_ratio, current_time)

    if signal_name not in [
      f"exit_profit_{self.long_rebuy_mode_name}_max",
      f"exit_{self.long_rebuy_mode_name}_stoploss_doom",
      f"exit_{self.long_rebuy_mode_name}_stoploss_u_e",
    ]:
      if sell and (signal_name is not None):
        return True, f"{signal_name}"

    #  Here ends exit signal conditions for long_exit_rebuy

    return False, None

