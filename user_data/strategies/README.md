# Strategies Directory

This directory is organized by responsibility:

- `myStrage/`
  - Current main strategy set.
  - Only keep the live main trend, the 193 reversal line, and the 216 return-focused line here.
- `run/`
  - Strategies currently used for running live / test-live bots.
- `test/`
  - All other experimental, historical, or comparison strategies.
- `entrypoints/`
  - Freqtrade-facing strategy entry classes.
- `core/`
  - Shared market-state, indicator, and risk logic.
  - Current indicator split:
    - `core/indicators/structure.py`
- `signals/`
  - Long and short entry/exit signal building blocks.
  - Current split:
    - `signals/long/entries.py`
    - `signals/short/entries.py`
    - `signals/reversal.py`
    - `signals/exit_rules.py`
    - `signals/filters.py`
- `pairs/`
  - Per-coin special handling and overrides.
  - Current explicit profiles:
    - `pairs/btc/profile.py`
    - `pairs/eth/profile.py`
    - `pairs/zec/profile.py`
- `shared/`
  - Common constants and reusable configuration.
- `archive/`
  - Historical and experimental versions kept for reference.
  - Legacy `CombinedTrendCaptureMilestoneV1*` and `CombinedTrendCaptureMilestoneV2*`
    families live here under `archive/old_versions/`.
- `research/`
  - Research notes, kline exports, and breakout audits that motivated
    strategy changes.

Current note:

- Active Top9 strategies now live under `myStrage/`.
- The running test-live entry now lives under `run/`.
- Historical / comparison strategies now live under `test/` or `archive/old_versions/`.

Primary current entrypoints:

- `myStrage/Top9MainTrendStrategy.py`
- `run/Top9Main60UTestLiveStrategy.py`
- `myStrage/Top9MainReversal193Strategy.py`
- `myStrage/Top9MainReversalZec216Strategy.py`
- `myStrage/Top9MainReversal216ShortAggressiveStrategy.py`

Test-live specific assets:

- `config.backtest.futures.top9.testlive.json`
- `config.live.futures.top9.testlive.json`
- `start_top9main_test_live.ps1`
- `start_top9main_test_live.cmd`
- `show_top9main_test_live_status.ps1`
- `show_top9main_test_live_status.cmd`

Research assets:

- `research/zec_1h_reversal_breakout_notes.md`
- `research/breakout_audit/`
- `research/zec_klines/`

Architecture notes are kept in:

- `策略架构说明.md`
- `策略总览.md`
