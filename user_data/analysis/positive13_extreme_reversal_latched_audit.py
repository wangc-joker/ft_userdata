#!/usr/bin/env python3
"""Round-2 latched Extreme Reversal signal audit.

Research-only: reads local candles and emits signal statistics. It does not
inherit from a strategy, create orders, or modify live/backtest configuration.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import positive13_extreme_reversal_signal_audit as v1


ROOT = v1.ROOT
USER_DATA = v1.USER_DATA
ANALYSIS_DIR = v1.ANALYSIS_DIR
REPORTS_DIR = v1.REPORTS_DIR
CONFIG = v1.CONFIG
START = v1.START
END = v1.END
TTLS = (24, 72, 120, 168)
CONFIRMATIONS = ("weak", "medium", "strong")

EVENT_VARIANTS = {
    "A": {
        "label": "loose",
        "long": {"rsi_4h": 25.0, "rsi_1h": 20.0},
        "short": {"rsi_4h": 75.0, "rsi_1h": 80.0},
    },
    "B": {
        "label": "medium",
        "long": {"rsi_1d": 40.0, "rsi_4h": 25.0, "rsi_1h": 20.0},
        "short": {"rsi_1d": 60.0, "rsi_4h": 75.0, "rsi_1h": 80.0},
    },
    "C": {
        "label": "strict",
        "long": {"rsi_1d": 30.0, "rsi_4h": 20.0, "rsi_1h": 15.0},
        "short": {"rsi_1d": 70.0, "rsi_4h": 80.0, "rsi_1h": 85.0},
    },
}

ENTRY_TAGS = {
    "long": "extreme_oversold_reversal_long",
    "short": "extreme_overbought_reversal_short",
}


@dataclass
class LatchedSignal:
    combination: str
    event_variant: str
    event_label: str
    watch_ttl_h: int
    confirmation: str
    pair: str
    side: str
    entry_tag: str
    event_start: str
    event_end: str
    signal_date: str
    year: int
    confirmation_delay_h: int
    entry_price: float
    stop_price: float
    risk_pct: float
    rsi_1d: float
    rsi_4h: float
    rsi_1h: float
    lower_wick_pct: float
    upper_wick_pct: float
    volume_ratio: float
    swept_recent_low_24_reclaimed: bool
    swept_recent_high_24_rejected: bool
    return_6h_pct: float
    return_24h_pct: float
    return_72h_pct: float
    mfe_24h_pct: float
    mfe_72h_pct: float
    mae_24h_pct: float
    mae_72h_pct: float
    first_to_1r: bool
    first_to_2r: bool
    first_to_stop: bool
    max_r_72h: float
    min_r_72h: float


def prepare_frame(pair: str) -> pd.DataFrame:
    frame = v1.merge_timeframes(pair)
    frame["prior_12_high"] = frame["high"].shift(1).rolling(12, min_periods=12).max()
    frame["prior_24_low"] = frame["low"].shift(1).rolling(24, min_periods=24).min()
    frame["prior_24_high"] = frame["high"].shift(1).rolling(24, min_periods=24).max()
    frame["volume_ma20"] = frame["volume"].shift(1).rolling(20, min_periods=20).mean()
    frame["volume_ratio"] = frame["volume"] / frame["volume_ma20"].replace(0.0, np.nan)
    candle_range = (frame["high"] - frame["low"]).replace(0.0, np.nan)
    frame["lower_wick_pct"] = (np.minimum(frame["open"], frame["close"]) - frame["low"]) / candle_range * 100.0
    frame["upper_wick_pct"] = (frame["high"] - np.maximum(frame["open"], frame["close"])) / candle_range * 100.0
    frame["swept_recent_low_24_reclaimed"] = (
        (frame["low"] < frame["prior_24_low"]) & (frame["close"] > frame["prior_24_low"])
    )
    frame["swept_recent_high_24_rejected"] = (
        (frame["high"] > frame["prior_24_high"]) & (frame["close"] < frame["prior_24_high"])
    )
    required = [
        "rsi_1d", "rsi_4h", "rsi_1h", "ema20_1h", "atr_1h",
        "prior_6_high", "prior_6_low", "prior_12_high", "prior_12_low",
        "prior_24_high", "prior_24_low", "volume_ratio",
    ]
    return frame.dropna(subset=required).reset_index(drop=True)


def event_mask(frame: pd.DataFrame, variant: str, side: str) -> np.ndarray:
    limits = EVENT_VARIANTS[variant][side]
    mask = np.ones(len(frame), dtype=bool)
    for name, threshold in limits.items():
        values = frame[name].to_numpy(dtype=float)
        mask &= values <= threshold if side == "long" else values >= threshold
    dates = frame["date"]
    return mask & (dates >= START).to_numpy() & (dates <= END).to_numpy()


def confirmation_masks(frame: pd.DataFrame, side: str) -> dict[str, np.ndarray]:
    rsi = frame["rsi_1h"]
    if side == "long":
        cross = (rsi.shift(1) < 30.0) & (rsi >= 30.0)
        weak = cross & (frame["close"] > frame["ema20_1h"])
        medium = weak & (frame["close"] > frame["prior_6_high"])
        strong = medium & (frame["close"] > frame["prior_12_high"]) & (frame["volume_ratio"] > 1.5)
    else:
        cross = (rsi.shift(1) > 70.0) & (rsi <= 70.0)
        weak = cross & (frame["close"] < frame["ema20_1h"])
        medium = weak & (frame["close"] < frame["prior_6_low"])
        strong = medium & (frame["close"] < frame["prior_12_low"]) & (frame["volume_ratio"] > 1.5)
    in_range = (frame["date"] >= START) & (frame["date"] <= END)
    return {
        "weak": (weak & in_range).to_numpy(dtype=bool),
        "medium": (medium & in_range).to_numpy(dtype=bool),
        "strong": (strong & in_range).to_numpy(dtype=bool),
    }


def episodes(mask: np.ndarray) -> list[tuple[int, int]]:
    padded = np.r_[False, mask, False].astype(np.int8)
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1) - 1
    return list(zip(starts.tolist(), ends.tolist()))


def first_true(mask: np.ndarray, start: int, end: int) -> int | None:
    if start > end:
        return None
    offsets = np.flatnonzero(mask[start : end + 1])
    return start + int(offsets[0]) if offsets.size else None


def make_signal(
    frame: pd.DataFrame,
    pair: str,
    variant: str,
    ttl: int,
    confirmation: str,
    side: str,
    episode: tuple[int, int],
    signal_index: int,
) -> LatchedSignal | None:
    start_index, end_index = episode
    row = frame.iloc[signal_index]
    entry = float(row["close"])
    atr = float(row["atr_1h"])
    stop = (
        float(row["prior_12_low"]) - 0.3 * atr
        if side == "long"
        else float(row["prior_12_high"]) + 0.3 * atr
    )
    outcome = v1.forward_stats(frame, signal_index, side, entry, stop)
    if outcome is None:
        return None
    combination = f"{variant}_{ttl}h_{confirmation}"
    return LatchedSignal(
        combination=combination,
        event_variant=variant,
        event_label=str(EVENT_VARIANTS[variant]["label"]),
        watch_ttl_h=ttl,
        confirmation=confirmation,
        pair=pair,
        side=side,
        entry_tag=ENTRY_TAGS[side],
        event_start=frame.iloc[start_index]["date"].isoformat(),
        event_end=frame.iloc[end_index]["date"].isoformat(),
        signal_date=row["date"].isoformat(),
        year=int(row["date"].year),
        confirmation_delay_h=signal_index - end_index,
        entry_price=entry,
        stop_price=stop,
        risk_pct=abs(entry - stop) / entry * 100.0,
        rsi_1d=float(row["rsi_1d"]),
        rsi_4h=float(row["rsi_4h"]),
        rsi_1h=float(row["rsi_1h"]),
        lower_wick_pct=float(row["lower_wick_pct"]),
        upper_wick_pct=float(row["upper_wick_pct"]),
        volume_ratio=float(row["volume_ratio"]),
        swept_recent_low_24_reclaimed=bool(row["swept_recent_low_24_reclaimed"]),
        swept_recent_high_24_rejected=bool(row["swept_recent_high_24_rejected"]),
        return_6h_pct=float(outcome["return_6h_pct"]),
        return_24h_pct=float(outcome["return_24h_pct"]),
        return_72h_pct=float(outcome["return_72h_pct"]),
        mfe_24h_pct=float(outcome["mfe_24h_pct"]),
        mfe_72h_pct=float(outcome["mfe_72h_pct"]),
        mae_24h_pct=float(outcome["mae_24h_pct"]),
        mae_72h_pct=float(outcome["mae_72h_pct"]),
        first_to_1r=bool(outcome["first_to_1r"]),
        first_to_2r=bool(outcome["first_to_2r"]),
        first_to_stop=bool(outcome["first_to_stop"]),
        max_r_72h=float(outcome["max_r_72h"]),
        min_r_72h=float(outcome["min_r_72h"]),
    )


def scan_pair(pair: str, frame: pd.DataFrame) -> tuple[list[LatchedSignal], list[dict[str, Any]]]:
    signals: list[LatchedSignal] = []
    funnel: list[dict[str, Any]] = []
    confirmation_by_side = {side: confirmation_masks(frame, side) for side in ("long", "short")}
    for variant in EVENT_VARIANTS:
        for side in ("long", "short"):
            event_episodes = episodes(event_mask(frame, variant, side))
            for ttl in TTLS:
                for confirmation in CONFIRMATIONS:
                    found = 0
                    confirmation_mask = confirmation_by_side[side][confirmation]
                    for position, episode in enumerate(event_episodes):
                        _, event_end = episode
                        next_start = event_episodes[position + 1][0] if position + 1 < len(event_episodes) else len(frame)
                        watch_end = min(event_end + ttl, next_start - 1, len(frame) - 1)
                        signal_index = first_true(confirmation_mask, event_end + 1, watch_end)
                        if signal_index is None:
                            continue
                        signal = make_signal(frame, pair, variant, ttl, confirmation, side, episode, signal_index)
                        if signal is not None:
                            signals.append(signal)
                            found += 1
                    funnel.append(
                        {
                            "pair": pair,
                            "combination": f"{variant}_{ttl}h_{confirmation}",
                            "event_variant": variant,
                            "watch_ttl_h": ttl,
                            "confirmation": confirmation,
                            "side": side,
                            "extreme_event_count": len(event_episodes),
                            "final_signal_count": found,
                        }
                    )
    return signals, funnel


def pf_proxy(rows: list[LatchedSignal]) -> float:
    values = [row.return_72h_pct for row in rows]
    wins = sum(value for value in values if value > 0)
    losses = -sum(value for value in values if value < 0)
    return wins / losses if losses else (math.inf if wins else 0.0)


def avg(rows: list[LatchedSignal], field: str) -> float:
    return sum(float(getattr(row, field)) for row in rows) / len(rows) if rows else 0.0


def summarize(
    rows: list[LatchedSignal],
    event_count: int | str,
    group_type: str,
    group_value: str,
) -> dict[str, Any]:
    count = len(rows)
    return {
        "group_type": group_type,
        "group_value": group_value,
        "extreme_event_count": event_count,
        "final_signal_count": count,
        "sample_status": "enough" if count >= 50 else "insufficient",
        "pf_proxy_72h": pf_proxy(rows),
        "avg_return_6h_pct": avg(rows, "return_6h_pct"),
        "avg_return_24h_pct": avg(rows, "return_24h_pct"),
        "avg_return_72h_pct": avg(rows, "return_72h_pct"),
        "avg_mfe_24h_pct": avg(rows, "mfe_24h_pct"),
        "avg_mae_24h_pct": avg(rows, "mae_24h_pct"),
        "avg_mfe_72h_pct": avg(rows, "mfe_72h_pct"),
        "avg_mae_72h_pct": avg(rows, "mae_72h_pct"),
        "first_to_1r_pct": sum(row.first_to_1r for row in rows) / count * 100.0 if count else 0.0,
        "first_to_2r_pct": sum(row.first_to_2r for row in rows) / count * 100.0 if count else 0.0,
        "first_to_stop_pct": sum(row.first_to_stop for row in rows) / count * 100.0 if count else 0.0,
        "avg_max_r": avg(rows, "max_r_72h"),
        "avg_min_r": avg(rows, "min_r_72h"),
        "avg_lower_wick_pct": avg(rows, "lower_wick_pct"),
        "avg_upper_wick_pct": avg(rows, "upper_wick_pct"),
        "avg_volume_ratio": avg(rows, "volume_ratio"),
        "low_sweep_reclaim_pct": sum(row.swept_recent_low_24_reclaimed for row in rows) / count * 100.0 if count else 0.0,
        "high_sweep_reject_pct": sum(row.swept_recent_high_24_rejected for row in rows) / count * 100.0 if count else 0.0,
    }


def write_csv(path: Path, rows: Iterable[dict[str, Any]], columns: list[str] | None = None) -> None:
    materialized = list(rows)
    fieldnames = columns or (list(materialized[0]) if materialized else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(materialized)


def format_num(value: Any) -> str:
    number = float(value)
    return "inf" if math.isinf(number) else f"{number:.2f}"


def quality_pass(row: dict[str, Any]) -> bool:
    return (
        row["final_signal_count"] >= 50
        and row["pf_proxy_72h"] >= 1.20
        and row["first_to_1r_pct"] > row["first_to_stop_pct"]
        and row["avg_max_r"] > abs(row["avg_min_r"])
    )


def combo_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Combination | Events | Signals | Status | PF proxy | Ret 6/24/72h | MFE/MAE 24h | MFE/MAE 72h | 1R/2R/Stop first | Avg max/min R |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['group_value']} | {row['extreme_event_count']} | {row['final_signal_count']} | "
            f"{row['sample_status']} | {format_num(row['pf_proxy_72h'])} | "
            f"{format_num(row['avg_return_6h_pct'])}/{format_num(row['avg_return_24h_pct'])}/{format_num(row['avg_return_72h_pct'])}% | "
            f"{format_num(row['avg_mfe_24h_pct'])}/{format_num(row['avg_mae_24h_pct'])}% | "
            f"{format_num(row['avg_mfe_72h_pct'])}/{format_num(row['avg_mae_72h_pct'])}% | "
            f"{format_num(row['first_to_1r_pct'])}/{format_num(row['first_to_2r_pct'])}/{format_num(row['first_to_stop_pct'])}% | "
            f"{format_num(row['avg_max_r'])}/{format_num(row['avg_min_r'])} |"
        )
    return lines


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    pairs = list(config["exchange"]["pair_whitelist"])
    signals: list[LatchedSignal] = []
    funnel: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    for pair in pairs:
        frame = prepare_frame(pair)
        in_period = frame[(frame["date"] >= START) & (frame["date"] <= END)]
        coverage.append(
            {
                "pair": pair,
                "start": in_period["date"].min().isoformat() if not in_period.empty else "",
                "end": in_period["date"].max().isoformat() if not in_period.empty else "",
                "candles_1h": len(in_period),
            }
        )
        pair_signals, pair_funnel = scan_pair(pair, frame)
        signals.extend(pair_signals)
        funnel.extend(pair_funnel)

    combinations = [f"{variant}_{ttl}h_{confirmation}" for variant in EVENT_VARIANTS for ttl in TTLS for confirmation in CONFIRMATIONS]
    summary: list[dict[str, Any]] = []
    combo_summary: list[dict[str, Any]] = []
    for combination in combinations:
        combo_signals = [row for row in signals if row.combination == combination]
        combo_funnel = [row for row in funnel if row["combination"] == combination]
        total_events = sum(row["extreme_event_count"] for row in combo_funnel)
        combo_row = summarize(combo_signals, total_events, "combination", combination)
        combo_row["combination"] = combination
        combo_summary.append(combo_row)
        summary.append(combo_row)
        for field in ("side", "pair", "year"):
            values = sorted({str(getattr(row, field)) for row in combo_signals})
            for value in values:
                selected = [row for row in combo_signals if str(getattr(row, field)) == value]
                if field == "side":
                    event_count = sum(row["extreme_event_count"] for row in combo_funnel if row["side"] == value)
                elif field == "pair":
                    event_count = sum(row["extreme_event_count"] for row in combo_funnel if row["pair"] == value)
                else:
                    event_count = "-"
                detail = summarize(selected, event_count, field, value)
                detail["combination"] = combination
                summary.append(detail)

    write_csv(
        ANALYSIS_DIR / "positive13_extreme_reversal_latched_signals.csv",
        [asdict(row) for row in signals],
        [field.name for field in fields(LatchedSignal)],
    )
    write_csv(ANALYSIS_DIR / "positive13_extreme_reversal_latched_summary.csv", summary)
    write_csv(ANALYSIS_DIR / "positive13_extreme_reversal_latched_funnel.csv", funnel)
    write_csv(ANALYSIS_DIR / "positive13_extreme_reversal_latched_coverage.csv", coverage)

    ranked = sorted(
        combo_summary,
        key=lambda row: (
            quality_pass(row),
            row["final_signal_count"] >= 50,
            row["final_signal_count"],
            row["pf_proxy_72h"] if math.isfinite(row["pf_proxy_72h"]) else 999.0,
            row["avg_return_72h_pct"],
        ),
        reverse=True,
    )
    enough = [row for row in combo_summary if row["final_signal_count"] >= 50]
    passing = [row for row in ranked if quality_pass(row)]
    best = ranked[0]
    best_combo = best["group_value"]
    best_signals = [row for row in signals if row.combination == best_combo]
    best_funnel = [row for row in funnel if row["combination"] == best_combo]
    side_rows = [
        summarize(
            [row for row in best_signals if row.side == side],
            sum(row["extreme_event_count"] for row in best_funnel if row["side"] == side),
            "side",
            side,
        )
        for side in ("long", "short")
    ]
    observed_sides = [row for row in side_rows if row["final_signal_count"] > 0]
    best_side = max(observed_sides, key=lambda row: (row["pf_proxy_72h"], row["avg_return_72h_pct"]), default=None)
    pair_rows = []
    for pair in pairs:
        selected = [row for row in best_signals if row.pair == pair]
        if selected:
            pair_rows.append(
                summarize(
                    selected,
                    sum(row["extreme_event_count"] for row in best_funnel if row["pair"] == pair),
                    "pair",
                    pair,
                )
            )
    year_rows = [
        summarize(
            [row for row in best_signals if str(row.year) == year],
            "-",
            "year",
            year,
        )
        for year in sorted({str(row.year) for row in best_signals})
    ]
    keep_pairs = [
        row["group_value"] for row in pair_rows
        if row["final_signal_count"] >= 6
        and row["pf_proxy_72h"] >= 1.10
        and row["first_to_1r_pct"] > row["first_to_stop_pct"]
        and row["avg_max_r"] > abs(row["avg_min_r"])
    ]
    passing_text = ", ".join(f"`{row['group_value']}`" for row in passing) if passing else "None currently pass every audit gate."

    report: list[str] = [
        "# Positive13 Extreme Reversal Latched Signal Audit",
        "",
        "## Scope And Definitions",
        "",
        "- Round-2 signal audit only; no strategy backtest, no live merge, and no order generation.",
        "- Period: 2023-06-18 through 2026-06-18; Positive13 local futures candles.",
        "- An extreme event is one contiguous extreme episode. The watch timer starts after the episode's final candle.",
        "- A later extreme episode supersedes an older unconfirmed watch. Each episode emits at most one signal per combination.",
        "- 4H/1D candles become available only after close. Recent highs/lows and volume MA exclude the current candle.",
        "- PF proxy = gross positive direction-adjusted 72h returns / absolute gross negative 72h returns; it is not trade PF.",
        "- Combination rows overlap across TTL and confirmation variants; their signal counts must not be summed as unique market events.",
        "- Same-candle stop/target ambiguity is resolved conservatively as stop-first.",
        "- Acceptance: fewer than 50 signals is insufficient. A research candidate additionally needs PF proxy >=1.20, 1R-first > stop-first, and avg max-R > |avg min-R|.",
        "",
        "## All 36 Combinations",
        "",
    ]
    report.extend(combo_table(combo_summary))
    report.extend(
        [
            "",
            "## Ranked Candidates",
            "",
        ]
    )
    report.extend(combo_table(ranked[:10]))
    report.extend(
        [
            "",
            f"- Combinations with >=50 signals: {len(enough)} / {len(combo_summary)}.",
            f"- Combinations passing all audit gates: {len(passing)} / {len(combo_summary)}.",
            f"- Best ranked combination: `{best_combo}` ({best['final_signal_count']} signals, PF proxy {format_num(best['pf_proxy_72h'])}).",
            "",
            "## Best Combination By Side",
            "",
        ]
    )
    report.extend(combo_table(side_rows))
    report.extend(["", "## Best Combination By Pair", ""])
    report.extend(combo_table(sorted(pair_rows, key=lambda row: row["pf_proxy_72h"], reverse=True)))
    report.extend(["", "## Best Combination By Year", ""])
    report.extend(combo_table(year_rows))
    report.extend(
        [
            "",
            "## Best Combination Candlestick Descriptors",
            "",
            "| Side | Signals | Lower wick | Upper wick | Volume ratio | Low sweep reclaim | High sweep reject |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in side_rows:
        report.append(
            f"| {row['group_value']} | {row['final_signal_count']} | {format_num(row['avg_lower_wick_pct'])}% | "
            f"{format_num(row['avg_upper_wick_pct'])}% | {format_num(row['avg_volume_ratio'])} | "
            f"{format_num(row['low_sweep_reclaim_pct'])}% | {format_num(row['high_sweep_reject_pct'])}% |"
        )
    report.extend(
        [
            "",
            "## Required Conclusions",
            "",
            f"1. **Are conditions still too strict?** {'Yes. No combination reaches 50 signals.' if not enough else 'Not universally. At least one combination reaches the 50-signal minimum.'}",
            f"2. **Which groups deserve a real backtest?** {passing_text}",
            f"3. **Which side has more edge?** {best_side['group_value'] + ' is directionally better within the best-ranked combination, but has only ' + str(best_side['final_signal_count']) + ' signals and is not confirmed' if best_side else 'Insufficient side-level sample to decide'}.",
            f"4. **Which pairs are worth retaining?** {', '.join(keep_pairs) if keep_pairs else 'None meet the six-signal pair screen inside the best-ranked combination.'}",
            "",
            "## Candlestick Pattern Notes",
            "",
            "- Signal detail includes lower/upper wick percentage, volume ratio, low-sweep reclaim, and high-sweep rejection.",
            "- These are posterior descriptors only and are not used to filter the current audit.",
            "",
            "## Outputs",
            "",
            "- `user_data/analysis/positive13_extreme_reversal_latched_signals.csv`",
            "- `user_data/analysis/positive13_extreme_reversal_latched_summary.csv`",
            "- `user_data/analysis/positive13_extreme_reversal_latched_funnel.csv`",
            "- `user_data/analysis/positive13_extreme_reversal_latched_coverage.csv`",
            "- `user_data/reports/positive13_extreme_reversal_latched_audit.md`",
            "",
        ]
    )
    (REPORTS_DIR / "positive13_extreme_reversal_latched_audit.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {len(signals)} signal rows across {len(combo_summary)} combinations")
    print(f">=50 signals: {len(enough)}; passing: {len(passing)}; best: {best_combo}")


if __name__ == "__main__":
    main()
