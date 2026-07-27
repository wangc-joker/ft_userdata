# Side-Slot Audit

## Full-run metrics

| run | max_open | trades | longs | shorts | profit_pct | profit_abs | profit_factor | maxdd_account_pct | long_profit_abs | short_profit_abs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| max3_current | 3 | 481 | 59 | 422 | 277.368 | 2773.680 | 2.429 | 4.778 | 707.240 | 2066.440 |
| max4_unrestricted | 4 | 514 | 59 | 455 | 273.472 | 2734.723 | 2.344 | 5.288 | 707.404 | 2027.318 |
| max4_3short_1long | 4 | 470 | 42 | 428 | 206.542 | 2065.422 | 2.172 | 4.785 | 289.221 | 1776.202 |

## Entry tags

| run | side | enter_tag | trades | wins | profit_abs | profit_factor |
| --- | --- | --- | --- | --- | --- | --- |
| max3_current | long | long_1d_center_compression | 52 | 15 | 630.978 | 3.897 |
| max3_current | long | long_pullback_restart_1h_body | 7 | 3 | 76.262 | 3.364 |
| max3_current | short | short_compression_breakdown | 101 | 46 | 417.569 | 2.012 |
| max3_current | short | short_pullback_restart | 321 | 184 | 1648.871 | 2.290 |
| max4_unrestricted | long | long_1d_center_compression | 52 | 15 | 630.372 | 3.886 |
| max4_unrestricted | long | long_pullback_restart_1h_body | 7 | 3 | 77.033 | 3.399 |
| max4_unrestricted | short | short_compression_breakdown | 110 | 50 | 338.700 | 1.714 |
| max4_unrestricted | short | short_pullback_restart | 345 | 202 | 1688.618 | 2.289 |
| max4_3short_1long | long | long_1d_center_compression | 35 | 7 | 216.748 | 2.431 |
| max4_3short_1long | long | long_pullback_restart_1h_body | 7 | 3 | 72.472 | 3.490 |
| max4_3short_1long | short | short_compression_breakdown | 103 | 46 | 329.046 | 1.833 |
| max4_3short_1long | short | short_pullback_restart | 325 | 186 | 1447.155 | 2.219 |

## Calendar years

| run | year | trades | profit_abs | profit_factor |
| --- | --- | --- | --- | --- |
| max3_current | 2021 | 31 | -63.910 | 0.292 |
| max3_current | 2022 | 92 | 169.532 | 1.677 |
| max3_current | 2023 | 84 | 100.371 | 1.366 |
| max3_current | 2024 | 90 | 629.805 | 2.898 |
| max3_current | 2025 | 129 | 1005.886 | 2.441 |
| max3_current | 2026 | 55 | 931.997 | 4.152 |
| max4_unrestricted | 2021 | 32 | -64.557 | 0.290 |
| max4_unrestricted | 2022 | 98 | 166.226 | 1.642 |
| max4_unrestricted | 2023 | 88 | 116.160 | 1.418 |
| max4_unrestricted | 2024 | 94 | 605.600 | 2.765 |
| max4_unrestricted | 2025 | 139 | 1018.983 | 2.391 |
| max4_unrestricted | 2026 | 63 | 892.311 | 3.691 |
| max4_3short_1long | 2021 | 30 | -60.943 | 0.303 |
| max4_3short_1long | 2022 | 92 | 170.386 | 1.678 |
| max4_3short_1long | 2023 | 81 | 117.925 | 1.457 |
| max4_3short_1long | 2024 | 85 | 412.511 | 2.301 |
| max4_3short_1long | 2025 | 127 | 674.426 | 2.107 |
| max4_3short_1long | 2026 | 55 | 751.117 | 4.131 |

## Executed-trade set differences

Trade identity uses `pair + side + enter_tag + exact open_date`. Attributed profit is the
archived profit of the run containing that trade and is not a counterfactual portfolio delta.

| comparison | difference | side | trades | profit_abs_attributed | profit_factor |
| --- | --- | --- | --- | --- | --- |
| max4_3short_1long_vs_max3 | base_only | long | 17 | 379.084 | 8.159 |
| max4_3short_1long_vs_max3 | candidate_only | short | 6 | -13.044 | 0.612 |
| max4_unrestricted_vs_max3 | base_only | short | 4 | -25.145 | 0.000 |
| max4_unrestricted_vs_max3 | candidate_only | short | 37 | -22.399 | 0.828 |
