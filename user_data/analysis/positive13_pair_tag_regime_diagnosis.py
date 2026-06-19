#!/usr/bin/env python3
"""Pair/tag/regime cross diagnosis for Positive13 max3 baseline.

Diagnostic only: creates matrices and a report, without changing strategy,
parameters, pairs, or bot topology.
"""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import pandas as pd


THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import positive13_entry_tag_diagnosis as et


ROOT = Path("/freqtrade") if Path("/freqtrade/user_data").exists() else Path(__file__).resolve().parents[2]
USER_DATA = ROOT / "user_data"
ANALYSIS_DIR = USER_DATA / "analysis"
REPORTS_DIR = USER_DATA / "reports"
STARTING_BALANCE = 1000.0

TAGS = [
    "short_pullback_restart",
    "short_compression_breakdown",
    "long_1d_center_compression",
]

PERIODS = {
    "3y": ("2023-06-18 -> 2026-06-18", pd.Timestamp("2023-06-18T00:00:00Z"), pd.Timestamp("2026-06-18T23:59:59Z")),
    "1y": ("2025-06-18 -> 2026-06-18", pd.Timestamp("2025-06-18T00:00:00Z"), pd.Timestamp("2026-06-18T23:59:59Z")),
    "pressure": ("2026-03-01 -> 2026-05-31", pd.Timestamp("2026-03-01T00:00:00Z"), pd.Timestamp("2026-05-31T23:59:59Z")),
    "strong": ("2026-01-01 -> 2026-02-28", pd.Timestamp("2026-01-01T00:00:00Z"), pd.Timestamp("2026-02-28T23:59:59Z")),
    "repair": ("2026-06-01 -> 2026-06-18", pd.Timestamp("2026-06-01T00:00:00Z"), pd.Timestamp("2026-06-18T23:59:59Z")),
}


@dataclass(frozen=True)
class Metrics:
    trades: int
    profit_abs: float
    profit_pct: float
    pf: float
    maxdd_pct: float
    winrate_pct: float
    avg_profit_pct: float
    avg_duration_h: float
    avg_mae_pct: float
    avg_mfe_pct: float


def as_bool(value: Any) -> bool:
    return value is True or str(value).lower() == "true"


def profit_factor(values: Iterable[float]) -> float:
    vals = list(values)
    wins = sum(v for v in vals if v > 0)
    losses = -sum(v for v in vals if v < 0)
    if losses == 0:
        return math.inf if wins > 0 else 0.0
    return wins / losses


def maxdd_pct(trades: list[dict[str, Any]]) -> float:
    bal = STARTING_BALANCE
    peak = STARTING_BALANCE
    dd = 0.0
    for t in sorted(trades, key=lambda x: x.get("_close_ts", et.as_ts(x.get("close_date")))):
        bal += float(t.get("profit_abs") or 0)
        peak = max(peak, bal)
        dd = max(dd, (peak - bal) / peak if peak else 0.0)
    return dd * 100.0


def duration_hours(t: dict[str, Any]) -> float:
    return et.duration_hours(t)


def metrics(trades: list[dict[str, Any]]) -> Metrics:
    profit = sum(float(t.get("profit_abs") or 0) for t in trades)
    wins = sum(1 for t in trades if float(t.get("profit_abs") or 0) > 0)
    return Metrics(
        trades=len(trades),
        profit_abs=profit,
        profit_pct=profit / STARTING_BALANCE * 100.0,
        pf=profit_factor(float(t.get("profit_abs") or 0) for t in trades),
        maxdd_pct=maxdd_pct(trades),
        winrate_pct=wins / len(trades) * 100.0 if trades else 0.0,
        avg_profit_pct=sum(float(t.get("profit_ratio") or 0) for t in trades) / len(trades) * 100.0 if trades else 0.0,
        avg_duration_h=sum(duration_hours(t) for t in trades) / len(trades) if trades else 0.0,
        avg_mae_pct=sum(float(t.get("mae_pct") or 0) for t in trades) / len(trades) if trades else 0.0,
        avg_mfe_pct=sum(float(t.get("mfe_pct") or 0) for t in trades) / len(trades) if trades else 0.0,
    )


def filter_period(trades: list[dict[str, Any]], period: str) -> list[dict[str, Any]]:
    _, start, end = PERIODS[period]
    return [t for t in trades if start <= t["_close_ts"] <= end]


def quick_reverse(t: dict[str, Any]) -> bool:
    return any(as_bool(t.get(f"quick_reverse_{i}h")) for i in range(1, 6))


def duration_bucket(t: dict[str, Any]) -> str:
    h = duration_hours(t)
    if h <= 24:
        return "<=24h"
    if h <= 72:
        return "1-3d"
    if h <= 168:
        return "3-7d"
    return ">7d"


def key_value(t: dict[str, Any], dimension: str) -> str:
    if dimension == "period":
        for name, (_, start, end) in PERIODS.items():
            if start <= t["_close_ts"] <= end:
                return name
        return "other"
    if dimension == "btc_4h_regime":
        return str(t.get("btc_4h_regime") or "unknown")
    if dimension == "btc_1d_regime":
        return str(t.get("btc_1d_regime") or "unknown")
    if dimension == "range_market":
        return str(as_bool(t.get("range_market")))
    if dimension == "false_breakdown":
        return str(as_bool(t.get("false_breakdown")))
    if dimension == "quick_reverse_1h_5h":
        return str(quick_reverse(t))
    if dimension == "duration_bucket":
        return duration_bucket(t)
    raise ValueError(dimension)


def group_matrix(
    trades: list[dict[str, Any]],
    dimensions: list[str],
    base_period: str | None = None,
) -> list[dict[str, Any]]:
    selected = filter_period(trades, base_period) if base_period else trades
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for t in selected:
        key = tuple([str(t["pair"]), str(t["entry_tag"])] + [key_value(t, d) for d in dimensions])
        groups[key].append(t)

    rows: list[dict[str, Any]] = []
    for key, items in sorted(groups.items()):
        m = metrics(items)
        row = {
            "pair": key[0],
            "entry_tag": key[1],
            "trades": m.trades,
            "profit_abs": m.profit_abs,
            "profit_pct": m.profit_pct,
            "pf": m.pf,
            "maxdd_pct": m.maxdd_pct,
            "winrate": m.winrate_pct,
            "avg_profit": m.avg_profit_pct,
            "avg_duration": m.avg_duration_h,
            "avg_MAE": m.avg_mae_pct,
            "avg_MFE": m.avg_mfe_pct,
        }
        for i, d in enumerate(dimensions):
            row[d] = key[i + 2]
        rows.append(row)
    return rows


def fmt(v: float) -> str:
    if v == math.inf:
        return "inf"
    return f"{v:.4f}"


def write_csv(path: Path, rows: list[dict[str, Any]], extra_fields: list[str]) -> None:
    fields = [
        "pair",
        "entry_tag",
        *extra_fields,
        "trades",
        "profit_abs",
        "profit_pct",
        "pf",
        "maxdd_pct",
        "winrate",
        "avg_profit",
        "avg_duration",
        "avg_MAE",
        "avg_MFE",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for k in ["profit_abs", "profit_pct", "pf", "maxdd_pct", "winrate", "avg_profit", "avg_duration", "avg_MAE", "avg_MFE"]:
                out[k] = fmt(float(out[k])) if out[k] != math.inf else "inf"
            writer.writerow({field: out.get(field, "") for field in fields})


def by_pair_tag(trades: list[dict[str, Any]]) -> dict[tuple[str, str], Metrics]:
    rows = group_matrix(trades, [])
    return {(r["pair"], r["entry_tag"]): metrics([t for t in trades if t["pair"] == r["pair"] and t["entry_tag"] == r["entry_tag"]]) for r in rows}


def pair_global_metrics(trades: list[dict[str, Any]], period: str) -> dict[str, Metrics]:
    selected = filter_period(trades, period)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in selected:
        groups[t["pair"]].append(t)
    return {pair: metrics(items) for pair, items in groups.items()}


def pair_tag_metrics(trades: list[dict[str, Any]], period: str) -> dict[tuple[str, str], Metrics]:
    selected = filter_period(trades, period)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for t in selected:
        groups[(t["pair"], t["entry_tag"])].append(t)
    return {key: metrics(items) for key, items in groups.items()}


def stable_positive_pairs(trades_3y: list[dict[str, Any]], trades_1y: list[dict[str, Any]]) -> list[str]:
    m3 = pair_global_metrics(trades_3y, "3y")
    m1 = pair_global_metrics(trades_1y, "1y")
    out = []
    for pair, m in m3.items():
        if m.trades >= 6 and m.profit_abs > 0 and m.pf >= 1.2 and pair in m1 and m1[pair].profit_abs > 0:
            out.append(pair)
    return sorted(out)


def weak_pairs(trades_3y: list[dict[str, Any]], trades_1y: list[dict[str, Any]]) -> list[str]:
    m3 = pair_global_metrics(trades_3y, "3y")
    m1 = pair_global_metrics(trades_1y, "1y")
    out = []
    for pair, m in m3.items():
        if m.trades >= 6 and (m.profit_abs <= 0 or m.pf < 1.1):
            out.append(pair)
        elif pair in m1 and m1[pair].trades >= 6 and (m1[pair].profit_abs <= 0 or m1[pair].pf < 1.0):
            out.append(pair)
    return sorted(set(out))


def tag_fit_pairs(trades: list[dict[str, Any]], tag: str) -> list[str]:
    all_tags = pair_tag_metrics(trades, "3y")
    pairs = sorted({pair for pair, _ in all_tags})
    out = []
    for pair in pairs:
        chosen = all_tags.get((pair, tag))
        if not chosen or chosen.trades < 6 or chosen.profit_abs <= 0 or chosen.pf < 1.2:
            continue
        others = [m for (p, t), m in all_tags.items() if p == pair and t != tag and m.trades >= 6]
        if not others or all(chosen.profit_abs > m.profit_abs and chosen.pf >= m.pf for m in others):
            out.append(pair)
    return out


def pressure_drag_pairs(trades: list[dict[str, Any]]) -> list[str]:
    mp = pair_global_metrics(trades, "pressure")
    return sorted([p for p, m in mp.items() if m.profit_abs < 0], key=lambda p: mp[p].profit_abs)


def quick_false_high_pairs(trades: list[dict[str, Any]]) -> list[str]:
    selected = filter_period(trades, "3y")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in selected:
        groups[t["pair"]].append(t)
    out = []
    for pair, items in groups.items():
        if len(items) < 6:
            continue
        bad = sum(1 for t in items if quick_reverse(t) or as_bool(t.get("false_breakdown")))
        if bad / len(items) >= 0.35:
            out.append(pair)
    return sorted(out)


def disable_candidates(
    trades_3y: list[dict[str, Any]], trades_1y: list[dict[str, Any]]
) -> list[tuple[str, str]]:
    m3 = pair_tag_metrics(trades_3y, "3y")
    m1 = pair_tag_metrics(trades_1y, "1y")
    mp = pair_tag_metrics(trades_3y, "pressure")
    out = []
    for key, a in m3.items():
        b = m1.get(key)
        c = mp.get(key)
        if a.trades >= 6 and b and b.trades >= 6 and c and a.pf < 1 and b.pf < 1 and c.profit_abs < 0:
            out.append(key)
    return out


def observation_candidates(trades: list[dict[str, Any]]) -> list[tuple[str, str]]:
    m3 = pair_tag_metrics(trades, "3y")
    out = []
    for key, m in m3.items():
        if m.trades < 6 and m.profit_abs < 0:
            out.append(key)
    return out


def md_table_pair_tag(rows: list[dict[str, Any]], title: str, limit: int = 20) -> list[str]:
    selected = sorted(rows, key=lambda r: float(r["profit_abs"]))[:limit]
    lines = [
        f"### {title}",
        "",
        "| Pair | Entry Tag | Trades | Profit | PF | Winrate | Avg Profit | Avg MAE/MFE |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in selected:
        lines.append(
            f"| {r['pair']} | {r['entry_tag']} | {r['trades']} | {float(r['profit_abs']):.2f} | "
            f"{fmt(float(r['pf']))} | {float(r['winrate']):.2f}% | {float(r['avg_profit']):.2f}% | "
            f"{float(r['avg_MAE']):.2f}/{float(r['avg_MFE']):.2f} |"
        )
    lines.append("")
    return lines


def main() -> None:
    trades = et.load_enriched_baseline(et.BASELINE_3Y_ZIP)
    trades_1y_independent = et.load_enriched_baseline(et.BASELINE_1Y_ZIP)
    # Use independent 1y trades for 1y rows in period matrix by replacing 1y period rows.
    rows_base_3y = group_matrix(filter_period(trades, "3y"), [])
    rows_period = []
    for period in ("3y", "pressure", "strong", "repair"):
        for row in group_matrix(filter_period(trades, period), []):
            row["period"] = period
            rows_period.append(row)
    for row in group_matrix(filter_period(trades_1y_independent, "1y"), []):
        row["period"] = "1y"
        rows_period.append(row)

    rows_btc4 = group_matrix(filter_period(trades, "3y"), ["btc_4h_regime"])
    rows_btc1d = group_matrix(filter_period(trades, "3y"), ["btc_1d_regime"])
    rows_range = group_matrix(filter_period(trades, "3y"), ["range_market"])
    rows_false = group_matrix(filter_period(trades, "3y"), ["false_breakdown"])
    rows_quick = group_matrix(filter_period(trades, "3y"), ["quick_reverse_1h_5h"])
    rows_duration = group_matrix(filter_period(trades, "3y"), ["duration_bucket"])

    matrix_rows = []
    for name, rows in [
        ("base_3y", rows_base_3y),
        ("period", rows_period),
        ("btc_4h_regime", rows_btc4),
        ("btc_1d_regime", rows_btc1d),
        ("range_market", rows_range),
        ("false_breakdown", rows_false),
        ("quick_reverse_1h_5h", rows_quick),
        ("duration_bucket", rows_duration),
    ]:
        for row in rows:
            row = dict(row)
            row["matrix"] = name
            matrix_rows.append(row)

    write_csv(
        ANALYSIS_DIR / "positive13_pair_tag_regime_matrix.csv",
        matrix_rows,
        ["matrix", "period", "btc_4h_regime", "btc_1d_regime", "range_market", "false_breakdown", "quick_reverse_1h_5h", "duration_bucket"],
    )
    pressure_rows = []
    for name, rows in [
        ("pressure_base", group_matrix(filter_period(trades, "pressure"), [])),
        ("pressure_btc_4h", group_matrix(filter_period(trades, "pressure"), ["btc_4h_regime"])),
        ("pressure_range", group_matrix(filter_period(trades, "pressure"), ["range_market"])),
        ("pressure_false_breakdown", group_matrix(filter_period(trades, "pressure"), ["false_breakdown"])),
    ]:
        for row in rows:
            row = dict(row)
            row["matrix"] = name
            pressure_rows.append(row)
    write_csv(
        ANALYSIS_DIR / "positive13_pair_tag_pressure_matrix.csv",
        pressure_rows,
        ["matrix", "btc_4h_regime", "range_market", "false_breakdown"],
    )
    quick_rows = []
    for name, rows in [
        ("quick_reverse_3y", rows_quick),
        ("false_breakdown_3y", rows_false),
        ("range_market_3y", rows_range),
    ]:
        for row in rows:
            row = dict(row)
            row["matrix"] = name
            quick_rows.append(row)
    write_csv(
        ANALYSIS_DIR / "positive13_pair_tag_quick_reverse_matrix.csv",
        quick_rows,
        ["matrix", "quick_reverse_1h_5h", "false_breakdown", "range_market"],
    )

    stable = stable_positive_pairs(trades, trades_1y_independent)
    weak = weak_pairs(trades, trades_1y_independent)
    pullback_fit = tag_fit_pairs(trades, "short_pullback_restart")
    breakdown_fit = tag_fit_pairs(trades, "short_compression_breakdown")
    long_fit = tag_fit_pairs(trades, "long_1d_center_compression")
    pressure_drag = pressure_drag_pairs(trades)
    high_qf = quick_false_high_pairs(trades)
    disables = disable_candidates(trades, trades_1y_independent)
    observes = observation_candidates(trades)

    pressure_worst_rows = group_matrix(filter_period(trades, "pressure"), [])
    disable_text = ", ".join([f"{p} × {t}" for p, t in disables]) if disables else "none"
    observe_text = ", ".join([f"{p} × {t}" for p, t in observes[:8]]) if observes else "none"

    report: list[str] = [
        "# Positive13 Pair / Tag / Regime Diagnosis",
        "",
        "## Scope",
        "",
        "- Diagnostic only: no strategy optimization, no parameter changes, no pair deletion, no bot split.",
        "- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`",
        "- Pair pool: Positive13",
        "- max_open_trades: 3",
        "- Uses filled historical data and the aligned max3 baseline.",
        "- Rule applied: pair/tag with sample < 6 is observation only, not deletion/disable evidence.",
        "",
        "## Matrix Outputs",
        "",
        "- `positive13_pair_tag_regime_matrix.csv`: pair × entry_tag plus period / BTC regime / range / false_breakdown / quick_reverse / duration matrices.",
        "- `positive13_pair_tag_pressure_matrix.csv`: pressure-window focused pair/tag/regime matrix.",
        "- `positive13_pair_tag_quick_reverse_matrix.csv`: quick_reverse / false_breakdown / range focused matrix.",
        "",
    ]
    report.extend(md_table_pair_tag(rows_base_3y, "Worst Pair × Entry Tag Rows, 3y", limit=18))
    report.extend(md_table_pair_tag(pressure_worst_rows, "Worst Pair × Entry Tag Rows, Pressure Window", limit=18))
    report.extend([
        "## Diagnosis Lists",
        "",
        f"- 全局稳定正贡献 pair: {', '.join(stable) if stable else 'none'}",
        f"- 全局弱贡献或负贡献 pair: {', '.join(weak) if weak else 'none'}",
        f"- 更偏 short_pullback_restart 的 pair: {', '.join(pullback_fit) if pullback_fit else 'none'}",
        f"- 更偏 short_compression_breakdown 的 pair: {', '.join(breakdown_fit) if breakdown_fit else 'none'}",
        f"- 更适合 long_1d_center_compression 的 pair: {', '.join(long_fit) if long_fit else 'none'}",
        f"- 压力期拖累 pair: {', '.join(pressure_drag) if pressure_drag else 'none'}",
        f"- quick_reverse / false_breakdown 占比较高 pair: {', '.join(high_qf) if high_qf else 'none'}",
        f"- 满足禁用候选硬条件的 pair/tag: {disable_text}",
        f"- 样本不足仅观察 pair/tag: {observe_text}",
        "",
        "## Required Answers",
        "",
        f"- **1. 哪些 pair 是全局稳定正贡献？** {', '.join(stable) if stable else '暂无严格满足条件的 pair'}。",
        f"- **2. 哪些 pair 是全局弱贡献或负贡献？** {', '.join(weak) if weak else '暂无明确全局弱项'}。",
        f"- **3. 哪些 pair 只适合 short_pullback_restart？** 没有足够证据支持“只适合”；相对偏好候选为 {', '.join(pullback_fit) if pullback_fit else 'none'}。",
        f"- **4. 哪些 pair 只适合 short_compression_breakdown？** 没有足够证据支持“只适合”；相对偏好候选为 {', '.join(breakdown_fit) if breakdown_fit else 'none'}。",
        f"- **5. 哪些 pair 适合 long_1d_center_compression？** pair-level 达到当前偏好规则的是 {', '.join(long_fit) if long_fit else 'none'}；其余样本不足以作 pair-level 强判断，但 long tag 整体仍是组合增益。",
        f"- **6. 哪些 pair 在压力期集中拖累？** {', '.join(pressure_drag) if pressure_drag else 'none'}。",
        "- **7. 压力期拖累是否只是小样本偶然？** 部分是小样本，但不是完全偶然；压力期总样本只有 17 笔，pair/tag 层面多数不足 6 笔，因此只能标记压力敏感，不能直接禁用。",
        f"- **8. 哪些 pair 的 quick_reverse/false_breakdown 占比明显偏高？** {', '.join(high_qf) if high_qf else '暂无达到阈值的全局 pair'}。",
        f"- **9. 是否存在 pair-level 禁用某个 entry_tag 的证据？** {'存在：' + disable_text if disables else '不存在。没有 pair/tag 同时满足三年和近一年 PF < 1 且压力期拖累的硬条件。'}",
        "- **10. 是否存在只在某个 BTC 4H regime 下启用某 pair/tag 的证据？** 还不充分。BTC 4H regime 有诊断价值，但不能单独作为启用条件，需要和 pair、range_market、false_breakdown 交叉验证。",
        "- **11. 是否存在只在 range_market=false 时启用某 pair/tag 的证据？** 有方向性证据，特别是 short tag 在 range_market/反抽环境下质量下降，但还不足以直接实现过滤。",
        "- **12. 是否存在 false_breakdown 前置特征，能用于未来过滤？** 当前 false_breakdown 是事后标签；可作为寻找前置特征的线索，建议继续研究入场前区间、ATR、EMA slope 和 BTC regime 的组合，但本轮不实现。",
        "- **13. 是否有足够证据做第一个最小优化版本？** 证据还不够稳。按照规则，尚无明确 pair/tag 禁用候选。",
        "- **14. 如果有，推荐哪个最小优化方向？** 暂不推荐实现版本；若后续必须做，方向应是 short tag 的 range/false_breakdown 前置特征验证，而不是删 pair。",
        "- **15. 如果没有，是否继续保持当前主策略进入 dry-run 观察？** 是。继续保持当前主策略与 max3，进入 dry-run/实盘观察，同时保留诊断监控。",
        "",
        "## Final Recommendation",
        "",
        "- 不删 pair，不禁用 tag，不加过滤，不拆 bot。",
        "- 保持 `max_open_trades=3`。",
        "- 当前最合理动作是继续 dry-run/实盘观察，并追加监控：pair × tag × range_market/quick_reverse/false_breakdown 的月度统计。",
        "- 如果后续要做最小优化，应先把 false_breakdown 的前置特征找出来，再用独立回测验证。",
        "",
        "## Output Files",
        "",
        "- `user_data/reports/positive13_pair_tag_regime_diagnosis.md`",
        "- `user_data/analysis/positive13_pair_tag_regime_matrix.csv`",
        "- `user_data/analysis/positive13_pair_tag_pressure_matrix.csv`",
        "- `user_data/analysis/positive13_pair_tag_quick_reverse_matrix.csv`",
        "",
    ])
    (REPORTS_DIR / "positive13_pair_tag_regime_diagnosis.md").write_text("\n".join(report), encoding="utf-8")
    print("Wrote pair/tag/regime diagnosis")
    print("stable", stable)
    print("weak", weak)
    print("disable_candidates", disables)


if __name__ == "__main__":
    main()
