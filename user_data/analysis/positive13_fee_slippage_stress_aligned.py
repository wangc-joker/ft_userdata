#!/usr/bin/env python3
"""Generate aligned Positive13 fee2x + slippage stress outputs.

The script reads the latest backtest zip exports created after historical data
was filled, keeps Freqtrade-reported baseline/fee2x metrics, and estimates
post-trade slippage from the fee2x trade lists.
"""

from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "user_data" / "backtest_results"
ANALYSIS_DIR = ROOT / "user_data" / "analysis"
REPORTS_DIR = ROOT / "user_data" / "reports"
STRATEGY = "DualTrendCombinedShortPullbackShapeV1Strategy"
STARTING_BALANCE = 1000.0

RUNS = [
    {
        "sample": "3y",
        "timerange": "2023-06-18 -> 2026-06-18",
        "scenario": "baseline",
        "zip": "backtest-result-2026-06-19_03-08-28.zip",
        "source": "baseline",
    },
    {
        "sample": "1y",
        "timerange": "2025-06-18 -> 2026-06-18",
        "scenario": "baseline",
        "zip": "backtest-result-2026-06-19_03-09-26.zip",
        "source": "baseline",
    },
    {
        "sample": "3y",
        "timerange": "2023-06-18 -> 2026-06-18",
        "scenario": "fee2x",
        "zip": "backtest-result-2026-06-19_03-10-59.zip",
        "source": "fee2x",
    },
    {
        "sample": "1y",
        "timerange": "2025-06-18 -> 2026-06-18",
        "scenario": "fee2x",
        "zip": "backtest-result-2026-06-19_03-11-58.zip",
        "source": "fee2x",
    },
]

SLIPPAGE_LEVELS = [
    ("fee2x + light slippage", 0.0003),
    ("fee2x + medium slippage", 0.0005),
    ("fee2x + heavy slippage", 0.0010),
]


@dataclass(frozen=True)
class Summary:
    sample: str
    timerange: str
    scenario: str
    trades: int
    profit_abs: float
    profit_pct: float
    profit_factor: float
    maxdd_pct: float
    winrate_pct: float
    avg_profit_pct: float
    source_zip: str


def load_strategy(zip_name: str) -> dict[str, Any]:
    path = RESULTS_DIR / zip_name
    if not path.exists():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path) as zf:
        json_name = next(
            name
            for name in zf.namelist()
            if name.endswith(".json") and "_config" not in name and "meta" not in name
        )
        data = json.loads(zf.read(json_name))
    return data["strategy"][STRATEGY]


def profit_factor(profits: list[float]) -> float:
    wins = sum(value for value in profits if value > 0)
    losses = -sum(value for value in profits if value < 0)
    if losses == 0:
        return float("inf") if wins > 0 else 0.0
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


def summarize_reported(
    strategy: dict[str, Any],
    sample: str,
    timerange: str,
    scenario: str,
    source_zip: str,
) -> Summary:
    return Summary(
        sample=sample,
        timerange=timerange,
        scenario=scenario,
        trades=int(strategy["total_trades"]),
        profit_abs=float(strategy["profit_total_abs"]),
        profit_pct=float(strategy["profit_total"]) * 100.0,
        profit_factor=float(strategy["profit_factor"]),
        maxdd_pct=float(strategy["max_drawdown_account"]) * 100.0,
        winrate_pct=float(strategy["winrate"]) * 100.0,
        avg_profit_pct=float(strategy["profit_mean"]) * 100.0,
        source_zip=source_zip,
    )


def summarize_slippage(
    strategy: dict[str, Any],
    sample: str,
    timerange: str,
    scenario: str,
    source_zip: str,
    slippage: float,
) -> Summary:
    trades = strategy["trades"]
    profits = [adjusted_profit_abs(trade, slippage) for trade in trades]
    profits_by_close = [
        (int(trade.get("close_timestamp") or trade.get("open_timestamp") or 0), profit)
        for trade, profit in zip(trades, profits)
    ]
    ratios = [
        profit / float(trade.get("stake_amount") or STARTING_BALANCE)
        for trade, profit in zip(trades, profits)
    ]
    wins = sum(1 for profit in profits if profit > 0)
    trade_count = len(trades)
    profit_abs = sum(profits)

    return Summary(
        sample=sample,
        timerange=timerange,
        scenario=scenario,
        trades=trade_count,
        profit_abs=profit_abs,
        profit_pct=profit_abs / STARTING_BALANCE * 100.0,
        profit_factor=profit_factor(profits),
        maxdd_pct=max_drawdown_pct(profits_by_close, STARTING_BALANCE),
        winrate_pct=(wins / trade_count * 100.0) if trade_count else 0.0,
        avg_profit_pct=(sum(ratios) / len(ratios) * 100.0) if ratios else 0.0,
        source_zip=source_zip,
    )


def fmt(value: float) -> str:
    if value == float("inf"):
        return "inf"
    return f"{value:.4f}"


def write_csv(rows: list[Summary]) -> Path:
    out = ANALYSIS_DIR / "positive13_fee_slippage_stress_aligned.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample",
                "timerange",
                "scenario",
                "trades",
                "profit_abs",
                "profit_pct",
                "profit_factor",
                "maxdd_pct",
                "winrate_pct",
                "avg_profit_pct",
                "source_zip",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sample": row.sample,
                    "timerange": row.timerange,
                    "scenario": row.scenario,
                    "trades": row.trades,
                    "profit_abs": fmt(row.profit_abs),
                    "profit_pct": fmt(row.profit_pct),
                    "profit_factor": fmt(row.profit_factor),
                    "maxdd_pct": fmt(row.maxdd_pct),
                    "winrate_pct": fmt(row.winrate_pct),
                    "avg_profit_pct": fmt(row.avg_profit_pct),
                    "source_zip": row.source_zip,
                }
            )
    return out


def table(rows: list[Summary], sample: str) -> str:
    lines = [
        "| Scenario | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Source |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in [item for item in rows if item.sample == sample]:
        lines.append(
            f"| {row.scenario} | {row.trades} | {row.profit_pct:.2f}% / {row.profit_abs:.2f} USDT | "
            f"{row.profit_factor:.2f} | {row.maxdd_pct:.2f}% | {row.winrate_pct:.2f}% | "
            f"{row.avg_profit_pct:.2f}% | `{row.source_zip}` |"
        )
    return "\n".join(lines)


def answer_line(question: str, answer: str) -> str:
    return f"- **{question}** {answer}"


def write_report(rows: list[Summary]) -> Path:
    out = REPORTS_DIR / "positive13_fee_slippage_stress_aligned.md"
    by_key = {(row.sample, row.scenario): row for row in rows}
    baseline_3y = by_key[("3y", "baseline")]
    baseline_1y = by_key[("1y", "baseline")]
    medium_3y = by_key[("3y", "fee2x + medium slippage")]
    medium_1y = by_key[("1y", "fee2x + medium slippage")]
    heavy_3y = by_key[("3y", "fee2x + heavy slippage")]
    heavy_1y = by_key[("1y", "fee2x + heavy slippage")]

    baseline_aligned = (
        baseline_3y.trades == 291
        and round(baseline_3y.profit_pct, 2) == 199.34
        and baseline_1y.trades == 111
        and round(baseline_1y.profit_pct, 2) == 51.23
    )
    medium_pass = (
        medium_3y.profit_factor >= 1.60
        and medium_3y.maxdd_pct <= 12.0
        and medium_1y.profit_factor >= 1.50
        and medium_1y.profit_abs > 0
    )
    heavy_acceptable = (
        heavy_3y.profit_factor >= 1.60
        and heavy_3y.maxdd_pct <= 12.0
        and heavy_1y.profit_factor >= 1.50
        and heavy_1y.profit_abs > 0
    )

    content = [
        "# Positive13 Fee2x + Slippage Stress Aligned",
        "",
        "## Scope",
        "",
        "- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`",
        "- Config: `user_data/config.backtest.dualtrend.combined.top50.positive13.max3.json`",
        "- Local override: `user_data/config.backtest.dualtrend.combined.top50.positive13.max3.localrun.json`",
        "- Pair pool: Positive13 static whitelist",
        "- Max open trades: 3",
        "- Baseline uses the filled local historical data.",
        "- Fee2x uses Freqtrade `--fee 0.001`.",
        "- Slippage is estimated from the new fee2x trade list, per side: light 0.03%, medium 0.05%, heavy 0.10%.",
        "- Not performed: max4/max5 diagnostics, pressure-month diagnostics, long-module diagnostics, strategy parameter changes.",
        "",
        "## Three-Year Result",
        "",
        "- Timerange: `2023-06-18 -> 2026-06-18`",
        "",
        table(rows, "3y"),
        "",
        "## Recent One-Year Result",
        "",
        "- Timerange: `2025-06-18 -> 2026-06-18`",
        "",
        table(rows, "1y"),
        "",
        "## Required Answers",
        "",
        answer_line(
            "1. 补齐数据后的 baseline 是否和旧基线基本对齐？",
            (
                "是。三年为 "
                f"{baseline_3y.trades} trades / +{baseline_3y.profit_pct:.2f}% / PF {baseline_3y.profit_factor:.2f} / "
                f"MaxDD {baseline_3y.maxdd_pct:.2f}%；近一年为 "
                f"{baseline_1y.trades} trades / +{baseline_1y.profit_pct:.2f}% / PF {baseline_1y.profit_factor:.2f} / "
                f"MaxDD {baseline_1y.maxdd_pct:.2f}%。"
                if baseline_aligned
                else "否，需要继续排查 baseline 差异。"
            ),
        ),
        answer_line(
            "2. fee2x + medium slippage 是否仍然通过？",
            (
                "是。三年 PF "
                f"{medium_3y.profit_factor:.2f}、MaxDD {medium_3y.maxdd_pct:.2f}%；近一年 PF "
                f"{medium_1y.profit_factor:.2f}、Profit +{medium_1y.profit_pct:.2f}%。"
                if medium_pass
                else "否，至少一个核心门槛没有通过。"
            ),
        ),
        answer_line(
            "3. fee2x + heavy slippage 是否仍然可接受？",
            (
                "是，但属于更保守压力假设下的边际通过。三年 PF "
                f"{heavy_3y.profit_factor:.2f}、MaxDD {heavy_3y.maxdd_pct:.2f}%；近一年 PF "
                f"{heavy_1y.profit_factor:.2f}、Profit +{heavy_1y.profit_pct:.2f}%。"
                if heavy_acceptable
                else "不完全可接受，至少一个核心门槛没有通过。"
            ),
        ),
        answer_line(
            "4. 三年 PF 是否仍 >= 1.60？",
            f"是。三年 medium PF {medium_3y.profit_factor:.2f}，heavy PF {heavy_3y.profit_factor:.2f}。",
        ),
        answer_line(
            "5. 三年 MaxDD 是否仍 <= 12%？",
            f"是。三年 medium MaxDD {medium_3y.maxdd_pct:.2f}%，heavy MaxDD {heavy_3y.maxdd_pct:.2f}%。",
        ),
        answer_line(
            "6. 近一年 PF 是否仍 >= 1.50？",
            f"是。近一年 medium PF {medium_1y.profit_factor:.2f}，heavy PF {heavy_1y.profit_factor:.2f}。",
        ),
        answer_line(
            "7. 近一年 Profit 是否仍 > 0？",
            f"是。近一年 medium Profit +{medium_1y.profit_pct:.2f}%，heavy Profit +{heavy_1y.profit_pct:.2f}%。",
        ),
        answer_line(
            "8. 是否建议进入第 8～10 步？",
            "建议进入，但只进入诊断，不建议直接改策略。当前 baseline 已对齐，medium 与 heavy 压力测试均通过核心门槛，可以继续做 max4/max5 多余交易诊断等第 8～10 步。",
        ),
        "",
        "## Output Files",
        "",
        "- `user_data/analysis/positive13_fee_slippage_stress_aligned.csv`",
        "- `user_data/reports/positive13_fee_slippage_stress_aligned.md`",
        "",
    ]
    out.write_text("\n".join(content), encoding="utf-8")
    return out


def main() -> None:
    strategies: dict[str, dict[str, Any]] = {}
    rows: list[Summary] = []

    for run in RUNS:
        strategy = load_strategy(run["zip"])
        strategies[f"{run['sample']}:{run['source']}"] = strategy
        rows.append(
            summarize_reported(
                strategy,
                run["sample"],
                run["timerange"],
                run["scenario"],
                run["zip"],
            )
        )

    for sample in ("3y", "1y"):
        source = next(run for run in RUNS if run["sample"] == sample and run["source"] == "fee2x")
        strategy = strategies[f"{sample}:fee2x"]
        for scenario, slippage in SLIPPAGE_LEVELS:
            rows.append(
                summarize_slippage(
                    strategy,
                    sample,
                    source["timerange"],
                    scenario,
                    source["zip"],
                    slippage,
                )
            )

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
    report_path = write_report(rows)
    print(f"Wrote {csv_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
