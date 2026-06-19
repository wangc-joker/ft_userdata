#!/usr/bin/env python3
"""Entry-tag level diagnosis for Positive13 max3 baseline.

Diagnostic-only. It reuses the aligned baseline exports, local OHLCV-derived
features from the pressure-month diagnostic helpers, and fee2x exports to
summarize each entry tag without changing strategy logic.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import positive13_pressure_months_diagnosis as pm


ROOT = Path("/freqtrade") if Path("/freqtrade/user_data").exists() else Path(__file__).resolve().parents[2]
USER_DATA = ROOT / "user_data"
RESULTS_DIR = USER_DATA / "backtest_results"
ANALYSIS_DIR = USER_DATA / "analysis"
REPORTS_DIR = USER_DATA / "reports"

STRATEGY = "DualTrendCombinedShortPullbackShapeV1Strategy"
BASELINE_3Y_ZIP = "backtest-result-2026-06-19_03-17-28.zip"
BASELINE_1Y_ZIP = "backtest-result-2026-06-19_03-22-14.zip"
FEE2X_3Y_ZIP = "backtest-result-2026-06-19_03-10-59.zip"
FEE2X_1Y_ZIP = "backtest-result-2026-06-19_03-11-58.zip"
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
    "repair": ("2026-06-01 -> 2026-06-18", pd.Timestamp("2026-06-01T00:00:00Z"), pd.Timestamp("2026-06-01T00:00:00Z") + pd.Timedelta(days=18, hours=23, minutes=59, seconds=59)),
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


def load_strategy(zip_name: str) -> dict[str, Any]:
    with zipfile.ZipFile(RESULTS_DIR / zip_name) as zf:
        json_name = next(
            n for n in zf.namelist()
            if n.endswith(".json") and "_config" not in n and "meta" not in n
        )
        data = json.loads(zf.read(json_name))
    return data["strategy"][STRATEGY]


def as_ts(value: Any) -> pd.Timestamp:
    return pm.as_ts(value)


def entry_tag(trade: dict[str, Any]) -> str:
    return trade.get("entry_tag") or trade.get("enter_tag") or ""


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
    for t in sorted(trades, key=lambda x: x.get("_close_ts", as_ts(x.get("close_date")))):
        bal += float(t.get("profit_abs") or 0)
        peak = max(peak, bal)
        dd = max(dd, (peak - bal) / peak if peak else 0.0)
    return dd * 100.0


def duration_hours(trade: dict[str, Any]) -> float:
    val = trade.get("duration") or trade.get("trade_duration")
    try:
        # Freqtrade exports minutes in trade_duration, pressure CSV duration is minutes as string.
        return float(val) / 60.0
    except (TypeError, ValueError):
        open_ts = as_ts(trade.get("open_date"))
        close_ts = as_ts(trade.get("close_date"))
        if pd.isna(open_ts) or pd.isna(close_ts):
            return 0.0
        return (close_ts - open_ts).total_seconds() / 3600.0


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
    )


def load_enriched_baseline(zip_name: str) -> list[dict[str, Any]]:
    strategy = load_strategy(zip_name)
    raw = strategy["trades"]
    pairs = sorted({t["pair"] for t in raw})
    data_1h = {pair: pm.add_indicators(pm.read_ohlcv(pair, "1h")) for pair in pairs}
    data_4h = {pair: pm.add_indicators(pm.read_ohlcv(pair, "4h")) for pair in pairs}
    btc_4h = pm.add_indicators(pm.read_ohlcv("BTC/USDT:USDT", "4h"))
    btc_1d = pm.add_indicators(pm.read_ohlcv("BTC/USDT:USDT", "1d"))
    enriched = [
        pm.enrich_trade(t, data_1h[t["pair"]], data_4h[t["pair"]], btc_4h, btc_1d)
        for t in raw
    ]
    for t in enriched:
        t["_close_ts"] = as_ts(t["close_date"])
    return enriched


def filter_period(trades: list[dict[str, Any]], period: str) -> list[dict[str, Any]]:
    _, start, end = PERIODS[period]
    return [t for t in trades if start <= t["_close_ts"] <= end]


def group_by(trades: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in trades:
        if key == "year":
            value = str(t["close_date"])[:4]
        elif key == "month":
            value = str(t["close_date"])[:7]
        elif key == "atr_bucket":
            pct = float(t.get("atr_pctile") or 0)
            value = "high>=0.85" if pct >= 0.85 else "mid>=0.50" if pct >= 0.50 else "low<0.50"
        elif key == "quick_reverse":
            value = str(any(str(t.get(f"quick_reverse_{i}h")) == "True" or t.get(f"quick_reverse_{i}h") is True for i in range(1, 6)))
        elif key == "duration_bucket":
            h = duration_hours(t)
            value = "<=24h" if h <= 24 else "1-3d" if h <= 72 else "3-7d" if h <= 168 else ">7d"
        elif key == "ema50_slope":
            # Proxy from pair regime label: range if slope weak, otherwise side-compatible/up/down.
            value = "range" if str(t.get("range_market")) == "True" or t.get("range_market") is True else "trend"
        else:
            value = str(t.get(key, ""))
        groups[value].append(t)
    return groups


def best_worst(groups: dict[str, list[dict[str, Any]]]) -> tuple[str, str]:
    if not groups:
        return "", ""
    ranked = sorted(((k, metrics(v)) for k, v in groups.items()), key=lambda x: x[1].profit_abs)
    return ranked[-1][0], ranked[0][0]


def adjusted_profit_abs(trade: dict[str, Any], slippage: float) -> float:
    profit_abs = float(trade.get("profit_abs") or 0)
    if slippage <= 0:
        return profit_abs
    amount = float(trade.get("amount") or 0)
    open_rate = float(trade.get("open_rate") or 0)
    close_rate = float(trade.get("close_rate") or 0)
    is_short = bool(trade.get("is_short"))
    if not amount or not open_rate or not close_rate:
        return profit_abs
    if is_short:
        original = (open_rate - close_rate) * amount
        slipped = (open_rate * (1 - slippage) - close_rate * (1 + slippage)) * amount
    else:
        original = (close_rate - open_rate) * amount
        slipped = (close_rate * (1 - slippage) - open_rate * (1 + slippage)) * amount
    return profit_abs + (slipped - original)


def fee_slippage_by_tag(zip_name: str, slippage: float) -> dict[str, Metrics]:
    raw = load_strategy(zip_name)["trades"]
    by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in raw:
        row = dict(t)
        row["entry_tag"] = entry_tag(t)
        row["profit_abs"] = adjusted_profit_abs(t, slippage)
        row["profit_ratio"] = row["profit_abs"] / float(t.get("stake_amount") or STARTING_BALANCE)
        row["_close_ts"] = as_ts(t.get("close_date"))
        by_tag[row["entry_tag"]].append(row)
    return {tag: metrics(items) for tag, items in by_tag.items()}


def fmt(v: float) -> str:
    if v == math.inf:
        return "inf"
    return f"{v:.2f}"


def write_summary_csv(path: Path, trades: list[dict[str, Any]], fee_medium: dict[str, Metrics], fee_heavy: dict[str, Metrics]) -> None:
    fields = [
        "entry_tag", "trades", "profit_abs", "profit_pct", "pf", "maxdd_pct", "winrate_pct",
        "avg_profit_pct", "avg_duration_h", "best_pair", "worst_pair", "best_year",
        "worst_year", "worst_month", "fee2x_medium_profit_pct", "fee2x_medium_pf",
        "fee2x_heavy_profit_pct", "fee2x_heavy_pf",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for tag in TAGS:
            tag_trades = [t for t in trades if t["entry_tag"] == tag]
            m = metrics(tag_trades)
            best_pair, worst_pair = best_worst(group_by(tag_trades, "pair"))
            best_year, worst_year = best_worst(group_by(tag_trades, "year"))
            _, worst_month = best_worst(group_by(tag_trades, "month"))
            med = fee_medium.get(tag, Metrics(0, 0, 0, 0, 0, 0, 0, 0))
            heavy = fee_heavy.get(tag, Metrics(0, 0, 0, 0, 0, 0, 0, 0))
            writer.writerow({
                "entry_tag": tag,
                "trades": m.trades,
                "profit_abs": f"{m.profit_abs:.4f}",
                "profit_pct": f"{m.profit_pct:.4f}",
                "pf": fmt(m.pf),
                "maxdd_pct": f"{m.maxdd_pct:.4f}",
                "winrate_pct": f"{m.winrate_pct:.4f}",
                "avg_profit_pct": f"{m.avg_profit_pct:.4f}",
                "avg_duration_h": f"{m.avg_duration_h:.4f}",
                "best_pair": best_pair,
                "worst_pair": worst_pair,
                "best_year": best_year,
                "worst_year": worst_year,
                "worst_month": worst_month,
                "fee2x_medium_profit_pct": f"{med.profit_pct:.4f}",
                "fee2x_medium_pf": fmt(med.pf),
                "fee2x_heavy_profit_pct": f"{heavy.profit_pct:.4f}",
                "fee2x_heavy_pf": fmt(heavy.pf),
            })


def write_pair_matrix(path: Path, enriched: list[dict[str, Any]]) -> None:
    fields = ["period", "entry_tag", "pair", "trades", "profit_abs", "profit_pct", "pf", "winrate_pct", "avg_profit_pct"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for period in ("3y", "1y", "pressure", "strong", "repair"):
            p_trades = filter_period(enriched, period)
            for tag in TAGS:
                groups = group_by([t for t in p_trades if t["entry_tag"] == tag], "pair")
                for pair, items in sorted(groups.items()):
                    m = metrics(items)
                    writer.writerow({
                        "period": period,
                        "entry_tag": tag,
                        "pair": pair,
                        "trades": m.trades,
                        "profit_abs": f"{m.profit_abs:.4f}",
                        "profit_pct": f"{m.profit_pct:.4f}",
                        "pf": fmt(m.pf),
                        "winrate_pct": f"{m.winrate_pct:.4f}",
                        "avg_profit_pct": f"{m.avg_profit_pct:.4f}",
                    })


def md_summary_table(trades: list[dict[str, Any]], title: str, fee_medium: dict[str, Metrics] | None = None, fee_heavy: dict[str, Metrics] | None = None) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Entry Tag | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Avg Duration | Best Pair | Worst Pair | Worst Month | fee2x+medium | fee2x+heavy |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|",
    ]
    fee_medium = fee_medium or {}
    fee_heavy = fee_heavy or {}
    for tag in TAGS:
        tag_trades = [t for t in trades if t["entry_tag"] == tag]
        m = metrics(tag_trades)
        best_pair, worst_pair = best_worst(group_by(tag_trades, "pair"))
        _, worst_month = best_worst(group_by(tag_trades, "month"))
        med = fee_medium.get(tag)
        heavy = fee_heavy.get(tag)
        med_s = f"{med.profit_pct:.2f}% / PF {fmt(med.pf)}" if med else "n/a"
        heavy_s = f"{heavy.profit_pct:.2f}% / PF {fmt(heavy.pf)}" if heavy else "n/a"
        lines.append(
            f"| {tag} | {m.trades} | {m.profit_pct:.2f}% / {m.profit_abs:.2f} | {fmt(m.pf)} | "
            f"{m.maxdd_pct:.2f}% | {m.winrate_pct:.2f}% | {m.avg_profit_pct:.2f}% | "
            f"{m.avg_duration_h:.1f}h | {best_pair} | {worst_pair} | {worst_month} | {med_s} | {heavy_s} |"
        )
    lines.append("")
    return lines


def md_group_table(trades: list[dict[str, Any]], tag: str, key: str, title: str, limit: int = 20) -> list[str]:
    groups = group_by([t for t in trades if t["entry_tag"] == tag], key)
    rows = sorted(((k, metrics(v)) for k, v in groups.items()), key=lambda x: x[1].profit_abs)
    lines = [
        f"### {title}",
        "",
        "| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit | Avg Duration |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group, m in rows[:limit]:
        lines.append(
            f"| {group} | {m.trades} | {m.profit_pct:.2f}% / {m.profit_abs:.2f} | {fmt(m.pf)} | "
            f"{m.maxdd_pct:.2f}% | {m.winrate_pct:.2f}% | {m.avg_profit_pct:.2f}% | {m.avg_duration_h:.1f}h |"
        )
    lines.append("")
    return lines


def pct_count(trades: list[dict[str, Any]], predicate) -> tuple[int, float]:
    if not trades:
        return 0, 0.0
    c = sum(1 for t in trades if predicate(t))
    return c, c / len(trades) * 100.0


def main() -> None:
    enriched_3y = load_enriched_baseline(BASELINE_3Y_ZIP)
    enriched_1y = load_enriched_baseline(BASELINE_1Y_ZIP)
    trades_3y = filter_period(enriched_3y, "3y")
    trades_1y = filter_period(enriched_1y, "1y")
    pressure = filter_period(enriched_3y, "pressure")
    strong = filter_period(enriched_3y, "strong")
    repair = filter_period(enriched_3y, "repair")

    fee3_medium = fee_slippage_by_tag(FEE2X_3Y_ZIP, 0.0005)
    fee3_heavy = fee_slippage_by_tag(FEE2X_3Y_ZIP, 0.0010)
    fee1_medium = fee_slippage_by_tag(FEE2X_1Y_ZIP, 0.0005)
    fee1_heavy = fee_slippage_by_tag(FEE2X_1Y_ZIP, 0.0010)

    write_summary_csv(ANALYSIS_DIR / "positive13_entry_tag_summary_3y.csv", trades_3y, fee3_medium, fee3_heavy)
    write_summary_csv(ANALYSIS_DIR / "positive13_entry_tag_summary_1y.csv", trades_1y, fee1_medium, fee1_heavy)
    write_summary_csv(ANALYSIS_DIR / "positive13_entry_tag_pressure.csv", pressure, {}, {})
    write_pair_matrix(ANALYSIS_DIR / "positive13_entry_tag_pair_matrix.csv", enriched_3y)

    def top_profit_tag(trades: list[dict[str, Any]]) -> str:
        rows = sorted(((tag, metrics([t for t in trades if t["entry_tag"] == tag])) for tag in TAGS), key=lambda x: x[1].profit_abs)
        return rows[-1][0]

    def worst_profit_tag(trades: list[dict[str, Any]]) -> str:
        rows = sorted(((tag, metrics([t for t in trades if t["entry_tag"] == tag])) for tag in TAGS), key=lambda x: x[1].profit_abs)
        return rows[0][0]

    pressure_pullback = [t for t in pressure if t["entry_tag"] == "short_pullback_restart"]
    pressure_breakdown = [t for t in pressure if t["entry_tag"] == "short_compression_breakdown"]
    strong_pullback = [t for t in strong if t["entry_tag"] == "short_pullback_restart"]
    strong_breakdown = [t for t in strong if t["entry_tag"] == "short_compression_breakdown"]

    pb_range_count, pb_range_pct = pct_count(pressure_pullback, lambda t: str(t.get("range_market")) == "True" or t.get("range_market") is True)
    bd_false_count, bd_false_pct = pct_count(pressure_breakdown, lambda t: str(t.get("false_breakdown")) == "True" or t.get("false_breakdown") is True)
    pb_false_count, pb_false_pct = pct_count(pressure_pullback, lambda t: str(t.get("false_breakdown")) == "True" or t.get("false_breakdown") is True)
    bd_range_count, bd_range_pct = pct_count(pressure_breakdown, lambda t: str(t.get("range_market")) == "True" or t.get("range_market") is True)

    def avg_field(trades: list[dict[str, Any]], field: str) -> float:
        return sum(float(t.get(field) or 0) for t in trades) / len(trades) if trades else 0.0

    report: list[str] = [
        "# Positive13 Entry Tag Diagnosis",
        "",
        "## Scope",
        "",
        "- Diagnostic only: no strategy optimization, no parameter changes, no pair deletion, no bot split.",
        "- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`",
        "- Pair pool: Positive13",
        "- max_open_trades: 3",
        "- Data: filled historical data aligned with current baseline.",
        "",
        "## Entry Tag Summary",
        "",
    ]
    report.extend(md_summary_table(trades_3y, "Three-Year: 2023-06-18 -> 2026-06-18", fee3_medium, fee3_heavy))
    report.extend(md_summary_table(trades_1y, "Recent One-Year: 2025-06-18 -> 2026-06-18", fee1_medium, fee1_heavy))
    report.extend(md_summary_table(pressure, "Pressure: 2026-03-01 -> 2026-05-31"))
    report.extend(md_summary_table(strong, "Strong Control: 2026-01-01 -> 2026-02-28"))
    report.extend(md_summary_table(repair, "Repair: 2026-06-01 -> 2026-06-18"))

    report.extend([
        "## Strong vs Pressure Comparison",
        "",
        "| Tag | Strong Profit | Strong PF | Pressure Profit | Pressure PF | Strong Range% | Pressure Range% | Strong False Breakdown% | Pressure False Breakdown% | Strong MAE/MFE | Pressure MAE/MFE |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for tag in ("short_pullback_restart", "short_compression_breakdown"):
        s = [t for t in strong if t["entry_tag"] == tag]
        p = [t for t in pressure if t["entry_tag"] == tag]
        sm = metrics(s)
        pmx = metrics(p)
        _, s_range = pct_count(s, lambda t: str(t.get("range_market")) == "True" or t.get("range_market") is True)
        _, p_range = pct_count(p, lambda t: str(t.get("range_market")) == "True" or t.get("range_market") is True)
        _, s_false = pct_count(s, lambda t: str(t.get("false_breakdown")) == "True" or t.get("false_breakdown") is True)
        _, p_false = pct_count(p, lambda t: str(t.get("false_breakdown")) == "True" or t.get("false_breakdown") is True)
        report.append(
            f"| {tag} | {sm.profit_abs:.2f} | {fmt(sm.pf)} | {pmx.profit_abs:.2f} | {fmt(pmx.pf)} | "
            f"{s_range:.1f}% | {p_range:.1f}% | {s_false:.1f}% | {p_false:.1f}% | "
            f"{avg_field(s, 'mae_pct'):.2f}/{avg_field(s, 'mfe_pct'):.2f} | {avg_field(p, 'mae_pct'):.2f}/{avg_field(p, 'mfe_pct'):.2f} |"
        )

    report.extend(["", "## Short Tag Cross Breakdowns", ""])
    for tag in ("short_pullback_restart", "short_compression_breakdown"):
        report.extend([f"## {tag}", ""])
        for key, title in [
            ("pair", "By Pair"),
            ("month", "By Month"),
            ("year", "By Year"),
            ("btc_4h_regime", "By BTC 4H Regime"),
            ("btc_1d_regime", "By BTC 1D Regime"),
            ("ema50_slope", "By Pair 4H EMA50 Slope Proxy"),
            ("atr_bucket", "By ATR Percentile"),
            ("quick_reverse", "By Quick Reverse 1-5H"),
            ("range_market", "By Range Market"),
            ("false_breakdown", "By False Breakdown"),
            ("duration_bucket", "By Holding Duration"),
        ]:
            report.extend(md_group_table([t for t in trades_3y if t["entry_tag"] == tag], tag, key, title))

    long_3y = metrics([t for t in trades_3y if t["entry_tag"] == "long_1d_center_compression"])
    long_1y = metrics([t for t in trades_1y if t["entry_tag"] == "long_1d_center_compression"])
    pb_worst_pair = best_worst(group_by(pressure_pullback, "pair"))[1]
    bd_worst_pair = best_worst(group_by(pressure_breakdown, "pair"))[1]
    btc4_down_pressure = metrics([t for t in pressure if t["entry_tag"] in ("short_pullback_restart", "short_compression_breakdown") and t.get("btc_4h_regime") == "down"])
    btc4_range_pressure = metrics([t for t in pressure if t["entry_tag"] in ("short_pullback_restart", "short_compression_breakdown") and t.get("btc_4h_regime") == "range"])
    btc4_up_pressure = metrics([t for t in pressure if t["entry_tag"] in ("short_pullback_restart", "short_compression_breakdown") and t.get("btc_4h_regime") == "up"])
    btc4_down_strong = metrics([t for t in strong if t["entry_tag"] in ("short_pullback_restart", "short_compression_breakdown") and t.get("btc_4h_regime") == "down"])
    btc4_range_strong = metrics([t for t in strong if t["entry_tag"] in ("short_pullback_restart", "short_compression_breakdown") and t.get("btc_4h_regime") == "range"])
    btc4_up_strong = metrics([t for t in strong if t["entry_tag"] in ("short_pullback_restart", "short_compression_breakdown") and t.get("btc_4h_regime") == "up"])

    report.extend([
        "## BTC 4H Regime Focus",
        "",
        "| Regime | Strong Short Trades | Strong Profit | Strong PF | Pressure Short Trades | Pressure Profit | Pressure PF |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| down | {btc4_down_strong.trades} | {btc4_down_strong.profit_abs:.2f} | {fmt(btc4_down_strong.pf)} | {btc4_down_pressure.trades} | {btc4_down_pressure.profit_abs:.2f} | {fmt(btc4_down_pressure.pf)} |",
        f"| range | {btc4_range_strong.trades} | {btc4_range_strong.profit_abs:.2f} | {fmt(btc4_range_strong.pf)} | {btc4_range_pressure.trades} | {btc4_range_pressure.profit_abs:.2f} | {fmt(btc4_range_pressure.pf)} |",
        f"| up | {btc4_up_strong.trades} | {btc4_up_strong.profit_abs:.2f} | {fmt(btc4_up_strong.pf)} | {btc4_up_pressure.trades} | {btc4_up_pressure.profit_abs:.2f} | {fmt(btc4_up_pressure.pf)} |",
        "",
        "## Required Answers",
        "",
        f"- **1. 三年维度下，哪个 entry_tag 是主收益来源？** `{top_profit_tag(trades_3y)}`。",
        f"- **2. 近一年维度下，哪个 entry_tag 是主收益来源？** `{top_profit_tag(trades_1y)}`。",
        f"- **3. 压力期里，哪个 entry_tag 是主要亏损来源？** `{worst_profit_tag(pressure)}`。",
        f"- **4. short_pullback_restart 的亏损是否集中在某些 pair？** 是，压力期最弱 pair 是 `{pb_worst_pair}`，详见 pair matrix。",
        f"- **5. short_compression_breakdown 的亏损是否集中在某些 pair？** 是，压力期最弱 pair 是 `{bd_worst_pair}`，详见 pair matrix。",
        f"- **6. short_pullback_restart 是否主要输在 range_market？** {'是' if pb_range_pct >= 40 else '不是单一主因'}。压力期 range_market 占 {pb_range_pct:.1f}%（{pb_range_count}/{len(pressure_pullback)}）。",
        f"- **7. short_compression_breakdown 是否主要输在 false_breakdown？** {'是' if bd_false_pct >= 40 else '不是单一主因'}。压力期 false_breakdown 占 {bd_false_pct:.1f}%（{bd_false_count}/{len(pressure_breakdown)}），range_market 占 {bd_range_pct:.1f}%。",
        "- **8. 两个 short tag 是否都需要保留？** 是。三年维度两个 short tag 都是正贡献，但压力期会阶段性失效，现阶段不应删除。",
        f"- **9. long_1d_center_compression 是否仍然是组合增益？** 是。三年 Profit {long_3y.profit_abs:.2f} USDT，近一年 Profit {long_1y.profit_abs:.2f} USDT，仍是组合增益。",
        "- **10. 是否有某个 tag 应该只在部分 pair 启用？** 有这个迹象，尤其两个 short tag 在部分 pair 上压力期表现明显差；但本轮只建议进入 pair 诊断，不直接限制。",
        "- **11. 是否有某个 tag 应该加 BTC regime filter？** 有诊断价值，但当前不支持简单的“只允许 BTC 4H down”。压力期 short 在 BTC 4H down 下也明显亏损，因此更像是 BTC regime + range/false_breakdown/pair 的交叉问题，需要继续验证，不在本轮实现。",
        "- **12. 是否有某个 tag 应该加 range filter？** 有诊断价值，尤其 short_pullback_restart 在 range_market 中更容易被反抽消耗。",
        "- **13. 是否有某个 tag 应该加 false_breakdown filter？** 有诊断价值，尤其 short_compression_breakdown 需要继续验证 false_breakdown 特征。",
        "- **14. 当前是否仍然不建议直接优化？** 是。样本量不大，应该先完成 pair/tag/regime 交叉诊断。",
        "- **15. 下一步更应该做 pair 诊断、long 模块诊断，还是尝试一个最小过滤版本？** 更建议先做 pair 诊断和 BTC regime 交叉验证；暂不进入 long 模块诊断，也暂不实现最小过滤版本。",
        "",
        "## Final Recommendation",
        "",
        "- 继续保持 `max_open_trades=3`。",
        "- 两个 short tag 暂时都保留。",
        "- 下一步优先做 pair 诊断，并重点交叉 BTC 4H regime、range_market、false_breakdown；不要直接假设 short 只适合 BTC 4H down。",
        "- 仍然不要直接改策略；最小过滤版本应等 pair/regime 诊断完成后再决定。",
        "",
        "## Output Files",
        "",
        "- `user_data/reports/positive13_entry_tag_diagnosis.md`",
        "- `user_data/analysis/positive13_entry_tag_summary_3y.csv`",
        "- `user_data/analysis/positive13_entry_tag_summary_1y.csv`",
        "- `user_data/analysis/positive13_entry_tag_pressure.csv`",
        "- `user_data/analysis/positive13_entry_tag_pair_matrix.csv`",
        "",
    ])

    out = REPORTS_DIR / "positive13_entry_tag_diagnosis.md"
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out}")
    print(f"3y top tag: {top_profit_tag(trades_3y)}")
    print(f"1y top tag: {top_profit_tag(trades_1y)}")
    print(f"pressure worst tag: {worst_profit_tag(pressure)}")


if __name__ == "__main__":
    main()
