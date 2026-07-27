# LongMicro Dry-Run Observation

This directory is reserved for reports generated from the isolated Positive13/max3 LongMicro observation bot.

Runtime snapshot: started at 2026-07-20 15:01 Asia/Shanghai. The API reported `dry_run`, `running`, 13 pairs, max 3 open trades, and a 1000 USDT virtual wallet. Initial state was 0 open and 0 closed trades. Check the container before relying on this snapshot.

Latest checked snapshot: at 2026-07-27 12:00 Asia/Shanghai the bot was running with 0 open trades and 1 closed trade. The first out-of-sample trade was BTC `long_pullback_restart_1h_body`, closed by stop loss on 2026-07-24 13:10:04 for `-1.68% / -5.4923 USDT`. The collision collector still had only this one `admitted` candidate and no slot-full collision. This single loss is observation evidence, not a promotion or rejection decision.

Incident note: Binance futures mainnet returned intermittent HTTP 451 responses on 2026-07-20 and later recovered. Docker Desktop was found stopped on 2026-07-21; after Docker restarted, the observation container automatically restarted and loaded markets successfully. The launcher now starts Docker Desktop when needed, and the status script reports alerts only from the current container start. Do not switch this observation bot to testnet metadata as a workaround.

Maintenance note: pandas FutureWarning messages caused by implicit boolean downcasting in the local DualTrend strategy were removed on 2026-07-21 with explicit nullable-boolean normalization. A one-year validation reproduced all 123 trades and `724.90464335 USDT` profit exactly. Freqtrade 2026.3 also emits the same warning from `freqtrade/strategy/strategy_helper.py:109`; the observation launcher now suppresses only that exact upstream module/message combination through `PYTHONWARNINGS`, without opting into pandas' future behavior or changing strategy logic.

- Strategy: `DualTrendPyramidSecondAdd20LongMicroV1Strategy`
- Container: `freqtrade-positive13-longmicro-observation`
- API: `127.0.0.1:8086`
- Database: `user_data/tradesv3-positive13-longmicro-observation.sqlite`
- CSV artifacts: `user_data/analysis/longmicro_observation/`
- Signal collision shadow database: `user_data/analysis/signal_collision_shadow.sqlite`

The observation bot is dry-run only and does not replace the existing Raw-compatible dry-run or the live container. Its launcher verifies that the live `freqtrade` container state and identity remain unchanged throughout startup, whether that container is running or stopped.

Use `start_positive13_longmicro_observation.cmd` to start, `show_positive13_longmicro_observation_status.cmd` to inspect it, `run_positive13_longmicro_observation_report.cmd` to generate isolated monitoring reports, and `stop_positive13_longmicro_observation.cmd` to stop only this verified observation container. Report generation runs `dryrun_monitor.py` inside the Freqtrade container, so the host does not need separate NumPy or pandas packages.

The read-only collision shadow collector uses the same API without changing strategy behavior. Use `start_positive13_collision_shadow.cmd`, `show_positive13_collision_shadow_status.cmd`, and `stop_positive13_collision_shadow.cmd`. It records admitted and slot-blocked signal candidates in a separate SQLite database. The first verified record on 2026-07-24 was the open BTC LongMicro signal and was classified as `admitted`; this is an infrastructure check, not a performance conclusion.

No production promotion should be inferred from an empty or small observation sample. Review Micro tag count, slot pressure, execution warnings, drawdown, and the existing monitoring gates before changing any runtime entry.
