#!/usr/bin/env python3
"""Audit multi-timeframe extreme RSI reversal signals without trading.

This module is intentionally independent from Freqtrade strategy classes. It
reads local OHLCV data, detects completed-candle signals, and measures forward
outcomes. It never creates orders or changes the live strategy/configuration.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


ROOT = Path("/freqtrade") if Path("/freqtrade/user_data").exists() else Path(__file__).resolve().parents[2]
USER_DATA = ROOT / "user_data"
DATA_DIR = USER_DATA / "data" / "binance" / "futures"
ANALYSIS_DIR = USER_DATA / "analysis"
REPORTS_DIR = USER_DATA / "reports"
CONFIG = USER_DATA / "config.backtest.dualtrend.combined.top50.positive13.max3.json"

START = pd.Timestamp("2023-06-18T00:00:00Z")
END = pd.Timestamp("2026-06-18T23:59:59Z")
RSI_PERIOD = 14
ATR_PERIOD = 14
CONFIRMATION_TTL_HOURS = 72
FORWARD_HOURS = (6, 24, 72)

ENTRY_TAGS = {
    "long": "extreme_oversold_reversal_long",
    "short": "extreme_overbought_reversal_short",
}

VARIANTS = {
    "A": {
        "label": "4H + 1H extreme",
        "long": {"rsi_4h": 15.0, "rsi_1h": 10.0},
        "short": {"rsi_4h": 85.0, "rsi_1h": 90.0},
    },
    "B": {
        "label": "A + strict 1D",
        "long": {"rsi_1d": 25.0, "rsi_4h": 15.0, "rsi_1h": 10.0},
        "short": {"rsi_1d": 75.0, "rsi_4h": 85.0, "rsi_1h": 90.0},
    },
    "C": {
        "label": "super extreme",
        "long": {"rsi_1d": 10.0, "rsi_4h": 5.0, "rsi_1h": 5.0},
        "short": {"rsi_1d": 90.0, "rsi_4h": 95.0, "rsi_1h": 95.0},
    },
}


@dataclass
class Signal:
    variant: str
    variant_label: str
    pair: str
    signal_date: str
    extreme_date: str
    year: int
    side: str
    entry_tag: str
    entry_price: float
    stop_price: float
    risk_pct: float
    confirmation_delay_h: int
    rsi_1d: float
    rsi_4h: float
    rsi_1h: float
    ema20_1h: float
    atr_1h: float
    return_6h_pct: float
    return_24h_pct: float
    return_72h_pct: float
    mfe_6h_pct: float
    mfe_24h_pct: float
    mfe_72h_pct: float
    mae_6h_pct: float
    mae_24h_pct: float
    mae_72h_pct: float
    first_to_1r: bool
    first_to_2r: bool
    first_to_stop: bool
    max_r_72h: float
    min_r_72h: float


def pair_stem(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def read_ohlcv(pair: str, timeframe: str) -> pd.DataFrame:
    path = DATA_DIR / f"{pair_stem(pair)}-{timeframe}-futures.feather"
    frame = pd.read_feather(path)
    frame["date"] = pd.to_datetime(frame["date"], utc=True).astype("datetime64[ns, UTC]")
    return frame.sort_values("date").drop_duplicates("date").reset_index(drop=True)


def wilder_rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, float("nan"))
    rsi = 100.0 - 100.0 / (1.0 + rs)
    rsi = rsi.mask((avg_loss == 0) & (avg_gain > 0), 100.0)
    return rsi.mask((avg_gain == 0) & (avg_loss > 0), 0.0)


def wilder_atr(frame: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    previous_close = frame["close"].shift(1)
    true_range = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - previous_close).abs(),
            (frame["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def add_1h_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["rsi_1h"] = wilder_rsi(out["close"])
    out["ema20_1h"] = out["close"].ewm(span=20, adjust=False, min_periods=20).mean()
    out["atr_1h"] = wilder_atr(out)
    out["prior_6_high"] = out["high"].shift(1).rolling(6, min_periods=6).max()
    out["prior_6_low"] = out["low"].shift(1).rolling(6, min_periods=6).min()
    out["prior_12_low"] = out["low"].shift(1).rolling(12, min_periods=12).min()
    out["prior_12_high"] = out["high"].shift(1).rolling(12, min_periods=12).max()
    return out


def merge_timeframes(pair: str) -> pd.DataFrame:
    one_hour = add_1h_indicators(read_ohlcv(pair, "1h"))
    four_hour = read_ohlcv(pair, "4h")[["date", "close"]].copy()
    daily = read_ohlcv(pair, "1d")[["date", "close"]].copy()
    four_hour["rsi_4h"] = wilder_rsi(four_hour["close"])
    daily["rsi_1d"] = wilder_rsi(daily["close"])

    # Informative candles become usable only after they have closed.
    four_hour["available_date"] = (four_hour["date"] + pd.Timedelta(hours=4)).astype("datetime64[ns, UTC]")
    daily["available_date"] = (daily["date"] + pd.Timedelta(days=1)).astype("datetime64[ns, UTC]")
    out = pd.merge_asof(
        one_hour.sort_values("date"),
        four_hour[["available_date", "rsi_4h"]].sort_values("available_date"),
        left_on="date",
        right_on="available_date",
        direction="backward",
    ).drop(columns="available_date")
    out = pd.merge_asof(
        out.sort_values("date"),
        daily[["available_date", "rsi_1d"]].sort_values("available_date"),
        left_on="date",
        right_on="available_date",
        direction="backward",
    ).drop(columns="available_date")
    return out.reset_index(drop=True)


def is_extreme(row: pd.Series, variant: str, side: str) -> bool:
    limits = VARIANTS[variant][side]
    if side == "long":
        return all(float(row[name]) <= threshold for name, threshold in limits.items())
    return all(float(row[name]) >= threshold for name, threshold in limits.items())


def is_confirmation(frame: pd.DataFrame, index: int, side: str) -> bool:
    if index <= 0:
        return False
    row = frame.iloc[index]
    previous = frame.iloc[index - 1]
    if side == "long":
        rsi_cross = float(previous["rsi_1h"]) < 20.0 <= float(row["rsi_1h"])
        return rsi_cross and row["close"] > row["prior_6_high"] and row["close"] > row["ema20_1h"]
    rsi_cross = float(previous["rsi_1h"]) > 80.0 >= float(row["rsi_1h"])
    return rsi_cross and row["close"] < row["prior_6_low"] and row["close"] < row["ema20_1h"]


def forward_stats(frame: pd.DataFrame, index: int, side: str, entry: float, stop: float) -> dict[str, Any] | None:
    if index + max(FORWARD_HOURS) >= len(frame):
        return None
    risk = entry - stop if side == "long" else stop - entry
    if not math.isfinite(risk) or risk <= 0:
        return None
    result: dict[str, Any] = {}
    for hours in FORWARD_HOURS:
        future = frame.iloc[index + 1 : index + hours + 1]
        final_close = float(future.iloc[-1]["close"])
        if side == "long":
            result[f"return_{hours}h_pct"] = (final_close / entry - 1.0) * 100.0
            result[f"mfe_{hours}h_pct"] = (float(future["high"].max()) / entry - 1.0) * 100.0
            result[f"mae_{hours}h_pct"] = (entry - float(future["low"].min())) / entry * 100.0
        else:
            result[f"return_{hours}h_pct"] = (entry / final_close - 1.0) * 100.0
            result[f"mfe_{hours}h_pct"] = (entry - float(future["low"].min())) / entry * 100.0
            result[f"mae_{hours}h_pct"] = (float(future["high"].max()) - entry) / entry * 100.0

    first_1r: int | None = None
    first_2r: int | None = None
    first_stop: int | None = None
    path = frame.iloc[index + 1 : index + 73]
    for offset, (_, candle) in enumerate(path.iterrows(), start=1):
        if side == "long":
            stop_hit = float(candle["low"]) <= stop
            one_hit = float(candle["high"]) >= entry + risk
            two_hit = float(candle["high"]) >= entry + 2.0 * risk
        else:
            stop_hit = float(candle["high"]) >= stop
            one_hit = float(candle["low"]) <= entry - risk
            two_hit = float(candle["low"]) <= entry - 2.0 * risk
        # With OHLCV, intrabar order is unknown; count simultaneous hits as stop-first.
        if stop_hit and first_stop is None:
            first_stop = offset
        if not stop_hit and one_hit and first_1r is None:
            first_1r = offset
        if not stop_hit and two_hit and first_2r is None:
            first_2r = offset

    result["first_to_1r"] = first_1r is not None and (first_stop is None or first_1r < first_stop)
    result["first_to_2r"] = first_2r is not None and (first_stop is None or first_2r < first_stop)
    result["first_to_stop"] = first_stop is not None and (first_1r is None or first_stop <= first_1r)
    if side == "long":
        result["max_r_72h"] = (float(path["high"].max()) - entry) / risk
        result["min_r_72h"] = (float(path["low"].min()) - entry) / risk
    else:
        result["max_r_72h"] = (entry - float(path["low"].min())) / risk
        result["min_r_72h"] = (entry - float(path["high"].max())) / risk
    return result


def scan_pair(pair: str, frame: pd.DataFrame) -> tuple[list[Signal], list[dict[str, Any]]]:
    signals: list[Signal] = []
    funnel: list[dict[str, Any]] = []
    required = ["rsi_1h", "rsi_4h", "rsi_1d", "ema20_1h", "atr_1h", "prior_12_low", "prior_12_high"]
    valid = frame.dropna(subset=required).copy()
    valid = valid[(valid["date"] >= START - pd.Timedelta(hours=CONFIRMATION_TTL_HOURS)) & (valid["date"] <= END)]
    valid = valid.reset_index(drop=True)

    for variant in VARIANTS:
        for side in ("long", "short"):
            active_index: int | None = None
            active_date: pd.Timestamp | None = None
            in_extreme_episode = False
            extreme_candles = 0
            extreme_episodes = 0
            confirmations = 0
            matched_confirmations = 0
            for index in range(1, len(valid)):
                row = valid.iloc[index]
                confirmation_now = is_confirmation(valid, index, side)
                confirmations += int(confirmation_now and row["date"] >= START)
                extreme_now = is_extreme(row, variant, side)
                if extreme_now:
                    extreme_candles += int(row["date"] >= START)
                    if not in_extreme_episode:
                        extreme_episodes += int(row["date"] >= START)
                        active_index = index
                        active_date = row["date"]
                    in_extreme_episode = True
                elif in_extreme_episode:
                    in_extreme_episode = False

                if active_index is None or active_date is None:
                    continue
                age = index - active_index
                if age > CONFIRMATION_TTL_HOURS:
                    active_index = None
                    active_date = None
                    continue
                if row["date"] < START or not confirmation_now:
                    continue

                matched_confirmations += 1
                entry = float(row["close"])
                atr = float(row["atr_1h"])
                stop = (
                    float(row["prior_12_low"]) - 0.3 * atr
                    if side == "long"
                    else float(row["prior_12_high"]) + 0.3 * atr
                )
                outcome = forward_stats(valid, index, side, entry, stop)
                if outcome is not None:
                    risk_pct = abs(entry - stop) / entry * 100.0
                    signals.append(
                        Signal(
                            variant=variant,
                            variant_label=str(VARIANTS[variant]["label"]),
                            pair=pair,
                            signal_date=row["date"].isoformat(),
                            extreme_date=active_date.isoformat(),
                            year=int(row["date"].year),
                            side=side,
                            entry_tag=ENTRY_TAGS[side],
                            entry_price=entry,
                            stop_price=stop,
                            risk_pct=risk_pct,
                            confirmation_delay_h=age,
                            rsi_1d=float(row["rsi_1d"]),
                            rsi_4h=float(row["rsi_4h"]),
                            rsi_1h=float(row["rsi_1h"]),
                            ema20_1h=float(row["ema20_1h"]),
                            atr_1h=atr,
                            **outcome,
                        )
                    )
                # One signal per extreme episode; a fresh extreme episode is required.
                active_index = None
                active_date = None
                in_extreme_episode = False
            funnel.append(
                {
                    "pair": pair,
                    "variant": variant,
                    "side": side,
                    "extreme_candles": extreme_candles,
                    "extreme_episodes": extreme_episodes,
                    "all_market_confirmations": confirmations,
                    "confirmations_within_72h_of_extreme": matched_confirmations,
                    "auditable_signals": sum(
                        signal.pair == pair and signal.variant == variant and signal.side == side
                        for signal in signals
                    ),
                }
            )
    return signals, funnel


def mean(rows: list[Signal], field: str) -> float:
    values = [float(getattr(row, field)) for row in rows]
    return sum(values) / len(values) if values else 0.0


def summarize(rows: list[Signal], group_type: str, group_value: str) -> dict[str, Any]:
    count = len(rows)
    result: dict[str, Any] = {"group_type": group_type, "group_value": group_value, "signals": count}
    for hours in FORWARD_HOURS:
        result[f"avg_return_{hours}h_pct"] = mean(rows, f"return_{hours}h_pct")
        result[f"avg_mfe_{hours}h_pct"] = mean(rows, f"mfe_{hours}h_pct")
        result[f"avg_mae_{hours}h_pct"] = mean(rows, f"mae_{hours}h_pct")
    for field in ("first_to_1r", "first_to_2r", "first_to_stop"):
        result[f"{field}_pct"] = sum(bool(getattr(row, field)) for row in rows) / count * 100.0 if count else 0.0
    result["avg_max_r"] = mean(rows, "max_r_72h")
    result["avg_min_r"] = mean(rows, "min_r_72h")
    return result


def grouped(rows: list[Signal], field: str) -> list[dict[str, Any]]:
    values = sorted({str(getattr(row, field)) for row in rows})
    return [summarize([row for row in rows if str(getattr(row, field)) == value], field, value) for value in values]


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    materialized = list(rows)
    columns = fieldnames or (list(materialized[0]) if materialized else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        if materialized:
            writer.writerows(materialized)


def fmt(value: float) -> str:
    return f"{value:.2f}"


def summary_table(rows: list[dict[str, Any]], title: str) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Group | Signals | Ret 6h | Ret 24h | Ret 72h | MFE/MAE 72h | 1R first | 2R first | Stop first | Avg max/min R |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['group_value']} | {row['signals']} | {fmt(row['avg_return_6h_pct'])}% | "
            f"{fmt(row['avg_return_24h_pct'])}% | {fmt(row['avg_return_72h_pct'])}% | "
            f"{fmt(row['avg_mfe_72h_pct'])}/{fmt(row['avg_mae_72h_pct'])}% | "
            f"{fmt(row['first_to_1r_pct'])}% | {fmt(row['first_to_2r_pct'])}% | "
            f"{fmt(row['first_to_stop_pct'])}% | {fmt(row['avg_max_r'])}/{fmt(row['avg_min_r'])} |"
        )
    lines.append("")
    return lines


def evidence_label(row: dict[str, Any]) -> str:
    if row["signals"] < 10:
        return "样本不足"
    positive_returns = sum(row[f"avg_return_{h}h_pct"] > 0 for h in FORWARD_HOURS)
    if positive_returns == 3 and row["first_to_1r_pct"] > row["first_to_stop_pct"] and row["avg_max_r"] > 1.0:
        return "有初步统计优势"
    if positive_returns >= 2 and row["avg_max_r"] > abs(row["avg_min_r"]):
        return "弱正向证据"
    return "未显示稳定优势"


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    pairs = list(config["exchange"]["pair_whitelist"])
    all_signals: list[Signal] = []
    funnel_rows: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    for pair in pairs:
        frame = merge_timeframes(pair)
        available = frame[(frame["date"] >= START) & (frame["date"] <= END)]
        coverage.append(
            {
                "pair": pair,
                "start": available["date"].min().isoformat() if not available.empty else "",
                "end": available["date"].max().isoformat() if not available.empty else "",
                "candles_1h": len(available),
            }
        )
        pair_signals, pair_funnel = scan_pair(pair, frame)
        all_signals.extend(pair_signals)
        funnel_rows.extend(pair_funnel)

    detail_rows = [asdict(signal) for signal in all_signals]
    summary_rows: list[dict[str, Any]] = []
    for variant in VARIANTS:
        selected = [signal for signal in all_signals if signal.variant == variant]
        base = summarize(selected, "variant", variant)
        base["variant"] = variant
        base["variant_label"] = VARIANTS[variant]["label"]
        summary_rows.append(base)
        for field in ("side", "pair", "year"):
            for row in grouped(selected, field):
                row["variant"] = variant
                row["variant_label"] = VARIANTS[variant]["label"]
                summary_rows.append(row)

    write_csv(
        ANALYSIS_DIR / "positive13_extreme_reversal_signals.csv",
        detail_rows,
        [field.name for field in fields(Signal)],
    )
    write_csv(ANALYSIS_DIR / "positive13_extreme_reversal_summary.csv", summary_rows)
    write_csv(ANALYSIS_DIR / "positive13_extreme_reversal_data_coverage.csv", coverage)
    write_csv(ANALYSIS_DIR / "positive13_extreme_reversal_funnel.csv", funnel_rows)

    variant_summary = [row for row in summary_rows if row["group_type"] == "variant"]
    side_summary = [row for row in summary_rows if row["group_type"] == "side"]
    pair_summary_a = [row for row in summary_rows if row["group_type"] == "pair" and row["variant"] == "A"]
    year_summary = [row for row in summary_rows if row["group_type"] == "year"]

    long_a = next((row for row in side_summary if row["variant"] == "A" and row["group_value"] == "long"), None)
    short_a = next((row for row in side_summary if row["variant"] == "A" and row["group_value"] == "short"), None)
    valid_pairs = [
        row["group_value"]
        for row in pair_summary_a
        if row["signals"] >= 6 and row["avg_return_24h_pct"] > 0 and row["avg_return_72h_pct"] > 0
        and row["first_to_1r_pct"] > row["first_to_stop_pct"]
    ]
    best_side = "无法判断"
    if long_a and short_a:
        long_score = long_a["avg_return_24h_pct"] + long_a["avg_return_72h_pct"] + long_a["avg_max_r"]
        short_score = short_a["avg_return_24h_pct"] + short_a["avg_return_72h_pct"] + short_a["avg_max_r"]
        best_side = "long" if long_score > short_score else "short"
    a_summary = next(row for row in variant_summary if row["group_value"] == "A")
    advantage = evidence_label(a_summary)
    enter_backtest = a_summary["signals"] >= 30 and advantage in {"有初步统计优势", "弱正向证据"}

    report: list[str] = [
        "# Positive13 Extreme Reversal Signal Audit",
        "",
        "## Scope And Method",
        "",
        "- Independent signal audit only. No orders, no strategy merge, no live configuration changes.",
        "- Pair pool: Positive13; interval: 2023-06-18 through 2026-06-18.",
        "- RSI/ATR use Wilder smoothing with period 14; EMA20 uses standard exponential smoothing.",
        "- 4H and 1D values are shifted to their candle close time to prevent lookahead bias.",
        "- An extreme episode may wait up to 72 completed 1H candles for confirmation; one signal is emitted per episode.",
        "- Breakout levels use the preceding 6 candles; stops use the preceding 12 candles plus 0.3 ATR.",
        "- Forward path is 72h. If stop and target touch in the same OHLC candle, stop is conservatively counted first.",
        "- A/B/C are overlapping condition sets and must not be added together.",
        "",
        "## Variant Results",
        "",
    ]
    report.extend(summary_table(variant_summary, "A / B / C Comparison"))
    report.extend(summary_table(side_summary, "By Side"))
    report.extend(summary_table(year_summary, "By Year"))
    report.extend(summary_table(pair_summary_a, "Variant A By Pair"))
    funnel_totals = []
    for variant in VARIANTS:
        for side in ("long", "short"):
            selected = [row for row in funnel_rows if row["variant"] == variant and row["side"] == side]
            funnel_totals.append(
                {
                    "variant": variant,
                    "side": side,
                    "extreme_candles": sum(row["extreme_candles"] for row in selected),
                    "extreme_episodes": sum(row["extreme_episodes"] for row in selected),
                    "all_market_confirmations": sum(row["all_market_confirmations"] for row in selected),
                    "matched": sum(row["confirmations_within_72h_of_extreme"] for row in selected),
                    "signals": sum(row["auditable_signals"] for row in selected),
                }
            )
    report.extend(
        [
            "### Condition Funnel",
            "",
            "| Variant | Side | Extreme candles | Extreme episodes | Confirmations anywhere | Confirmed <=72h | Auditable signals |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in funnel_totals:
        report.append(
            f"| {row['variant']} | {row['side']} | {row['extreme_candles']} | {row['extreme_episodes']} | "
            f"{row['all_market_confirmations']} | {row['matched']} | {row['signals']} |"
        )
    report.append("")
    report.extend(
        [
            "## Conclusions",
            "",
            f"- **Does extreme reversal show a statistical edge?** {advantage}. Variant A has {a_summary['signals']} signals; the conclusion is based on forward returns, first-hit rates, and R excursion together rather than return alone.",
            f"- **Which side is better?** {best_side}, based on Variant A's combined 24h/72h return and average max-R score. This remains an audit conclusion, not a trading recommendation.",
            f"- **Which pairs look effective?** {', '.join(valid_pairs) if valid_pairs else 'None meet the minimum six-signal directional screen'}. Pairs below six signals are observation-only.",
            f"- **Should it enter strategy backtesting?** {'Yes: create a separate experimental backtest strategy next, but do not merge it into live trading.' if enter_backtest else 'Not yet: collect more evidence or revise the audit hypothesis before strategy backtesting.'}",
            "- RSI 1D 10/90 is used only in super-extreme Variant C, never as the default condition.",
            "",
            "## Output Files",
            "",
            "- `user_data/analysis/positive13_extreme_reversal_signals.csv`",
            "- `user_data/analysis/positive13_extreme_reversal_summary.csv`",
            "- `user_data/analysis/positive13_extreme_reversal_data_coverage.csv`",
            "- `user_data/analysis/positive13_extreme_reversal_funnel.csv`",
            "- `user_data/reports/positive13_extreme_reversal_signal_audit.md`",
            "",
        ]
    )
    (REPORTS_DIR / "positive13_extreme_reversal_signal_audit.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {len(all_signals)} signal rows across A/B/C")
    for row in variant_summary:
        print(row["group_value"], row["signals"], evidence_label(row))


if __name__ == "__main__":
    main()
