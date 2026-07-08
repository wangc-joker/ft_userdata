# DualTrend CloseGuard 加仓逐笔对比

- baseline: `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`
- candidate: `DualTrendCompressionCloseQualityGuard028PyramidEarlyWide25CloseGuardStrategy`
- baseline trades: `319`
- candidate trades: `318`
- common keyed trades: `318`
- baseline-only trades: `1`
- candidate-only trades: `0`

## short_pullback_restart

- matched trades: `206`
- improved trades: `101`
- worsened trades: `71`
- unchanged trades: `34`
- trades with extra order(s): `65`
- gross improvement: `194.323 USDT`
- gross worsening: `-77.787 USDT`
- net delta: `116.536 USDT`

## Pair Delta

- `XRP/USDT:USDT`: `74.087 USDT`
- `DOGE/USDT:USDT`: `15.915 USDT`
- `BNB/USDT:USDT`: `15.298 USDT`
- `ETH/USDT:USDT`: `14.400 USDT`
- `SUI/USDT:USDT`: `9.017 USDT`
- `LINK/USDT:USDT`: `5.075 USDT`
- `BTC/USDT:USDT`: `4.046 USDT`
- `ZEC/USDT:USDT`: `0.857 USDT`
- `ADA/USDT:USDT`: `-1.497 USDT`
- `SOL/USDT:USDT`: `-2.066 USDT`
- `NEAR/USDT:USDT`: `-2.765 USDT`
- `TAO/USDT:USDT`: `-15.830 USDT`

## Best Delta Trades

- `XRP/USDT:USDT` `2026-01-22 14:00:00+00:00`: `47.429 USDT` (trailing_stop_loss -> partial_exit, orders 2->3)
- `XRP/USDT:USDT` `2026-02-22 13:00:00+00:00`: `11.143 USDT` (partial_exit -> partial_exit, orders 2->3)
- `BNB/USDT:USDT` `2026-04-01 14:00:00+00:00`: `10.687 USDT` (partial_exit -> partial_exit, orders 2->3)
- `XRP/USDT:USDT` `2025-11-20 16:00:00+00:00`: `7.701 USDT` (partial_exit -> partial_exit, orders 2->3)
- `SUI/USDT:USDT` `2025-01-26 21:00:00+00:00`: `7.337 USDT` (partial_exit -> partial_exit, orders 2->3)
- `ETH/USDT:USDT` `2025-04-05 13:00:00+00:00`: `6.976 USDT` (partial_exit -> partial_exit, orders 2->3)
- `ETH/USDT:USDT` `2025-11-20 16:00:00+00:00`: `6.727 USDT` (partial_exit -> partial_exit, orders 2->3)
- `SUI/USDT:USDT` `2025-09-25 01:00:00+00:00`: `5.622 USDT` (partial_exit -> partial_exit, orders 2->3)
- `TAO/USDT:USDT` `2026-01-29 02:00:00+00:00`: `5.454 USDT` (partial_exit -> partial_exit, orders 2->3)
- `DOGE/USDT:USDT` `2026-02-10 07:00:00+00:00`: `4.964 USDT` (partial_exit -> partial_exit, orders 2->3)

## Worst Delta Trades

- `TAO/USDT:USDT` `2026-01-25 05:00:00+00:00`: `-13.026 USDT` (partial_exit -> partial_exit, orders 2->2)
- `TAO/USDT:USDT` `2024-06-10 05:00:00+00:00`: `-12.463 USDT` (partial_exit -> trailing_stop_loss, orders 2->3)
- `SOL/USDT:USDT` `2023-08-24 15:00:00+00:00`: `-10.788 USDT` (partial_exit -> trailing_stop_loss, orders 2->3)
- `BNB/USDT:USDT` `2026-03-22 00:00:00+00:00`: `-7.176 USDT` (stop_loss -> trailing_stop_loss, orders 2->3)
- `ZEC/USDT:USDT` `2026-01-23 08:00:00+00:00`: `-5.504 USDT` (trailing_stop_loss -> trailing_stop_loss, orders 2->3)
- `SUI/USDT:USDT` `2025-09-24 04:00:00+00:00`: `-4.262 USDT` (stop_loss -> trailing_stop_loss, orders 2->3)
- `ADA/USDT:USDT` `2025-06-02 09:00:00+00:00`: `-4.259 USDT` (stop_loss -> trailing_stop_loss, orders 2->3)
- `LINK/USDT:USDT` `2024-10-13 15:00:00+00:00`: `-3.073 USDT` (stop_loss -> trailing_stop_loss, orders 2->3)
- `ADA/USDT:USDT` `2024-06-02 18:00:00+00:00`: `-2.907 USDT` (trailing_stop_loss -> trailing_stop_loss, orders 2->3)
- `NEAR/USDT:USDT` `2023-08-22 18:00:00+00:00`: `-2.481 USDT` (stop_loss -> trailing_stop_loss, orders 2->3)