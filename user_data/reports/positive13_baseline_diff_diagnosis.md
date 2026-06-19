# Positive13 Baseline Diff Diagnosis

## Scope

This report investigates why the current Positive13 baseline reproduced as:

| Run | Trades | Profit | PF | MaxDD | Long / Short |
|---|---:|---:|---:|---:|---:|
| Previous reported baseline | 294 | +1907.86 USDT / +190.79% | 1.97 | 7.68% | 46 / 248 |
| Current recheck baseline | 241 | +1511.33 USDT / +151.13% | 2.01 | 7.24% | 38 / 203 |
| Difference | -53 | -396.53 USDT / -39.65 pp | +0.04 | -0.44 pp | -8 / -45 |

Important limitation: the previous run artifact referenced by the historical reports was under `D:/test/ft_userdata`, for example `D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-49-31.zip`. That directory no longer exists on this machine, so the previous run's raw zip, exported strategy snapshot, config snapshot, and trade list cannot be directly hashed or parsed. The previous-run facts below are therefore limited to values preserved in the markdown reports.

No step 8 max4/max5 diagnosis was executed, and no strategy was modified.

## 1. Strategy File Path And Hash

| Item | Previous reported baseline | Current recheck baseline |
|---|---|---|
| Strategy class | `DualTrendCombinedShortPullbackShapeV1Strategy` | `DualTrendCombinedShortPullbackShapeV1Strategy` |
| Strategy file path in report/config | `user_data/strategies/DualTrendCombinedShortPullbackShapeV1Strategy.py` in historical report text | Current class is defined in `user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py` |
| Artifact path | `D:/test/ft_userdata/.../backtest-result-2026-06-18_06-49-31.zip` | `user_data/backtest_results/backtest-result-2026-06-19_01-07-59.zip` |
| Strategy hash | Not directly verifiable because previous zip is unavailable | `a1c9b13d1e5a4ea3e4936653b0e43ed918c4b34ab1e4ff8fd6c7377df56e997a` |

Current exported strategy snapshot hash matches the current local strategy file hash:

```text
SHA256 user_data/strategies/DualTrendCombinedLongDailyCenterShortV1GlobalFilterStrategies.py
a1c9b13d1e5a4ea3e4936653b0e43ed918c4b34ab1e4ff8fd6c7377df56e997a
```

Interpretation: we can confirm the current run strategy snapshot. We cannot confirm whether the previous `294 / +190.79%` run used byte-identical strategy code.

## 2. Config File Path And Content Difference

| Item | Previous reported baseline | Current recheck baseline |
|---|---|---|
| Config path | `D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json` | `D:/work/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json` |
| Config hash | Not directly verifiable because previous workspace is unavailable | `4ab794dcb7ddb6a8803f96a36664635e3fb84f1d6af239cf846612ead626dd30` |
| Strategy in config | Historical reports say same main candidate | `DualTrendCombinedShortPullbackShapeV1Strategy` |
| Trading mode | Historical reports say futures / isolated | `futures` / `isolated` |
| max_open_trades | 3 | 3 |
| dry_run_wallet | 1000 | 1000 |
| stake_amount | Historical reports imply same config, but not directly verifiable | `unlimited` |

Current config key values:

```text
max_open_trades = 3
stake_currency = USDT
stake_amount = unlimited
tradable_balance_ratio = 0.99
dry_run = true
dry_run_wallet = 1000
trading_mode = futures
margin_mode = isolated
enable_protections = true
pairlists = StaticPairList
strategy = DualTrendCombinedShortPullbackShapeV1Strategy
```

No full previous config diff can be produced without the old `D:/test/ft_userdata` artifact.

## 3. localrun Override Fields

The current run used this additional schema-only override:

```json
{
  "api_server": {
    "jwt_secret_key": "positive13_backtest_local_jwt_secret_20260619",
    "ws_token": "positive13_backtest_local_ws_token_20260619"
  }
}
```

It changed only:

| Field | Base config | localrun override |
|---|---|---|
| `api_server.jwt_secret_key` | `CHANGE_ME` | `positive13_backtest_local_jwt_secret_20260619` |
| `api_server.ws_token` | `CHANGE_ME` | `positive13_backtest_local_ws_token_20260619` |

Reason: Freqtrade 2026.5.1 rejects the old short `CHANGE_ME` JWT value during config validation. This override does not change strategy logic, pairlist, stake, timerange, fee, protections, or max open trades.

## 4. Pair Whitelist Comparison

The previous markdown reports list the Positive13 pool as:

```text
ETH, ZEC, BTC, ADA, BNB, SOL, DOGE, XRP, TAO, SUI, PAXG, NEAR, LINK
```

Current config whitelist:

```text
ETH/USDT:USDT
ZEC/USDT:USDT
BTC/USDT:USDT
ADA/USDT:USDT
BNB/USDT:USDT
SOL/USDT:USDT
DOGE/USDT:USDT
XRP/USDT:USDT
TAO/USDT:USDT
SUI/USDT:USDT
PAXG/USDT:USDT
NEAR/USDT:USDT
LINK/USDT:USDT
```

Judgment: pair whitelist appears semantically identical by symbol set. However, exact previous config formatting/order cannot be directly verified because the previous config file is unavailable.

## 5. Timerange Comparison

| Item | Previous reported baseline | Current recheck baseline |
|---|---|---|
| Three-year timerange | `2023-06-18 -> 2026-06-18` | `20230618-20260618` |
| Current zip timerange | Not available | `20230618-20260618` |
| Effective backtest window | Historical report only | `2023-06-18 00:00:00 -> 2026-06-18 00:00:00` |

Judgment: reported timerange is the same.

## 6. Fee / Stake / max_open_trades / Wallet Comparison

| Field | Previous reported baseline | Current recheck baseline |
|---|---|---|
| Fee | Baseline, no special fee override reported | No `--fee`; config has no `fee` key |
| Stake | Not directly verifiable from previous artifact | `stake_amount = unlimited`, `tradable_balance_ratio = 0.99` |
| max_open_trades | 3 | 3 |
| dry_run_wallet | 1000 | 1000 |
| Protections | Historical report says same main candidate/config | `enable_protections = true` |

Judgment: based on reports, these appear intended to be the same. Exact previous values cannot be fully proven without the old zip/config.

## 7. Data Coverage Comparison

Previous run data coverage cannot be directly inspected because the old workspace and zip are unavailable.

Current Positive13 data coverage after this recheck:

| Pair group | Current 1h futures coverage | Current 4h futures coverage | Current 1d futures coverage |
|---|---|---|---|
| ETH, ZEC, BTC, ADA, BNB, SOL, DOGE, XRP | starts 2021-04-17, ends 2026-06-19 00:00 | starts 2023-04-15, ends 2026-06-18 20:00 | starts 2021-04-17, ends 2026-06-18 |
| NEAR, LINK | starts 2025-10-15, ends 2026-06-19 00:00 | starts 2025-10-15, ends 2026-06-18 20:00 | starts 2025-10-15, ends 2026-06-18 |
| TAO, SUI, PAXG | starts 2026-04-18, ends 2026-06-19 00:00 | starts 2026-04-18, ends 2026-06-18 20:00 | starts 2026-04-18, ends 2026-06-18 |

Important observation: TAO, SUI, and PAXG have no usable current data for most of the 2023-06-18 to 2026-06-18 interval. In the current recheck they produced 0 trades. The previous report also showed Positive13 included these symbols, but without the previous zip we cannot verify whether they had any different historical coverage or trades.

## 8. Per-Pair Trade Count Difference

Previous per-pair trade counts are not preserved in the markdown reports, and the previous zip is unavailable. Therefore a true pair-by-pair diff cannot be computed.

Current three-year pair counts:

| Pair | Current trades |
|---|---:|
| ADA/USDT:USDT | 35 |
| BNB/USDT:USDT | 21 |
| BTC/USDT:USDT | 37 |
| DOGE/USDT:USDT | 22 |
| ETH/USDT:USDT | 32 |
| LINK/USDT:USDT | 6 |
| NEAR/USDT:USDT | 8 |
| SOL/USDT:USDT | 27 |
| XRP/USDT:USDT | 40 |
| ZEC/USDT:USDT | 13 |
| TAO/USDT:USDT | 0 |
| SUI/USDT:USDT | 0 |
| PAXG/USDT:USDT | 0 |

Current side/tag counts:

| Bucket | Current trades | Previous reported trades | Difference |
|---|---:|---:|---:|
| Long | 38 | 46 | -8 |
| Short | 203 | 248 | -45 |
| `short_pullback_restart` | 142 | Not preserved | Unknown |
| `short_compression_breakdown` | 61 | Not preserved | Unknown |
| `long_1d_center_compression` | 38 | Not preserved | Unknown |

This shows that most of the missing 53 trades are short trades, not long trades.

## 9. Which Time Periods Lost Trades

Previous month-by-month counts are not preserved in the markdown reports, and the previous zip is unavailable. Therefore exact missing periods cannot be computed.

Current open-month trade counts:

| Month | Current trades |
|---|---:|
| 2023-07 | 1 |
| 2023-08 | 10 |
| 2023-09 | 7 |
| 2023-10 | 4 |
| 2023-11 | 4 |
| 2023-12 | 2 |
| 2024-01 | 8 |
| 2024-02 | 5 |
| 2024-04 | 6 |
| 2024-05 | 5 |
| 2024-06 | 15 |
| 2024-07 | 5 |
| 2024-08 | 6 |
| 2024-09 | 4 |
| 2024-10 | 6 |
| 2024-11 | 5 |
| 2024-12 | 2 |
| 2025-01 | 4 |
| 2025-02 | 13 |
| 2025-03 | 10 |
| 2025-04 | 6 |
| 2025-05 | 5 |
| 2025-06 | 11 |
| 2025-07 | 3 |
| 2025-08 | 6 |
| 2025-09 | 8 |
| 2025-10 | 7 |
| 2025-11 | 11 |
| 2025-12 | 12 |
| 2026-01 | 11 |
| 2026-02 | 11 |
| 2026-03 | 9 |
| 2026-04 | 4 |
| 2026-05 | 6 |
| 2026-06 | 9 |

Because the current total is lower primarily by short trades, the missing trades are likely concentrated in short entry conditions (`short_pullback_restart` / `short_compression_breakdown`) rather than long module removal.

## 10. Final Judgment On Difference Source

The difference is not explained by the items we can verify as identical or effectively identical:

1. Pair pool appears identical: same Positive13 symbols.
2. Timerange appears identical: `2023-06-18 -> 2026-06-18`.
3. max_open_trades is identical: 3.
4. dry_run_wallet is identical: 1000.
5. Current baseline did not use a special fee override.
6. localrun override only changed API token validation fields and should not affect backtest decisions.

The strongest evidence is the trade-count structure:

```text
Previous: 294 trades = 46 long + 248 short
Current:  241 trades = 38 long + 203 short
Diff:     -53 trades = -8 long + -45 short
```

Therefore, the most likely difference source is one of the following:

1. Strategy code drift between the previous `D:/test/ft_userdata` run and the current `D:/work/ft_userdata` run.
2. Historical market data differences between the old workspace and current workspace.
3. Freqtrade version/runtime behavior differences, because the current run used Freqtrade `2026.5.1` and required a config schema override; the previous runtime version is not preserved in the available markdown reports.

Given the missing previous zip/config, the exact root cause cannot be proven yet. The current evidence rules out obvious pairlist/timerange/max3/wallet differences and points toward strategy snapshot, data snapshot, or Freqtrade runtime difference.

## Required Hold

Do not enter max4/max5 extra-trade diagnosis yet.

Do not modify the strategy yet.

Before proceeding, recover or provide the previous artifacts if possible:

```text
D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-49-31.zip
D:/test/ft_userdata/user_data/backtest_results/backtest-result-2026-06-18_06-51-00.zip
D:/test/ft_userdata/user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json
```

With those files, we can produce the missing exact comparisons: previous strategy hash, previous config hash/full diff, exact per-pair trade diff, exact missing-trade timestamps, and definitive root cause.
