# DualTrend Collision Opportunity Cost

> Generated 2026-07-27T04:05:01.047702+00:00 from the constrained archive and exact matched collision episodes.

## Scope

- Strategy: `DualTrendPyramidSecondAdd20LongMicroV1Strategy`
- Backtest range: `2021-07-29 16:00:00 -> 2026-06-18 00:00:00`
- Constrained trades: `481`
- Matched rejected episodes: `80` across `56` collision timestamps
- Admission-addressable timestamps: `26`
- Older-occupants-only timestamps: `30`

A timestamp is admission-addressable only when at least one constrained trade opened on the same candle. Older-only collisions cannot be fixed by tag ordering; they require an explicit preemption or early-exit rule.

## Same-candle Ranking

The tested local rule applies only to all-short candidate pools: `short_pullback_restart` before `short_compression_breakdown`, then the archived whitelist order. Mixed long/short pools are excluded because no cross-direction priority was prespecified.

- Evaluable all-short timestamps: `26`
- Timestamps whose selected pairs would change: `3`
- Sum of local selected-trade return deltas: `-1.06%`
- Oracle upper-bound delta across addressable timestamps: `+47.92%`

| Year | Evaluable | Changed | Pullback-first delta |
|---:|---:|---:|---:|
| 2021 | 2 | 1 | +0.12% |
| 2022 | 5 | 0 | +0.00% |
| 2023 | 4 | 0 | +0.00% |
| 2024 | 3 | 1 | -1.34% |
| 2025 | 8 | 1 | +0.16% |
| 2026 | 4 | 0 | +0.00% |

These deltas are one-step static comparisons of known trade outcomes. Replacing a trade changes later occupancy, stake sizing, protections, and possibly future signals, so the sum is not a portfolio-return estimate.

## Occupant Remaining Value

- Occupant valuations completed: `240 / 240`
- Rejected candidate beat the hindsight-weakest occupant by realized remaining value: `54 / 80` valued episodes
- Rejected candidate beat the hindsight-weakest older occupant: `43 / 72` comparable episodes

Remaining value is the fee-adjusted cash-flow difference between holding the actual trade through its recorded future entries/exits and closing it at the collision 5m candle open, normalized by current notional. Funding is not reconstructed. This is a diagnostic ranking signal, not a replacement backtest.

## Older-position Preemption

Each older-only timestamp permits at most one static replacement. The candidate is selected with the same pullback-first short rule; mixed-direction timestamps are excluded. Victims are chosen only from information visible at the collision: either the worst marked return or the oldest open time.

- Evaluable older-only timestamps: `29`
- Worst-current-return victim: `13 / 29` positive local deltas, sum `+8.31%`
- Worst-current-return median delta: `-0.28%`; sum after removing the single best event: `-3.05%`
- Oldest-position victim: `10 / 29` positive local deltas, sum `-16.87%`

| Year | Evaluable | Worst-mark positive | Worst-mark delta | Oldest delta |
|---:|---:|---:|---:|---:|
| 2022 | 5 | 2 | -0.42% | -6.27% |
| 2023 | 2 | 1 | +9.64% | -3.02% |
| 2024 | 5 | 1 | -6.14% | +4.30% |
| 2025 | 7 | 3 | -0.34% | -4.98% |
| 2026 | 10 | 6 | +5.56% | -6.90% |

## Decision

Do not change live admission or preempt existing positions from this analysis alone. A ranking rule is promotable only if its gains are reasonably distributed across years and it survives a full stateful backtest that propagates replacement effects.
