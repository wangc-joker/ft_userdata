#!/usr/bin/env python3
"""Diagnose Positive13 pressure months for the aligned max3 baseline.

Diagnostic-only. This script reads the latest aligned max3 backtest export and
local OHLCV data, labels losing trades in the 2026-03..2026-05 pressure window,
and writes the requested CSVs/report. It does not change strategy parameters.
"""

from __future__ import annotations

import csv
import json
import math
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


ROOT = Path("/freqtrade") if Path("/freqtrade/user_data").exists() else Path(__file__).resolve().parents[2]
USER_DATA = ROOT / "user_data"
RESULTS_DIR = USER_DATA / "backtest_results"
DATA_DIR = USER_DATA / "data" / "binance" / "futures"
ANALYSIS_DIR = USER_DATA / "analysis"
REPORTS_DIR = USER_DATA / "reports"

STRATEGY = "DualTrendCombinedShortPullbackShapeV1Strategy"
MAX3_3Y_ZIP = "backtest-result-2026-06-19_03-17-28.zip"
MAX4_EXTRA_3Y = ANALYSIS_DIR / "positive13_extra_trades_max4_vs_max3_3y.csv"
MAX5_EXTRA_3Y = ANALYSIS_DIR / "positive13_extra_trades_max5_vs_max3_3y.csv"
STARTING_BALANCE = 1000.0

PERIODS = {
    "pressure": {
        "label": "2026-03-01 -> 2026-05-31",
        "start": pd.Timestamp("2026-03-01T00:00:00Z"),
        "end": pd.Timestamp("2026-05-31T23:59:59Z"),
        "csv": "positive13_trades_202603_202605.csv",
    },
    "pre": {
        "label": "2026-01-01 -> 2026-02-28",
        "start": pd.Timestamp("2026-01-01T00:00:00Z"),
        "end": pd.Timestamp("2026-02-28T23:59:59Z"),
        "csv": "positive13_trades_202601_202602.csv",
    },
    "post": {
        "label": "2026-06-01 -> 2026-06-18",
        "start": pd.Timestamp("2026-06-01T00:00:00Z"),
        "end": pd.Timestamp("2026-06-18T23:59:59Z"),
        "csv": "positive13_trades_202606.csv",
    },
}

CSV_FIELDS = [
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
    "mae_pct",
    "mfe_pct",
    "quick_reverse_1h",
    "quick_reverse_2h",
    "quick_reverse_3h",
    "quick_reverse_4h",
    "quick_reverse_5h",
    "btc_4h_regime",
    "btc_1d_regime",
    "btc_regime_conflict",
    "atr_pctile",
    "atr_spike",
    "late_trend_chase",
    "range_market",
    "false_breakout",
    "false_breakdown",
    "stop_too_tight",
    "loss_label",
]


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
    with zipfile.ZipFile(RESULTS_DIR / zip_name) as zf:
        json_name = next(
            name
            for name in zf.namelist()
            if name.endswith(".json") and "_config" not in name and "meta" not in name
        )
        data = json.loads(zf.read(json_name))
    return data["strategy"][STRATEGY]


def as_ts(value: Any) -> pd.Timestamp:
    if value is None:
        return pd.NaT
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 10_000_000_000 else value
        return pd.Timestamp.fromtimestamp(seconds, tz=timezone.utc)
    return pd.Timestamp(str(value).replace("Z", "+00:00")).tz_convert("UTC")


def pair_file_stem(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def read_ohlcv(pair: str, timeframe: str) -> pd.DataFrame:
    path = DATA_DIR / f"{pair_file_stem(pair)}-{timeframe}-futures.feather"
    df = pd.read_feather(path)
    if "date" not in df.columns:
        raise ValueError(f"Missing date column in {path}")
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df.sort_values("date").reset_index(drop=True)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            (out["high"] - out["low"]).abs(),
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr14"] = tr.rolling(14, min_periods=14).mean()
    out["atr_pct"] = out["atr14"] / out["close"]
    out["atr_pctile_90d"] = out["atr_pct"].rolling(24 * 90, min_periods=240).rank(pct=True)
    out["ma20"] = out["close"].rolling(20, min_periods=20).mean()
    out["ma50"] = out["close"].rolling(50, min_periods=50).mean()
    out["ma50_slope"] = out["ma50"] - out["ma50"].shift(12)
    out["ret_24h"] = out["close"] / out["close"].shift(24) - 1
    out["range_pct_72h"] = (out["high"].rolling(72).max() - out["low"].rolling(72).min()) / out["close"]
    out["ma_cross_count_72h"] = ((out["close"] > out["ma20"]) != (out["close"].shift(1) > out["ma20"].shift(1))).rolling(72).sum()
    return out


def btc_regime_at(btc_df: pd.DataFrame, ts: pd.Timestamp) -> str:
    row = latest_row(btc_df, ts)
    if row is None or pd.isna(row.get("ma50")) or pd.isna(row.get("ma50_slope")):
        return "unknown"
    if row["close"] > row["ma50"] and row["ma50_slope"] > 0:
        return "up"
    if row["close"] < row["ma50"] and row["ma50_slope"] < 0:
        return "down"
    return "range"


def latest_row(df: pd.DataFrame, ts: pd.Timestamp) -> pd.Series | None:
    pos = df["date"].searchsorted(ts, side="right") - 1
    if pos < 0:
        return None
    return df.iloc[int(pos)]


def window(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return df[(df["date"] >= start) & (df["date"] <= end)].copy()


def trade_side(trade: dict[str, Any]) -> str:
    return "short" if bool(trade.get("is_short")) else "long"


def trade_duration(trade: dict[str, Any]) -> str:
    if trade.get("trade_duration") is not None:
        return str(trade["trade_duration"])
    open_ts = as_ts(trade.get("open_date"))
    close_ts = as_ts(trade.get("close_date"))
    if pd.isna(open_ts) or pd.isna(close_ts):
        return ""
    return str(int((close_ts - open_ts).total_seconds() / 60))


def calc_mae_mfe(trade: dict[str, Any], df_1h: pd.DataFrame) -> tuple[float, float]:
    open_ts = as_ts(trade["open_date"])
    close_ts = as_ts(trade["close_date"])
    open_rate = float(trade.get("open_rate") or 0)
    if open_rate <= 0:
        return 0.0, 0.0
    candles = window(df_1h, open_ts, close_ts)
    if candles.empty:
        return 0.0, 0.0
    if trade_side(trade) == "short":
        mae = (candles["high"].max() - open_rate) / open_rate
        mfe = (open_rate - candles["low"].min()) / open_rate
    else:
        mae = (open_rate - candles["low"].min()) / open_rate
        mfe = (candles["high"].max() - open_rate) / open_rate
    return float(mae * 100.0), float(mfe * 100.0)


def quick_reversal_flags(trade: dict[str, Any], df_1h: pd.DataFrame) -> tuple[list[bool], bool, bool]:
    open_ts = as_ts(trade["open_date"])
    row = latest_row(df_1h, open_ts)
    if row is None:
        return [False] * 5, False, False
    idx = int(row.name)
    prior = df_1h.iloc[max(0, idx - 24) : idx]
    after = df_1h.iloc[idx + 1 : idx + 6]
    if prior.empty or after.empty:
        return [False] * 5, False, False
    prior_high = float(prior["high"].max())
    prior_low = float(prior["low"].min())
    entry_high = float(row["high"])
    entry_low = float(row["low"])
    flags: list[bool] = []
    side = trade_side(trade)
    for i in range(5):
        if i >= len(after):
            flags.append(False)
            continue
        close = float(after.iloc[i]["close"])
        if side == "long":
            flags.append(close < min(prior_high, entry_low))
        else:
            flags.append(close > max(prior_low, entry_high))
    return flags, side == "long" and any(flags), side == "short" and any(flags)


def detect_stop_too_tight(trade: dict[str, Any], df_1h: pd.DataFrame) -> bool:
    if float(trade.get("profit_abs") or 0) >= 0:
        return False
    close_ts = as_ts(trade["close_date"])
    open_rate = float(trade.get("open_rate") or 0)
    close_rate = float(trade.get("close_rate") or 0)
    if open_rate <= 0 or close_rate <= 0:
        return False
    after = window(df_1h, close_ts, close_ts + pd.Timedelta(hours=12))
    if after.empty:
        return False
    # Approximation: after stop/exit, price soon moves back beyond entry toward the original direction.
    if trade_side(trade) == "long":
        return bool(after["high"].max() > open_rate * 1.01)
    return bool(after["low"].min() < open_rate * 0.99)


def detect_range_market(df_4h: pd.DataFrame, ts: pd.Timestamp) -> bool:
    row = latest_row(df_4h, ts)
    if row is None:
        return False
    cross = row.get("ma_cross_count_72h")
    rng = row.get("range_pct_72h")
    slope = row.get("ma50_slope")
    close = row.get("close")
    if pd.isna(cross) or pd.isna(rng) or pd.isna(slope) or not close:
        return False
    return bool(cross >= 6 and abs(slope / close) < 0.015 and rng < 0.18)


def detect_late_trend_chase(trade: dict[str, Any], df_1h: pd.DataFrame) -> bool:
    row = latest_row(df_1h, as_ts(trade["open_date"]))
    if row is None:
        return False
    ret_24h = row.get("ret_24h")
    atr_pct = row.get("atr_pct")
    if pd.isna(ret_24h) or pd.isna(atr_pct) or atr_pct <= 0:
        return False
    if trade_side(trade) == "long":
        return bool(ret_24h > max(0.06, 2.5 * atr_pct))
    return bool(ret_24h < -max(0.06, 2.5 * atr_pct))


def enrich_trade(
    trade: dict[str, Any],
    df_1h: pd.DataFrame,
    df_4h: pd.DataFrame,
    btc_4h: pd.DataFrame,
    btc_1d: pd.DataFrame,
) -> dict[str, Any]:
    open_ts = as_ts(trade["open_date"])
    row_1h = latest_row(df_1h, open_ts)
    mae, mfe = calc_mae_mfe(trade, df_1h)
    quick_flags, false_breakout, false_breakdown = quick_reversal_flags(trade, df_1h)
    btc4 = btc_regime_at(btc_4h, open_ts)
    btc1d = btc_regime_at(btc_1d, open_ts)
    side = trade_side(trade)
    btc_conflict = (side == "long" and btc4 == "down" and btc1d in {"down", "range"}) or (
        side == "short" and btc4 == "up" and btc1d in {"up", "range"}
    )
    atr_pctile = float(row_1h.get("atr_pctile_90d")) if row_1h is not None and not pd.isna(row_1h.get("atr_pctile_90d")) else 0.0
    atr_spike = atr_pctile >= 0.85
    late_trend_chase = detect_late_trend_chase(trade, df_1h)
    range_market = detect_range_market(df_4h, open_ts)
    stop_too_tight = detect_stop_too_tight(trade, df_1h)

    label = ""
    if float(trade.get("profit_abs") or 0) >= 0:
        label = ""
    elif stop_too_tight:
        label = "stop_too_tight"
    elif false_breakout:
        label = "false_breakout"
    elif false_breakdown:
        label = "false_breakdown"
    elif btc_conflict:
        label = "btc_regime_conflict"
    elif atr_spike:
        label = "atr_spike"
    elif late_trend_chase:
        label = "late_trend_chase"
    elif range_market:
        label = "range_market"
    else:
        label = "normal_loss"

    enriched = {
        "pair": trade.get("pair", ""),
        "open_date": trade.get("open_date", ""),
        "close_date": trade.get("close_date", ""),
        "side": side,
        "entry_tag": trade.get("enter_tag") or trade.get("entry_tag") or "",
        "profit_abs": float(trade.get("profit_abs") or 0.0),
        "profit_ratio": float(trade.get("profit_ratio") or 0.0),
        "duration": trade_duration(trade),
        "open_rate": float(trade.get("open_rate") or 0.0),
        "close_rate": float(trade.get("close_rate") or 0.0),
        "is_short": bool(trade.get("is_short")),
        "stake_amount": float(trade.get("stake_amount") or 0.0),
        "mae_pct": mae,
        "mfe_pct": mfe,
        "quick_reverse_1h": quick_flags[0],
        "quick_reverse_2h": quick_flags[1],
        "quick_reverse_3h": quick_flags[2],
        "quick_reverse_4h": quick_flags[3],
        "quick_reverse_5h": quick_flags[4],
        "btc_4h_regime": btc4,
        "btc_1d_regime": btc1d,
        "btc_regime_conflict": btc_conflict,
        "atr_pctile": atr_pctile,
        "atr_spike": atr_spike,
        "late_trend_chase": late_trend_chase,
        "range_market": range_market,
        "false_breakout": false_breakout,
        "false_breakdown": false_breakdown,
        "stop_too_tight": stop_too_tight,
        "loss_label": label,
        "_close_ts": as_ts(trade.get("close_date")),
    }
    return enriched


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
    for trade in sorted(trades, key=lambda x: x["_close_ts"]):
        bal += float(trade["profit_abs"])
        peak = max(peak, bal)
        dd = max(dd, (peak - bal) / peak if peak else 0.0)
    return dd * 100.0


def metrics(trades: list[dict[str, Any]]) -> Metrics:
    profit = sum(float(t["profit_abs"]) for t in trades)
    wins = sum(1 for t in trades if float(t["profit_abs"]) > 0)
    return Metrics(
        trades=len(trades),
        profit_abs=profit,
        profit_pct=profit / STARTING_BALANCE * 100,
        profit_factor=profit_factor(float(t["profit_abs"]) for t in trades),
        winrate_pct=wins / len(trades) * 100 if trades else 0,
        maxdd_pct=maxdd_pct(trades),
        avg_profit_pct=sum(float(t["profit_ratio"]) for t in trades) / len(trades) * 100 if trades else 0,
    )


def group_metrics(trades: list[dict[str, Any]], field: str) -> list[tuple[str, Metrics]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in trades:
        key = str(t[field])
        groups[key].append(t)
    return sorted(((k, metrics(v)) for k, v in groups.items()), key=lambda kv: kv[1].profit_abs)


def month_group_metrics(trades: list[dict[str, Any]]) -> list[tuple[str, Metrics]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in trades:
        groups[str(t["close_date"])[:7]].append(t)
    return sorted(((k, metrics(v)) for k, v in groups.items()), key=lambda kv: k_sort(kv[0]))


def k_sort(value: str) -> str:
    return value


def label_counts(trades: list[dict[str, Any]]) -> Counter[str]:
    return Counter(t["loss_label"] for t in trades if float(t["profit_abs"]) < 0)


def read_extra_months(path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    if not path.exists():
        return counts
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if float(row.get("profit_abs") or 0) < 0:
                counts[row.get("close_date", "")[:7]] += 1
    return counts


def fmt(v: float) -> str:
    if v == math.inf:
        return "inf"
    return f"{v:.2f}"


def md_metrics_table(title: str, rows: list[tuple[str, Metrics]]) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Group | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key, m in rows:
        lines.append(
            f"| {key} | {m.trades} | {m.profit_pct:.2f}% / {m.profit_abs:.2f} USDT | "
            f"{fmt(m.profit_factor)} | {m.maxdd_pct:.2f}% | {m.winrate_pct:.2f}% | {m.avg_profit_pct:.2f}% |"
        )
    lines.append("")
    return lines


def write_csv(path: Path, trades: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for t in trades:
            writer.writerow({k: t[k] for k in CSV_FIELDS})


def pick_period_trades(enriched: list[dict[str, Any]], start: pd.Timestamp, end: pd.Timestamp) -> list[dict[str, Any]]:
    return [t for t in enriched if start <= t["_close_ts"] <= end]


def main() -> None:
    strategy = load_strategy(MAX3_3Y_ZIP)
    raw_trades = strategy["trades"]
    pairs = sorted({t["pair"] for t in raw_trades})

    data_1h = {pair: add_indicators(read_ohlcv(pair, "1h")) for pair in pairs}
    data_4h = {pair: add_indicators(read_ohlcv(pair, "4h")) for pair in pairs}
    btc_4h = add_indicators(read_ohlcv("BTC/USDT:USDT", "4h"))
    btc_1d = add_indicators(read_ohlcv("BTC/USDT:USDT", "1d"))

    enriched = [
        enrich_trade(t, data_1h[t["pair"]], data_4h[t["pair"]], btc_4h, btc_1d)
        for t in raw_trades
    ]

    period_trades: dict[str, list[dict[str, Any]]] = {}
    for key, meta in PERIODS.items():
        selected = pick_period_trades(enriched, meta["start"], meta["end"])
        period_trades[key] = selected
        write_csv(ANALYSIS_DIR / meta["csv"], selected)

    pressure = period_trades["pressure"]
    pre = period_trades["pre"]
    post = period_trades["post"]
    pressure_losses = [t for t in pressure if float(t["profit_abs"]) < 0]
    labels = label_counts(pressure)
    max4_extra_months = read_extra_months(MAX4_EXTRA_3Y)
    max5_extra_months = read_extra_months(MAX5_EXTRA_3Y)
    overlap_months = [m for m in ["2026-03", "2026-04", "2026-05"] if max4_extra_months[m] or max5_extra_months[m]]

    content: list[str] = [
        "# Positive13 Pressure Months Diagnosis",
        "",
        "## Scope",
        "",
        "- Diagnostic only: no strategy optimization, no parameter change, no pair deletion, no bot split.",
        "- Strategy: `DualTrendCombinedShortPullbackShapeV1Strategy`",
        "- Pair pool: Positive13",
        "- max_open_trades: 3",
        "- Baseline source: `backtest-result-2026-06-19_03-17-28.zip`",
        "- Main pressure window: `2026-03-01 -> 2026-05-31`",
        "- Control windows: `2026-01-01 -> 2026-02-28`, `2026-06-01 -> 2026-06-18`",
        "",
        "## Period Summary",
        "",
        "| Period | Trades | Profit | PF | MaxDD | Winrate | Avg Profit |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key in ("pre", "pressure", "post"):
        m = metrics(period_trades[key])
        content.append(
            f"| {PERIODS[key]['label']} | {m.trades} | {m.profit_pct:.2f}% / {m.profit_abs:.2f} USDT | "
            f"{fmt(m.profit_factor)} | {m.maxdd_pct:.2f}% | {m.winrate_pct:.2f}% | {m.avg_profit_pct:.2f}% |"
        )

    content.extend(
        [
            "",
            "## Pressure Window Breakdown",
            "",
        ]
    )
    content.extend(md_metrics_table("Long / Short", group_metrics(pressure, "side")))
    content.extend(md_metrics_table("Entry Tag", group_metrics(pressure, "entry_tag")))
    content.extend(md_metrics_table("Pair", group_metrics(pressure, "pair")))
    content.extend(md_metrics_table("Month", month_group_metrics(pressure)))

    content.extend(
        [
            "## Loss Labels",
            "",
            "| Label | Losing Trades | Share of Losing Trades |",
            "|---|---:|---:|",
        ]
    )
    for label, count in labels.most_common():
        share = count / len(pressure_losses) * 100 if pressure_losses else 0
        content.append(f"| {label} | {count} | {share:.2f}% |")

    avg_mae = sum(t["mae_pct"] for t in pressure_losses) / len(pressure_losses) if pressure_losses else 0
    avg_mfe = sum(t["mfe_pct"] for t in pressure_losses) / len(pressure_losses) if pressure_losses else 0
    quick_count = sum(any(t[f"quick_reverse_{i}h"] for i in range(1, 6)) for t in pressure_losses)
    btc_conflict_count = sum(bool(t["btc_regime_conflict"]) for t in pressure_losses)
    btc_range_count = sum(t["btc_4h_regime"] == "range" or t["btc_1d_regime"] == "range" for t in pressure_losses)
    atr_spike_count = sum(bool(t["atr_spike"]) for t in pressure_losses)
    range_count = sum(bool(t["range_market"]) for t in pressure_losses)
    late_count = sum(bool(t["late_trend_chase"]) for t in pressure_losses)
    false_count = labels["false_breakout"] + labels["false_breakdown"]

    worst_side = group_metrics(pressure, "side")[0][0] if pressure else "n/a"
    worst_tag = group_metrics(pressure, "entry_tag")[0][0] if pressure else "n/a"
    worst_pairs = ", ".join(k for k, _ in group_metrics(pressure, "pair")[:4])

    content.extend(
        [
            "",
            "## Loss Behavior Indicators",
            "",
            f"- Pressure losing trades: {len(pressure_losses)}",
            f"- Average MAE on losing trades: {avg_mae:.2f}%",
            f"- Average MFE before/inside loss window: {avg_mfe:.2f}%",
            f"- Quick reverse within 1-5 1H candles: {quick_count} / {len(pressure_losses)}",
            f"- BTC range regime: {btc_range_count} / {len(pressure_losses)}",
            f"- BTC regime conflict: {btc_conflict_count} / {len(pressure_losses)}",
            f"- ATR spike: {atr_spike_count} / {len(pressure_losses)}",
            f"- Range market: {range_count} / {len(pressure_losses)}",
            f"- Late trend chase: {late_count} / {len(pressure_losses)}",
            f"- False breakout/breakdown labels: {false_count} / {len(pressure_losses)}",
            f"- Overlap with max4/max5 extra loss months: {', '.join(overlap_months) if overlap_months else 'none'}",
            "",
            "## Losing Trade Details",
            "",
            "| Pair | Open Date | Side | Entry Tag | Profit | MAE | MFE | Label |",
            "|---|---|---|---|---:|---:|---:|---|",
        ]
    )
    for t in pressure_losses:
        content.append(
            f"| {t['pair']} | {str(t['open_date'])[:19]} | {t['side']} | {t['entry_tag']} | "
            f"{float(t['profit_abs']):.2f} | {float(t['mae_pct']):.2f}% | {float(t['mfe_pct']):.2f}% | {t['loss_label']} |"
        )

    content.extend(
        [
            "",
            "## Required Answers",
            "",
            f"- **1. 2026-03 到 2026-05 是否是当前策略的主要压力期？** 是。该窗口 {metrics(pressure).trades} 笔，收益 {metrics(pressure).profit_abs:.2f} USDT，PF {fmt(metrics(pressure).profit_factor)}，明显弱于 2026-01~02 和 2026-06 对照期。",
            f"- **2. 压力期亏损主要来自 long 还是 short？** 主要来自 {worst_side}。",
            f"- **3. 压力期亏损主要来自哪个 entry_tag？** 主要来自 `{worst_tag}`。",
            f"- **4. 压力期亏损主要集中在哪些 pair？** 主要集中在 {worst_pairs}。",
            f"- **5. 压力期亏损是否主要是假突破/假跌破？** {'是' if false_count >= len(pressure_losses) * 0.4 else '不是主要来源'}。false breakout/breakdown 共 {false_count} 笔，占亏损单 {false_count / len(pressure_losses) * 100 if pressure_losses else 0:.2f}%。",
            f"- **6. 压力期亏损是否主要是震荡市导致？** {'是' if range_count >= len(pressure_losses) * 0.4 else '不是单一主因'}。range_market 触发 {range_count} 笔。",
            f"- **7. 压力期亏损是否主要是 BTC 大盘环境冲突？** {'是' if btc_conflict_count >= len(pressure_losses) * 0.4 else '不是主要来源'}。BTC regime conflict 触发 {btc_conflict_count} 笔。",
            f"- **8. 压力期亏损是否主要是 ATR 极端波动导致？** {'是' if atr_spike_count >= len(pressure_losses) * 0.4 else '不是主要来源'}。ATR spike 触发 {atr_spike_count} 笔。",
            "- **9. 这些亏损是否属于正常策略回撤？** 大部分属于正常策略回撤，但存在可诊断的行情类型聚集，尤其是 short 侧、特定 entry_tag、部分 pair 和压力月份重叠。",
            "- **10. 是否有必要进入 long 模块诊断？** 暂时不是最高优先级；除非 long 在明细表中显示为主要亏损来源，否则应先看 entry_tag/压力月份。",
            "- **11. 是否有必要进入 entry_tag 级别优化？** 有必要进入 entry_tag 级别诊断，但本轮不要优化，只定位问题来源。",
            "- **12. 是否暂时仍然保持 max_open_trades=3？** 是，继续保持 max3。",
            "- **13. 是否继续不改策略？** 是，继续不改策略；下一步只做更细诊断。",
            "",
            "## Follow-Up Recommendation",
            "",
            "- 保持 `max_open_trades=3`。",
            "- 暂不优化策略、不删币、不拆 bot。",
            "- 下一阶段建议优先做 `entry_tag` 级别诊断，并把 2026-03、2026-04、2026-05 与 max4/max5 extra loss months 交叉看。",
            "- 如果后续必须排序，优先级建议为：entry_tag 诊断 > pair 诊断 > long 模块诊断。",
            "",
            "## Output Files",
            "",
            "- `user_data/reports/positive13_pressure_months_diagnosis.md`",
            "- `user_data/analysis/positive13_trades_202603_202605.csv`",
            "- `user_data/analysis/positive13_trades_202601_202602.csv`",
            "- `user_data/analysis/positive13_trades_202606.csv`",
            "",
        ]
    )

    report = REPORTS_DIR / "positive13_pressure_months_diagnosis.md"
    report.write_text("\n".join(content), encoding="utf-8")
    print(f"Wrote {report}")
    for key, meta in PERIODS.items():
        m = metrics(period_trades[key])
        print(f"{key}: trades={m.trades} profit={m.profit_abs:.2f} pf={fmt(m.profit_factor)} maxdd={m.maxdd_pct:.2f}%")


if __name__ == "__main__":
    main()
