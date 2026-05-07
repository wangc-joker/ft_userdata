# NFI Migration Checklist

## Reference

Source file:

```text
D:\test\NostalgiaForInfinity\NostalgiaForInfinityX7.py
```

## Step 1: Parity Baseline

- [x] Record original NFI backtest config.
- [x] Record original NFI pairlist.
- [x] Record original NFI timeranges.
- [x] Record original NFI result for recent 6 month sample.
- [x] Record NFIRefactorStrategy parity result for recent 6 month sample.
- [ ] Record original NFI result for top9 / 300U.
- [ ] Record original NFI result for top20 / 300U.
- [ ] Record original NFI result for 3 month downtrend sample.

## Step 2: Module Extraction

- [x] Extract class constants and mode names.
- [x] Extract mode coin lists.
- [x] Extract top-level strategy defaults.
- [x] Extract informative pair construction.
- [x] Extract BTC informative indicators.
- [x] Extract pair informative indicators.
- [x] Extract base timeframe indicators.
- [x] Extract populate_indicators orchestration.
- [x] Extract and split global long protections.
- [x] Split long global protection expression into chunk modules.
- [x] Extract and split global short protections.
- [x] Extract populate_entry_trend entry signal factory.
- [x] Split long entry modes into smaller modules.
- [x] Extract and split long normal entry conditions #1-#6 as modular condition helpers.
- [x] Split normal long entry conditions #1-#6 into individual modules.
- [x] Extract and split long pump entry condition #21 as modular condition helper.
- [x] Split pump long entry condition #21 into an individual module.
- [x] Extract and split long entry condition #120 as modular condition helper.
- [x] Split grind long entry condition #120 into an individual module.
- [x] Extract and split long quick entry conditions #41-#46 as modular condition helpers.
- [x] Split quick long entry conditions #41-#46 into individual modules.
- [x] Extract and split long rebuy entry conditions #61-#63 as modular condition helpers.
- [x] Split rebuy long entry conditions #61-#63 into individual modules.
- [x] Extract and split long rapid entry conditions #101-#104 as modular condition helpers.
- [x] Split rapid long entry conditions #101-#104 into individual modules.
- [x] Extract and split long top-coins entry conditions #141-#145 as modular condition helpers.
- [x] Split top-coins long entry conditions #141-#145 into individual modules.
- [x] Extract and split long scalp entry conditions #161-#163 as modular condition helpers.
- [x] Split scalp long entry conditions #161-#163 into individual modules.
- [x] Split short entry modes into smaller modules.
- [x] Extract short entry condition #501 as modular condition helper.
- [x] Extract short normal entry conditions #502-#503 as modular condition helpers.
- [x] Extract short entry condition #504 as modular condition helper.
- [x] Extract short quick entry conditions #541-#542 as modular condition helpers.
- [x] Extract short rapid entry condition #543 as modular condition helper.
- [x] Extract short top-coins entry conditions #641-#642 as modular condition helpers.
- [x] Extract short scalp entry condition #661 as modular condition helper.
- [x] Split short entry conditions #501-#504, #541-#543, #641-#642, #661 into individual modules.
- [x] Extract custom stake amount.
- [x] Extract leverage.
- [x] Extract and split custom exit orchestration.
- [x] Extract shared custom exit reason formatter.
- [x] Extract shared custom exit mode invocation helper.
- [x] Extract custom exit long/short mode match predicates.
- [x] Extract custom exit rule-table executor.
- [x] Extract custom exit fallback router.
- [x] Extract confirm_trade_exit.
- [x] Extract and split profit target marker helper.
- [x] Extract and split profit target exit decision helper.
- [x] Extract populate_exit_trend.
- [x] Extract simple grind/btc exit mode helpers.
- [x] Extract top-coins exit mode orchestration.
- [x] Extract scalp exit mode orchestration.
- [x] Extract and split advanced normal/quick/rapid/rebuy/pump/high-profit exit mode orchestration.
- [x] Split rapid exit mode orchestration into long/short modules.
- [x] Split quick exit mode orchestration into long/short modules.
- [x] Split rebuy exit mode orchestration into long/short modules.
- [x] Split scalp exit mode orchestration into long/short modules.
- [x] Split normal exit mode orchestration into long/short modules.
- [x] Split top-coins exit mode orchestration into long/short modules.
- [x] Split pump exit mode orchestration into long/short modules.
- [x] Split high-profit exit mode orchestration into long/short modules.
- [x] Point advanced exit compatibility module directly at long/short mode modules.
- [x] Extract and split shared long/short exit signal aggregators.
- [x] Extract and split Williams-R long/short exit signal libraries.
- [x] Extract and split DEC long/short exit signal libraries by profit band.
- [x] Extract and split main long/short profit ladder exit helpers.
- [x] Extract and split long/short emergency stoploss exit helpers.
- [x] Extract order filled callback.
- [x] Extract position adjustment routing.
- [x] Extract small position adjustment helper methods.
- [x] Extract total profit calculation helper.
- [x] Split experimental grind adjustment handlers into long/short v2/v3 modules.
- [x] Investigate grind adjustment detail handler parity drift.
- [x] Split position adjustment helper predicates into long/short modules.
- [x] Extract position adjustment detail handlers.
- [x] Extract position adjustment call context object.
- [x] Extract position adjustment mode state object.
- [x] Extract position adjustment context/state builder helpers.
- [x] Extract position adjustment grind tag set helpers.
- [x] Extract position adjustment handler selectors.
- [x] Extract position adjustment tag predicate helpers.
- [x] Extract position adjustment mode predicate helpers.
- [x] Split position adjustment context/state helpers into dedicated module.
- [x] Split rebuy adjustment routing into dedicated module.
- [x] Split rebuy adjustment tag matching helpers into dedicated module.
- [x] Split rebuy adjustment handler selectors into dedicated module.
- [x] Split grind adjustment routing into dedicated module.
- [x] Remove position adjustment detail compatibility route layer.
- [x] Extract position adjustment grind direction router.
- [x] Extract position adjustment grind route selector.
- [x] Split grind adjustment tag matching helpers into dedicated module.
- [x] Split grind adjustment handler selectors into dedicated module.
- [x] Add lightweight tests for grind adjustment helpers.
- [x] Add lightweight tests for rebuy adjustment route helpers.
- [x] Add guard test to keep experimental grind adjustment handlers unwired.
- [x] Extract rebuy position adjustment handlers.
- [x] Extract rebuy position adjustment shared context.
- [x] Extract rebuy position adjustment return helpers.
- [x] Extract rebuy position adjustment sub-grind state helper.
- [x] Extract rebuy position adjustment amount and derisk helpers.
- [x] Extract rebuy position adjustment entry predicate helpers.
- [x] Extract rebuy position adjustment mode config and order-side helpers.
- [x] Extract rebuy position adjustment entry return helper.
- [x] Extract rebuy position adjustment entry attempt helper.
- [x] Extract rebuy position adjustment context wrapper helpers.
- [x] Extract rebuy position adjustment derisk-to-grind v2 router.
- [x] Extract rebuy position adjustment generic handler.
- [x] Extract confirm_trade_entry and mode entry guards.
- [x] Extract runtime mode/state helper methods.
- [x] Extract ticker timeframe helper.
- [x] Extract hold-trades runtime helpers.
- [x] Extract runtime cache initialization and persistence.
- [x] Extract runtime cache classes.
- [x] Extract bot loop start runtime hook.

## Step 3: Regression Checks

For every extracted module:

- [x] Add reusable NFI refactor regression check script.
- [x] Strategy loads.
- [x] Backtest completes.
- [x] Trade count remains close.
- [x] Profit remains close.
- [x] Drawdown remains close.
- [x] Entry tag distribution remains close.
- [x] Long/short split remains close.

## Step 4: Post-Parity Improvements

Only after parity:

- [ ] Reduce low-quality entries.
- [ ] Make runtime state persistent.
- [ ] Improve dynamic coin universe.
- [ ] Revisit short signal quality.
- [ ] Tune stake sizing and max open trades.
