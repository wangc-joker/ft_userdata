def confirm_trade_exit(
    strategy,
    pair: str,
    trade,
    order_type: str,
    amount: float,
    rate: float,
    time_in_force: str,
    exit_reason: str,
    current_time,
    **kwargs,
) -> bool:
    is_backtest = strategy.is_backtest_mode()

    if exit_reason != "force_exit":
        if strategy._should_hold_trade(trade, rate, exit_reason):
            return False

        if exit_reason in ["stop_loss", "trailing_stop_loss"]:
            is_liquidation = False
            if strategy.is_futures_mode and is_backtest:
                if (trade.is_short and rate > trade.liquidation_price) or (
                    not trade.is_short and rate < trade.liquidation_price
                ):
                    is_liquidation = True
            if not is_liquidation:
                return False

        if strategy.exit_profit_only:
            profit = 0.0
            if trade.realized_profit != 0.0:
                profit = ((rate - trade.open_rate) / trade.open_rate) * trade.stake_amount * (
                    1 - trade.fee_close
                )
                profit = profit + trade.realized_profit
                profit = profit / trade.stake_amount
            else:
                profit = trade.calc_profit_ratio(rate)
            if profit < strategy.exit_profit_offset:
                return False

    strategy._remove_profit_target(pair)
    return True
