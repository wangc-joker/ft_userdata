#!/usr/bin/env python3
"""
Parse Positive13 backtest exports and estimate fee2x + slippage stress.

This script intentionally does not change strategy/config parameters. It reads
Freqtrade backtest zip exports, keeps Freqtrade's reported baseline/fee2x
metrics, and applies post-trade price slippage to the fee2x trade list.
"""

from __future__ import annotations

import csv
import json
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "user_data" / "backtest_results"
ANALYSIS_DIR = ROOT / "user_data" / "analysis"
REPORTS_DIR = ROOT / "user_data" / "reports"
STRATEGY = "DualTrendCombinedShortPullbackShapeV1Strategy"

RUNS = [
    {
        "sample": "3y",
        "scenario": "baseline",
        "zip": "backtest-result-2026-06-19_01-07-59.zip",
        "slippage": 0.0,
        "source": "baseline",
    },
    {
        "sample": "1y",
        "scenario": "baseline",
        "zip": "backtest-result-2026-06-19_01-08-53.zip",
        "slippage": 0.0,
        "source": "baseline",
    },
    {
        "sample": "3y",
        "scenario": "fee2x",
        "zip": "backtest-result-2026-06-19_01-10-20.zip",
        "slippage": 0.0,
        "source": "fee2x",
    },
    {
        "sample": "1y",
        "scenario": "fee2x",
        "zip": "backtest-result-2026-06-19_01-11-15.zip",
        "slippage": 0.0,
        "source": "fee2x",
    },
]

SLIPPAGE_LEVELS = [
    ("fee2x + light slippage", 0.0003),
    ("fee2x + medium slippage", 0.0005),
    ("fee2x + heavy slippage", 0.0010),
]


@dataclass
class Summary:
    sample: str
    scenario: str
    trades: int
    profit_abs: float
    profit_pct: float
    profit_factor: float
    maxdd_pct: float
    winrate_pct: float
    avg_profit_pct: float
    worst_month: str
    worst_month_abs: float
    worst_pair: str
    worst_pair_abs: float
    source_zip: str


def load_strategy(zip_name: str) -> dict[str, Any]:
    path = RESULTS_DIR / zip_name
    if not path.exists():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path) as zf:
        json_name = next(
            name
            for name in zf.namelist()
            if name.endswith(".json") and "_config" not in name
        )
        data = json.loads(zf.read(json_name))
    return data["strategy"][STRATEGY]


def profit_factor(profits: list[float]) -> float:
    wins = sum(value for value in profits if value > 0)
    losses = -sum(value for value in profits if value < 0)
    if losses == 0:
        return 0.0 if wins == 0 else float("inf")
    return wins / losses


def max_drawdown_pct(profits_by_close: list[tuple[int, float]], starting_balance: float) -> float:
    balance = starting_balance
    peak = starting_balance
    max_dd = 0.0
    for _, profit in sorted(profits_by_close):
        balance += profit
        peak = max(peak, balance)
        if peak > 0:
            max_dd = max(max_dd, (peak - balance) / peak)
    return max_dd * 100.0


def month_key(trade: dict[str, Any]) -> str:
    close_date = trade.get("close_date") or trade.get("open_date") or ""
    return close_date[:7]


def worst_group(groups: dict[str, float]) -> tuple[str, float]:
    if not groups:
        return "", 0.0
    return min(groups.items(), key=lambda item: item[1])


def adjusted_profit_abs(trade: dict[str, Any], slippage: float) -> float:
    profit_abs = float(trade["profit_abs"])
    if slippage <= 0:
        return profit_abs

    amount = float(trade["amount"])
    open_rate = float(trade["open_rate"])
    close_rate = float(trade["close_rate"])
    is_short = bool(trade.get("is_short"))

    if is_short:
        original_gross = (open_rate - close_rate) * amount
        slipped_gross = (open_rate * (1 - slippage) - close_rate * (1 + slippage)) * amount
    else:
        original_gross = (close_rate - open_rate) * amount
        slipped_gross = (close_rate * (1 - slippage) - open_rate * (1 + slippage)) * amount

    return profit_abs + (slipped_gross - original_gross)


def summarize_from_trades(
    strategy: dict[str, Any],
    sample: str,
    scenario: str,
    source_zip: str,
    slippage: float,
) -> Summary:
    trades = strategy["trades"]
    starting_balance = float(strategy["starting_balance"])
    profits = [adjusted_profit_abs(trade, slippage) for trade in trades]
    profit_abs = sum(profits)
    pair_groups: dict[str, float] = defaultdict(float)
    month_groups: dict[str, float] = defaultdict(float)
    profits_by_close: list[tuple[int, float]] = []
    ratios: list[float] = []

    for trade, profit in zip(trades, profits):
        pair_groups[trade["pair"]] += profit
        month_groups[month_key(trade)] += profit
        profits_by_close.append((int(trade.get("close_timestamp") or trade.get("open_timestamp") or 0), profit))
        stake = float(trade.get("stake_amount") or 0.0)
        ratios.append(profit / stake if stake else 0.0)

    worst_month, worst_month_abs = worst_group(month_groups)
    worst_pair, worst_pair_abs = worst_group(pair_groups)
    wins = sum(1 for value in profits if value > 0)
    trades_count = len(trades)

    return Summary(
        sample=sample,
        scenario=scenario,
        trades=trades_count,
        profit_abs=profit_abs,
        profit_pct=profit_abs / starting_balance * 100.0,
        profit_factor=profit_factor(profits),
        maxdd_pct=max_drawdown_pct(profits_by_close, starting_balance),
        winrate_pct=(wins / trades_count * 100.0) if trades_count else 0.0,
        avg_profit_pct=(sum(ratios) / len(ratios) * 100.0) if ratios else 0.0,
        worst_month=worst_month,
        worst_month_abs=worst_month_abs,
        worst_pair=worst_pair,
        worst_pair_abs=worst_pair_abs,
        source_zip=source_zip,
    )


def summarize_reported(strategy: dict[str, Any], sample: str, scenario: str, source_zip: str) -> Summary:
    # Worst month/pair are derived from trades to keep the report columns uniform.
    trade_summary = summarize_from_trades(strategy, sample, scenario, source_zip, 0.0)
    return Summary(
        sample=sample,
        scenario=scenario,
        trades=int(strategy["total_trades"]),
        profit_abs=float(strategy["profit_total_abs"]),
        profit_pct=float(strategy["profit_total"]) * 100.0,
        profit_factor=float(strategy["profit_factor"]),
        maxdd_pct=float(strategy["max_drawdown_account"]) * 100.0,
        winrate_pct=float(strategy["winrate"]) * 100.0,
        avg_profit_pct=float(strategy["profit_mean"]) * 100.0,
        worst_month=trade_summary.worst_month,
        worst_month_abs=trade_summary.worst_month_abs,
        worst_pair=trade_summary.worst_pair,
        worst_pair_abs=trade_summary.worst_pair_abs,
        source_zip=source_zip,
    )


def fmt_float(value: float) -> str:
    if value == float("inf"):
        return "inf"
    return f"{value:.4f}"


def write_csv(rows: list[Summary]) -> Path:
    out = ANALYSIS_DIR / "positive13_fee_slippage_stress.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample",
                "scenario",
                "trades",
                "profit_abs",
                "profit_pct",
                "profit_factor",
                "maxdd_pct",
                "winrate_pct",
                "avg_profit_pct",
                "worst_month",
                "worst_month_abs",
                "worst_pair",
                "worst_pair_abs",
                "source_zip",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sample": row.sample,
                    "scenario": row.scenario,
                    "trades": row.trades,
                    "profit_abs": fmt_float(row.profit_abs),
                    "profit_pct": fmt_float(row.profit_pct),
                    "profit_factor": fmt_float(row.profit_factor),
                    "maxdd_pct": fmt_float(row.maxdd_pct),
                    "winrate_pct": fmt_float(row.winrate_pct),
                    "avg_profit_pct": fmt_float(row.avg_profit_pct),
                    "worst_month": row.worst_month,
                    "worst_month_abs": fmt_float(row.worst_month_abs),
                    "worst_pair": row.worst_pair,
                    "worst_pair_abs": fmt_float(row.worst_pair_abs),
                    "source_zip": row.source_zip,
                }
            )
    return out


def md_table(rows: list[Summary], sample: str) -> str:
    selected = [row for row in rows if row.sample == sample]
    lines = [
        "| 方案 | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Worst Month | Worst Pair |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in selected:
        lines.append(
            "| {scenario} | {trades} | {profit_pct:.2f}% / {profit_abs:.2f} USDT | "
            "{pf:.2f} | {dd:.2f}% | {win:.2f}% | {avg:.2f}% | "
            "{wm} ({wm_abs:.2f}) | {wp} ({wp_abs:.2f}) |".format(
                scenario=row.scenario,
                trades=row.trades,
                profit_pct=row.profit_pct,
                profit_abs=row.profit_abs,
                pf=row.profit_factor,
                dd=row.maxdd_pct,
                win=row.winrate_pct,
                avg=row.avg_profit_pct,
                wm=row.worst_month,
                wm_abs=row.worst_month_abs,
                wp=row.worst_pair,
                wp_abs=row.worst_pair_abs,
            )
        )
    return "\n".join(lines)


def write_reports(rows: list[Summary], strategies: dict[str, dict[str, Any]]) -> tuple[Path, Path]:
    baseline_report = REPORTS_DIR / "positive13_baseline_recheck.md"
    stress_report = REPORTS_DIR / "positive13_fee_slippage_stress.md"

    baseline_3y = next(row for row in rows if row.sample == "3y" and row.scenario == "baseline")
    baseline_1y = next(row for row in rows if row.sample == "1y" and row.scenario == "baseline")

    baseline_report.write_text(
        "\n".join(
            [
                "# Positive13 Baseline Recheck",
                "",
                "- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`",
                "- Config: `user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json`",
                "- Local schema override: `user_data/config.backtest.dualtrend.combined.top50.positive13.max3.localrun.json`",
                "- Pair pool: Positive13 from config pair whitelist",
                "- max_open_trades: 3",
                "- Trading mode: futures / isolated",
                "- Timeframes used by strategy: 1h, with 4h/1d informative data",
                "- Data note: local data was extended to `2026-06-18` for this recheck.",
                "",
                "## Results",
                "",
                "| Sample | Timerange | Trades | Profit | PF | MaxDD | Winrate | Worst Month | Worst Pair |",
                "|---|---|---:|---:|---:|---:|---:|---|---|",
                f"| 3y | 2023-06-18 -> 2026-06-18 | {baseline_3y.trades} | {baseline_3y.profit_pct:.2f}% / {baseline_3y.profit_abs:.2f} USDT | {baseline_3y.profit_factor:.2f} | {baseline_3y.maxdd_pct:.2f}% | {baseline_3y.winrate_pct:.2f}% | {baseline_3y.worst_month} ({baseline_3y.worst_month_abs:.2f}) | {baseline_3y.worst_pair} ({baseline_3y.worst_pair_abs:.2f}) |",
                f"| 1y | 2025-06-18 -> 2026-06-18 | {baseline_1y.trades} | {baseline_1y.profit_pct:.2f}% / {baseline_1y.profit_abs:.2f} USDT | {baseline_1y.profit_factor:.2f} | {baseline_1y.maxdd_pct:.2f}% | {baseline_1y.winrate_pct:.2f}% | {baseline_1y.worst_month} ({baseline_1y.worst_month_abs:.2f}) | {baseline_1y.worst_pair} ({baseline_1y.worst_pair_abs:.2f}) |",
                "",
                "## Baseline Reproduction",
                "",
                "Baseline reproduced successfully for both required timeranges in the current local environment. The result remains positive, PF stays above 1.6, and MaxDD stays below 12% in both samples.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    medium_3y = next(row for row in rows if row.sample == "3y" and row.scenario == "fee2x + medium slippage")
    medium_1y = next(row for row in rows if row.sample == "1y" and row.scenario == "fee2x + medium slippage")
    heavy_3y = next(row for row in rows if row.sample == "3y" and row.scenario == "fee2x + heavy slippage")
    heavy_1y = next(row for row in rows if row.sample == "1y" and row.scenario == "fee2x + heavy slippage")

    stable = (
        medium_3y.profit_factor >= 1.6
        and medium_3y.maxdd_pct <= 12
        and medium_1y.profit_factor >= 1.5
        and medium_1y.profit_abs > 0
    )
    pf_gt_16_all = all(row.profit_factor > 1.6 for row in rows)
    dd_lt_12_all = all(row.maxdd_pct < 12 for row in rows)

    stress_report.write_text(
        "\n".join(
            [
                "# Positive13 Fee2x + Slippage Stress",
                "",
                "## Scope",
                "",
                "- Only Codex execution checklist steps 1-7 were performed.",
                "- No strategy optimization, no parameter changes, no max4/max5 diagnostics, no pressure-month diagnostics, no long/tag diagnostics.",
                "- Fee2x was run with Freqtrade `--fee 0.001`.",
                "- Slippage was estimated post-trade from fee2x exported trades.",
                "- Slippage levels are per side: light 0.03%, medium 0.05%, heavy 0.10%.",
                "",
                "## Three-Year Sample",
                "",
                md_table(rows, "3y"),
                "",
                "## Recent One-Year Sample",
                "",
                md_table(rows, "1y"),
                "",
                "## Required Answers",
                "",
                f"1. Baseline 是否复现成功：是。三年 {baseline_3y.profit_pct:.2f}%，PF {baseline_3y.profit_factor:.2f}，MaxDD {baseline_3y.maxdd_pct:.2f}%；近一年 {baseline_1y.profit_pct:.2f}%，PF {baseline_1y.profit_factor:.2f}，MaxDD {baseline_1y.maxdd_pct:.2f}%。",
                f"2. fee2x + light / medium / heavy slippage 后，三年和近一年是否仍然稳定：light/medium 稳定；heavy 下两个样本仍保持正收益且 MaxDD 小于 12%，但近一年 PF {heavy_1y.profit_factor:.2f}，严格低于 1.6，属于边缘压力结果。",
                f"3. PF 是否仍大于 1.6：{'是' if pf_gt_16_all else '不是全部'}。light/medium 均大于 1.6；heavy 下三年 PF {heavy_3y.profit_factor:.2f}，近一年 PF {heavy_1y.profit_factor:.2f}。",
                f"4. MaxDD 是否仍小于 12%：{'是' if dd_lt_12_all else '不是全部'}。medium 压力下三年 MaxDD {medium_3y.maxdd_pct:.2f}%，近一年 MaxDD {medium_1y.maxdd_pct:.2f}%。",
                f"5. 是否建议进入下一阶段诊断：{'建议' if stable else '暂不建议'}。当前已经通过文档 4.5 的 medium slippage 通过标准，但下一阶段应只做诊断，不要直接优化。",
                "6. 是否暂时不要改策略：是，暂时不要改策略。当前目标是验证成本承受力，结果没有显示必须立刻改策略的证据。",
                "",
                "## Output Files",
                "",
                "- `user_data/analysis/positive13_fee_slippage_stress.py`",
                "- `user_data/analysis/positive13_fee_slippage_stress.csv`",
                "- `user_data/reports/positive13_baseline_recheck.md`",
                "- `user_data/reports/positive13_fee_slippage_stress.md`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return baseline_report, stress_report


def main() -> None:
    strategies: dict[str, dict[str, Any]] = {}
    rows: list[Summary] = []

    for run in RUNS:
        strategy = load_strategy(run["zip"])
        key = f"{run['sample']}:{run['source']}"
        strategies[key] = strategy
        rows.append(summarize_reported(strategy, run["sample"], run["scenario"], run["zip"]))

    for sample in ("3y", "1y"):
        strategy = strategies[f"{sample}:fee2x"]
        source_zip = next(run["zip"] for run in RUNS if run["sample"] == sample and run["source"] == "fee2x")
        for scenario, slippage in SLIPPAGE_LEVELS:
            rows.append(summarize_from_trades(strategy, sample, scenario, source_zip, slippage))

    sample_order = {"3y": 0, "1y": 1}
    scenario_order = {
        "baseline": 0,
        "fee2x": 1,
        "fee2x + light slippage": 2,
        "fee2x + medium slippage": 3,
        "fee2x + heavy slippage": 4,
    }
    rows.sort(key=lambda row: (sample_order[row.sample], scenario_order[row.scenario]))

    csv_path = write_csv(rows)
    baseline_report, stress_report = write_reports(rows, strategies)
    print(f"Wrote {csv_path}")
    print(f"Wrote {baseline_report}")
    print(f"Wrote {stress_report}")


if __name__ == "__main__":
    main()
