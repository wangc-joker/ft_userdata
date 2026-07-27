# Repository Instructions

## DualTrend Source Of Truth

- Before analyzing, editing, backtesting, or recommending a DualTrend strategy, read `CURRENT_DUALTREND.md` in the repository root.
- Treat that file as the sole authority for the current research candidate, standard backtest scope, retained controls, rejected experiments, and runtime/config differences.
- The current research candidate is `DualTrendPyramidSecondAdd20LongMicroV1Strategy`. Keep `DualTrendPyramidSecondAdd20V1Strategy` as the stable control, and do not report the historical `+191.75%` Window05To15 strategy as current.
- Use the corrected 2026-07-20 LongMicro results in `CURRENT_DUALTREND.md`. The earlier `+216.62%`, `+281.17%`, `+200.99%`, and `+253.85%` figures are invalid because an expansion-mixin parameter accidentally overrode the parent daily-long breakout buffer.
- Dated files under `user_data/reports/` and DualTrend files under `我的策略/` are historical evidence. Their use of words such as "current", "main", or "candidate" applies only to the date of that document.
- Do not infer the research candidate from a config or launcher alone. The Positive13 backtest config defaults to Raw, and the existing Positive13 dry-run launcher also runs a Raw-compatible alias.
- A separate LongMicro observation bot was started on port 8086 on 2026-07-20. Always check runtime state before describing it as active; the launcher must leave the live `freqtrade` container state and identity unchanged.
- If a new experiment replaces the research candidate, update `CURRENT_DUALTREND.md` in the same change. Include the promoted class, comparable results, runtime status, and newly rejected directions.
