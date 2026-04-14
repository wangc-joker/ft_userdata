# Strategies Directory

This directory is organized by responsibility:

- `entrypoints/`
  - Freqtrade-facing strategy entry classes.
  - Root files like `Top9RegimeMainStrategy.py` remain as compatibility shims.
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

Current note:

- The active Top9 ancestor chain is still kept in the root directory for now
  because those classes are imported directly by the entrypoints.
- Older experimental and historical branches have been moved into
  `archive/old_versions/`.

Primary current entrypoints:

- `Top9RegimeMainStrategy.py`
- `Top9RegimeMainReversalStrategy.py`
- `Top9RegimeMainReversal216Strategy.py`

Architecture notes are kept in:

- `策略架构说明.md`
- `策略总览.md`
