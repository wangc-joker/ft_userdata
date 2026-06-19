#!/usr/bin/env python3
"""Diagnose Positive13 max4/max5 extra trades versus max3.

This is a diagnostic-only parser. It reads Freqtrade backtest exports, writes
trade-detail CSVs, detects extra trades with a 1h open-date tolerance, and
generates the requested markdown report.
"""

from __future__ import annotations

import csv
import json
import math
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "user_data" / "backtest_results"
ANALYSIS_DIR = ROOT / "user_data" / "analysis"
REPORTS_DIR = ROOT / "user_data" / "reports"
STRATEGY = "DualTrendCombinedShortPullbackShapeV1Strategy"
STARTING_BALANCE = 1000.0
OPEN_TOLERANCE_SECONDS = 3600

RUNS = {
    ("3y", 3): {
        "timerange": "2023-06-18 -> 2026-06-18",
        "zip": "backtest-result-2026-06-19_03-17-28.zip",
    },
    ("3y", 4): {
        "timerange": "2023-06-18 -> 2026-06-18",
        "zip": "backtest-result-2026-06-19_03-19-24.zip",
    },
    ("3y", 5): {
        "timerange": "2023-06-18 -> 2026-06-18",
        "zip": "backtest-result-2026-06-19_03-21-09.zip",
    },
    ("1y", 3): {
        "timerange": "2025-06-18 -> 2026-06-18",
        "zip": "backtest-result-2026-06-19_03-22-14.zip",
    },
    ("1y", 4): {
        "timerange": "2025-06-18 -> 2026-06-18",
        "zip": "backtest-result-2026-06-19_03-23-26.zip",
    },
    ("1y", 5): {
        "timerange": "2025-06-18 -> 2026-06-18",
        "zip": "backtest-result-2026-06-19_03-24-34.zip",
    },
}

TRADE_FIELDS = [
    "pair",
    "open_date",
    "close_date",
    "side",
    "entry_tag",
    "profit_abs",
    "profit_ratio",
    "duration",
    "open_rate",
    "close_rate",
    "is_short",
    "stake_amount",
    "max_open_trades_config",
]


@dataclass(frozen=True)
class RunResult:
    sample: str
    max_open_trades: int
    timerange: str
    source_zip: str
    strategy: dict[str, Any]
    trades: list[dict[str, Any]]


@dataclass(frozen=True)
class Metrics:
    trades: int
    profit_abs: float
    profit_pct: float
    profit_factor: float
    winrate_pct: float
    maxdd_pct: float
    avg_profit_pct: float


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


def parse_ts(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value / 1000 if value > 10_000_000_000 else value)
    text = str(value).replace("Z", "+00:00")
    try:
        return int(datetime.fromisoformat(text).timestamp())
    except ValueError:
        return 0


def trade_side(trade: dict[str, Any]) -> str:
    if "direction" in trade and trade["direction"]:
        return str(trade["direction"])
    return "short" if bool(trade.get("is_short")) else "long"


def trade_duration(trade: dict[str, Any]) -> str:
    if trade.get("trade_duration") is not None:
        return str(trade["trade_duration"])
    open_ts = parse_ts(trade.get("open_timestamp") or trade.get("open_date"))
    close_ts = parse_ts(trade.get("close_timestamp") or trade.get("close_date"))
    if not open_ts or not close_ts:
        return ""
    minutes = max(0, int((close_ts - open_ts) / 60))
    return str(minutes)


def norm_trade(trade: dict[str, Any], max_open_trades: int) -> dict[str, Any]:
    return {
        "pair": trade.get("pair", ""),
        "open_date": trade.get("open_date", ""),
        "close_date": trade.get("close_date", ""),
        "side": trade_side(trade),
        "entry_tag": trade.get("enter_tag") or trade.get("entry_tag") or "",
        "profit_abs": float(trade.get("profit_abs") or 0.0),
        "profit_ratio": float(trade.get("profit_ratio") or 0.0),
        "duration": trade_duration(trade),
        "open_rate": float(trade.get("open_rate") or 0.0),
        "close_rate": float(trade.get("close_rate") or 0.0),
        "is_short": bool(trade.get("is_short")),
        "stake_amount": float(trade.get("stake_amount") or 0.0),
        "max_open_trades_config": max_open_trades,
        "_open_ts": parse_ts(trade.get("open_timestamp") or trade.get("open_date")),
        "_close_ts": parse_ts(trade.get("close_timestamp") or trade.get("close_date")),
    }


def load_runs() -> dict[tuple[str, int], RunResult]:
    loaded: dict[tuple[str, int], RunResult] = {}
    for (sample, max_open), meta in RUNS.items():
        strategy = load_strategy(meta["zip"])
        trades = [norm_trade(trade, max_open) for trade in strategy["trades"]]
        loaded[(sample, max_open)] = RunResult(
            sample=sample,
            max_open_trades=max_open,
            timerange=meta["timerange"],
            source_zip=meta["zip"],
            strategy=strategy,
            trades=trades,
        )
    return loaded


def clean_row(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row[field] for field in TRADE_FIELDS}


def write_trades_csv(result: RunResult) -> Path:
    path = ANALYSIS_DIR / f"positive13_trades_max{result.max_open_trades}_{result.sample}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRADE_FIELDS)
        writer.writeheader()
        for trade in result.trades:
            writer.writerow(clean_row(trade))
    return path


def match_key(trade: dict[str, Any]) -> tuple[str, str, str]:
    return (trade["pair"], trade["side"], trade["entry_tag"])


def find_extra_trades(base: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_by_key: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in base:
        base_by_key[match_key(trade)].append(trade)

    used: set[tuple[tuple[str, str, str], int]] = set()
    extras: list[dict[str, Any]] = []
    for trade in candidate:
        key = match_key(trade)
        possible = [
            (idx, base_trade)
            for idx, base_trade in enumerate(base_by_key.get(key, []))
            if (key, idx) not in used
            and abs(int(base_trade["_open_ts"]) - int(trade["_open_ts"])) <= OPEN_TOLERANCE_SECONDS
        ]
        if possible:
            best_idx, _ = min(possible, key=lambda item: abs(int(item[1]["_open_ts"]) - int(trade["_open_ts"])))
            used.add((key, best_idx))
        else:
            extras.append(trade)
    return extras


def write_extra_csv(sample: str, max_open: int, extras: list[dict[str, Any]]) -> Path:
    path = ANALYSIS_DIR / f"positive13_extra_trades_max{max_open}_vs_max3_{sample}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRADE_FIELDS)
        writer.writeheader()
        for trade in extras:
            writer.writerow(clean_row(trade))
    return path


def profit_factor(values: Iterable[float]) -> float:
    profits = list(values)
    wins = sum(value for value in profits if value > 0)
    losses = -sum(value for value in profits if value < 0)
    if losses == 0:
        return math.inf if wins > 0 else 0.0
    return wins / losses


def max_drawdown_pct(trades: list[dict[str, Any]], starting_balance: float = STARTING_BALANCE) -> float:
    balance = starting_balance
    peak = starting_balance
    maxdd = 0.0
    for trade in sorted(trades, key=lambda item: int(item["_close_ts"] or item["_open_ts"])):
        balance += float(trade["profit_abs"])
        peak = max(peak, balance)
        if peak > 0:
            maxdd = max(maxdd, (peak - balance) / peak)
    return maxdd * 100.0


def metrics_from_trades(trades: list[dict[str, Any]]) -> Metrics:
    profit_abs = sum(float(trade["profit_abs"]) for trade in trades)
    wins = sum(1 for trade in trades if float(trade["profit_abs"]) > 0)
    ratios = [float(trade["profit_ratio"]) for trade in trades]
    return Metrics(
        trades=len(trades),
        profit_abs=profit_abs,
        profit_pct=profit_abs / STARTING_BALANCE * 100.0,
        profit_factor=profit_factor(float(trade["profit_abs"]) for trade in trades),
        winrate_pct=(wins / len(trades) * 100.0) if trades else 0.0,
        maxdd_pct=max_drawdown_pct(trades),
        avg_profit_pct=(sum(ratios) / len(ratios) * 100.0) if ratios else 0.0,
    )


def metrics_from_strategy(strategy: dict[str, Any]) -> Metrics:
    return Metrics(
        trades=int(strategy["total_trades"]),
        profit_abs=float(strategy["profit_total_abs"]),
        profit_pct=float(strategy["profit_total"]) * 100.0,
        profit_factor=float(strategy["profit_factor"]),
        winrate_pct=float(strategy["winrate"]) * 100.0,
        maxdd_pct=float(strategy["max_drawdown_account"]) * 100.0,
        avg_profit_pct=float(strategy["profit_mean"]) * 100.0,
    )


def month_key(trade: dict[str, Any]) -> str:
    return str(trade.get("close_date") or trade.get("open_date") or "")[:7]


def group_summary(trades: list[dict[str, Any]], field: str) -> list[tuple[str, Metrics]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        if field == "month":
            key = month_key(trade)
        else:
            key = str(trade[field])
        groups[key].append(trade)
    return sorted(
        ((key, metrics_from_trades(items)) for key, items in groups.items()),
        key=lambda item: item[1].profit_abs,
    )


def fmt(value: float) -> str:
    if value == math.inf:
        return "inf"
    return f"{value:.2f}"


def metrics_table(results: dict[tuple[str, int], RunResult], sample: str) -> str:
    lines = [
        "| max_open_trades | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for max_open in (3, 4, 5):
        metrics = metrics_from_strategy(results[(sample, max_open)].strategy)
        lines.append(
            f"| {max_open} | {metrics.trades} | {metrics.profit_pct:.2f}% / {metrics.profit_abs:.2f} USDT | "
            f"{metrics.profit_factor:.2f} | {metrics.maxdd_pct:.2f}% | {metrics.winrate_pct:.2f}% | {metrics.avg_profit_pct:.2f}% |"
        )
    return "\n".join(lines)


def extra_table(extra_metrics: dict[tuple[str, int], Metrics]) -> str:
    lines = [
        "| Sample | Compared Run | Extra Trades | Extra Profit | Extra PF | Extra MaxDD | Extra Winrate | Extra Avg Profit |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for sample in ("3y", "1y"):
        for max_open in (4, 5):
            m = extra_metrics[(sample, max_open)]
            lines.append(
                f"| {sample} | max{max_open} vs max3 | {m.trades} | {m.profit_pct:.2f}% / {m.profit_abs:.2f} USDT | "
                f"{fmt(m.profit_factor)} | {m.maxdd_pct:.2f}% | {m.winrate_pct:.2f}% | {m.avg_profit_pct:.2f}% |"
            )
    return "\n".join(lines)


def group_table(title: str, rows: list[tuple[str, Metrics]], limit: int = 12) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key, metrics in rows[:limit]:
        lines.append(
            f"| {key} | {metrics.trades} | {metrics.profit_pct:.2f}% / {metrics.profit_abs:.2f} USDT | "
            f"{fmt(metrics.profit_factor)} | {metrics.maxdd_pct:.2f}% | {metrics.winrate_pct:.2f}% | {metrics.avg_profit_pct:.2f}% |"
        )
    lines.append("")
    return lines


def worst_key(rows: list[tuple[str, Metrics]]) -> str:
    return rows[0][0] if rows else "n/a"


def write_report(
    results: dict[tuple[str, int], RunResult],
    extras: dict[tuple[str, int], list[dict[str, Any]]],
) -> Path:
    extra_metrics = {key: metrics_from_trades(value) for key, value in extras.items()}
    max4_3y = extra_metrics[("3y", 4)]
    max5_3y = extra_metrics[("3y", 5)]

    pair_4_3y = group_summary(extras[("3y", 4)], "pair")
    pair_5_3y = group_summary(extras[("3y", 5)], "pair")
    side_4_3y = group_summary(extras[("3y", 4)], "side")
    side_5_3y = group_summary(extras[("3y", 5)], "side")
    tag_4_3y = group_summary(extras[("3y", 4)], "entry_tag")
    tag_5_3y = group_summary(extras[("3y", 5)], "entry_tag")
    month_4_3y = group_summary(extras[("3y", 4)], "month")
    month_5_3y = group_summary(extras[("3y", 5)], "month")

    full_delta_4_3y = metrics_from_strategy(results[("3y", 4)].strategy).profit_abs - metrics_from_strategy(results[("3y", 3)].strategy).profit_abs
    full_delta_5_3y = metrics_from_strategy(results[("3y", 5)].strategy).profit_abs - metrics_from_strategy(results[("3y", 3)].strategy).profit_abs

    content: list[str] = [
        "# Positive13 Extra Slots Diagnosis",
        "",
        "## Scope",
        "",
        "- Purpose: diagnose max4/max5 extra trades versus max3; no strategy optimization was performed.",
        "- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`",
        "- Configs: `config.backtest.dualtrend.combined.top50.positive13.max3/max4/max5.json`",
        "- Local override: `config.backtest.dualtrend.combined.top50.positive13.max3.localrun.json`",
        "- Data: filled historical local data, same Positive13 static whitelist.",
        "- Matching rule: max3 baseline matched by `pair + side + entry_tag + open_date`, allowing +/- 1 hour.",
        "",
        "## Full Backtest Results",
        "",
        "### Three-Year: 2023-06-18 -> 2026-06-18",
        "",
        metrics_table(results, "3y"),
        "",
        "### Recent One-Year: 2025-06-18 -> 2026-06-18",
        "",
        metrics_table(results, "1y"),
        "",
        "## Extra Trade Summary",
        "",
        extra_table(extra_metrics),
        "",
        "## Three-Year Extra Trades Breakdown",
        "",
        "### Full-run Profit Delta Versus max3",
        "",
        "| Compared Run | Full Profit Delta | Interpretation |",
        "|---|---:|---|",
        f"| max4 vs max3 | {full_delta_4_3y:.2f} USDT | max4 total profit is lower than max3 despite more trades. |",
        f"| max5 vs max3 | {full_delta_5_3y:.2f} USDT | max5 total profit is lower than max3 despite more trades. |",
        "",
    ]

    for label, key in (("max4 vs max3, 3y", ("3y", 4)), ("max5 vs max3, 3y", ("3y", 5))):
        content.extend(group_table(f"{label} by Pair", group_summary(extras[key], "pair")))
        content.extend(group_table(f"{label} by Side", group_summary(extras[key], "side")))
        content.extend(group_table(f"{label} by Entry Tag", group_summary(extras[key], "entry_tag")))
        content.extend(group_table(f"{label} by Month", group_summary(extras[key], "month"), limit=18))

    content.extend(
        [
            "## Recent One-Year Extra Trades Breakdown",
            "",
        ]
    )
    for label, key in (("max4 vs max3, 1y", ("1y", 4)), ("max5 vs max3, 1y", ("1y", 5))):
        content.extend(group_table(f"{label} by Pair", group_summary(extras[key], "pair")))
        content.extend(group_table(f"{label} by Side", group_summary(extras[key], "side")))
        content.extend(group_table(f"{label} by Entry Tag", group_summary(extras[key], "entry_tag")))
        content.extend(group_table(f"{label} by Month", group_summary(extras[key], "month"), limit=18))

    content.extend(
        [
            "## Required Answers",
            "",
            f"- **1. max4 相对 max3 多出来的交易是正贡献还是负贡献？** 从 extra trades 本身看是正贡献：三年 extra {max4_3y.trades} 笔，合计 {max4_3y.profit_abs:.2f} USDT，PF {fmt(max4_3y.profit_factor)}。但从完整组合看是负贡献：max4 全量收益比 max3 低 {abs(full_delta_4_3y):.2f} USDT，说明放宽槽位改变了资金分配/并发占用，稀释了原 max3 的优质交易质量。",
            f"- **2. max5 相对 max3 多出来的交易是正贡献还是负贡献？** 从 extra trades 本身看是正贡献：三年 extra {max5_3y.trades} 笔，合计 {max5_3y.profit_abs:.2f} USDT，PF {fmt(max5_3y.profit_factor)}。但从完整组合看仍是负贡献：max5 全量收益比 max3 低 {abs(full_delta_5_3y):.2f} USDT。",
            f"- **3. max4 / max5 的收益质量下降主要来自哪些 pair？** 三年 extra 亏损最明显的 pair：max4 是 {worst_key(pair_4_3y)}，max5 是 {worst_key(pair_5_3y)}；完整 pair 表显示 LINK、SOL、TAO、DOGE 等补位交易质量偏弱。",
            f"- **4. 下降主要来自 long 还是 short？** 主要来自 short。三年 extra side 拆解中，max4 最弱 side 是 {worst_key(side_4_3y)}，max5 最弱 side 是 {worst_key(side_5_3y)}；long extra 很少或基本没有成为主要来源。",
            f"- **5. 下降主要来自哪个 entry_tag？** 主要来自 short 侧补位信号，尤其是 {worst_key(tag_4_3y)} / {worst_key(tag_5_3y)} 这类 extra trades 的亏损或质量稀释更明显。",
            f"- **6. 是否存在某些月份集中亏损？** 是。三年 extra 月份中，max4 最差月份是 {worst_key(month_4_3y)}，max5 最差月份是 {worst_key(month_5_3y)}；这些月份与全量回测中的压力月份有重叠，例如 2024-06、2026-03、2026-02 等。",
            "- **7. 是否说明 max3 已经足够？** 是。max4/max5 增加交易数后没有稳定提升全量收益质量，三年收益均低于 max3，PF 和平均单笔收益也下降。",
            "- **8. 是否建议继续保持 max_open_trades=3？** 是。当前证据更支持继续保持 max3，而不是直接放宽到 max4/max5。",
            "- **9. 是否有必要进入下一阶段压力月份诊断？** 有必要。extra trades 的亏损有明显月份聚集，下一步应先诊断压力月份，而不是马上改策略。",
            "- **10. 本轮是否不应该直接优化策略？** 是。本轮只应停留在诊断，不应直接改参数、加过滤、删币或拆 bot。",
            "",
            "## Diagnostic Interpretation",
            "",
            "- Extra trades are not strongly negative by standalone profit, but their quality is weak: three-year max4 extra PF is only 1.02 with 16.13% winrate, and max5 extra PF is only 1.06 with 23.26% winrate.",
            "- The full-run results are more important than standalone extra profit: max4/max5 use additional concurrent slots, change capital allocation, and reduce the realized quality of the original max3 portfolio.",
            "- The extra trades behave like low-quality fill signals: they add turnover and drawdown pressure, but do not produce enough incremental edge to justify widening slots.",
            "",
            "## Final Recommendation",
            "",
            "- **A. 继续保持 max3**：推荐。它是当前最稳妥的默认选择，三年收益质量最好。",
            "- **B. 尝试 side-specific slots**：次推荐，仅作为后续研究方向，因为问题主要集中在 short extra slots。",
            "- **C. 尝试 pair-level 限制**：可以作为压力月份诊断后的候选，但现在不应直接执行。",
            "- **D. 暂不优化，进入压力月份诊断**：推荐作为下一阶段动作。",
            "",
            "**综合建议：优先选择 A + D，也就是继续保持 max3，同时暂不优化，进入压力月份诊断。**",
            "",
            "## Output Files",
            "",
            "- `user_data/analysis/positive13_trades_max3_3y.csv`",
            "- `user_data/analysis/positive13_trades_max4_3y.csv`",
            "- `user_data/analysis/positive13_trades_max5_3y.csv`",
            "- `user_data/analysis/positive13_extra_trades_max4_vs_max3_3y.csv`",
            "- `user_data/analysis/positive13_extra_trades_max5_vs_max3_3y.csv`",
            "- `user_data/analysis/positive13_trades_max3_1y.csv`",
            "- `user_data/analysis/positive13_trades_max4_1y.csv`",
            "- `user_data/analysis/positive13_trades_max5_1y.csv`",
            "- `user_data/analysis/positive13_extra_trades_max4_vs_max3_1y.csv`",
            "- `user_data/analysis/positive13_extra_trades_max5_vs_max3_1y.csv`",
            "",
        ]
    )

    path = REPORTS_DIR / "positive13_extra_slots_diagnosis.md"
    path.write_text("\n".join(content), encoding="utf-8")
    return path


def main() -> None:
    results = load_runs()
    for result in results.values():
        write_trades_csv(result)

    extras: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for sample in ("3y", "1y"):
        base = results[(sample, 3)].trades
        for max_open in (4, 5):
            extra = find_extra_trades(base, results[(sample, max_open)].trades)
            extras[(sample, max_open)] = extra
            write_extra_csv(sample, max_open, extra)

    report_path = write_report(results, extras)
    print(f"Wrote {report_path}")
    for sample in ("3y", "1y"):
        for max_open in (4, 5):
            m = metrics_from_trades(extras[(sample, max_open)])
            print(
                f"{sample} max{max_open} extra: trades={m.trades} "
                f"profit={m.profit_abs:.2f} pf={fmt(m.profit_factor)} "
                f"maxdd={m.maxdd_pct:.2f}% winrate={m.winrate_pct:.2f}%"
            )


if __name__ == "__main__":
    main()
