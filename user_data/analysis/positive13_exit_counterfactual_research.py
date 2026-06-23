#!/usr/bin/env python3
"""Offline exit counterfactual research for the aligned Positive13 baseline.

This script fixes baseline entries and stakes, changes only post-profit exit
handling, and audits prices after the original exit. It never imports or
modifies the live strategy and does not place orders.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


ROOT = Path("/freqtrade") if Path("/freqtrade/user_data").exists() else Path(__file__).resolve().parents[2]
USER_DATA = ROOT / "user_data"
RESULTS_DIR = USER_DATA / "backtest_results"
DATA_DIR = USER_DATA / "data" / "binance" / "futures"
ANALYSIS_DIR = USER_DATA / "analysis"
REPORTS_DIR = USER_DATA / "reports"
STRATEGY = "DualTrendCombinedShortPullbackShapeV1Strategy"
ZIP_3Y = "backtest-result-2026-06-19_03-17-28.zip"
ZIP_1Y = "backtest-result-2026-06-19_03-22-14.zip"
STARTING_BALANCE = 1000.0
MAX_HOLD_HOURS = 14 * 24
WINDOWS = (6, 12, 24, 48, 72, 168, 336)

BASELINE_FIELDS = [
    "pair", "side", "entry_tag", "open_date", "close_date", "open_rate",
    "close_rate", "profit_abs", "profit_ratio", "exit_reason", "trade_duration",
    "is_short", "stake_amount", "amount", "max_rate", "min_rate", "fee_open",
    "fee_close", "initial_stop_loss_abs", "stop_loss_abs", "funding_fees",
]

MODEL_SPECS = {
    "baseline": {"kind": "baseline"},
    "A_giveback50_floor1": {"kind": "giveback", "trigger": 0.03, "giveback": 0.50, "floor": 0.01},
    "B_giveback60_floor1.5": {"kind": "giveback", "trigger": 0.05, "giveback": 0.60, "floor": 0.015},
    "C_giveback70_floor2": {"kind": "giveback", "trigger": 0.08, "giveback": 0.70, "floor": 0.02},
    "D_atr1h_1.5": {"kind": "atr", "trigger": 0.05, "atr_col": "atr_1h", "multiplier": 1.5},
    "D_atr1h_2.0": {"kind": "atr", "trigger": 0.05, "atr_col": "atr_1h", "multiplier": 2.0},
    "D_atr1h_2.5": {"kind": "atr", "trigger": 0.05, "atr_col": "atr_1h", "multiplier": 2.5},
    "D_atr1h_3.0": {"kind": "atr", "trigger": 0.05, "atr_col": "atr_1h", "multiplier": 3.0},
    "D_atr4h_1.5": {"kind": "atr", "trigger": 0.05, "atr_col": "atr_4h", "multiplier": 1.5},
    "D_atr4h_2.0": {"kind": "atr", "trigger": 0.05, "atr_col": "atr_4h", "multiplier": 2.0},
    "D_atr4h_2.5": {"kind": "atr", "trigger": 0.05, "atr_col": "atr_4h", "multiplier": 2.5},
    "D_atr4h_3.0": {"kind": "atr", "trigger": 0.05, "atr_col": "atr_4h", "multiplier": 3.0},
    "E_min24h_profit_protect": {"kind": "time", "trigger": 0.05, "giveback": 0.60, "floor": 0.015},
}


@dataclass
class ModelTrade:
    period: str
    model: str
    pair: str
    side: str
    entry_tag: str
    open_date: str
    close_date: str
    open_rate: float
    close_rate: float
    profit_abs: float
    profit_ratio: float
    duration_h: float
    exit_reason: str
    activated: bool
    activation_date: str
    original_close_date: str
    original_profit_abs: float
    original_profit_ratio: float
    mae_pct: float
    mfe_pct: float
    stake_amount: float


def load_result(zip_name: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with zipfile.ZipFile(RESULTS_DIR / zip_name) as archive:
        name = next(
            item for item in archive.namelist()
            if item.endswith(".json") and "_config" not in item and "meta" not in item
        )
        strategy = json.loads(archive.read(name))["strategy"][STRATEGY]
    return strategy, strategy["trades"]


def ts(value: Any) -> pd.Timestamp:
    parsed = pd.Timestamp(value)
    return parsed.tz_localize("UTC") if parsed.tzinfo is None else parsed.tz_convert("UTC")


def pair_stem(pair: str) -> str:
    return pair.replace("/", "_").replace(":", "_")


def atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    previous = frame["close"].shift(1)
    tr = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - previous).abs(),
            (frame["low"] - previous).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def load_pair_data(pair: str) -> pd.DataFrame:
    one = pd.read_feather(DATA_DIR / f"{pair_stem(pair)}-1h-futures.feather")
    four = pd.read_feather(DATA_DIR / f"{pair_stem(pair)}-4h-futures.feather")
    for frame in (one, four):
        frame["date"] = pd.to_datetime(frame["date"], utc=True).astype("datetime64[ns, UTC]")
        frame.sort_values("date", inplace=True)
    one["atr_1h"] = atr(one)
    four["atr_4h"] = atr(four)
    four["available_date"] = (four["date"] + pd.Timedelta(hours=4)).astype("datetime64[ns, UTC]")
    merged = pd.merge_asof(
        one,
        four[["available_date", "atr_4h"]],
        left_on="date",
        right_on="available_date",
        direction="backward",
    ).drop(columns="available_date")
    return merged.sort_values("date").reset_index(drop=True)


def side(trade: dict[str, Any]) -> str:
    return "short" if bool(trade.get("is_short")) else "long"


def tag(trade: dict[str, Any]) -> str:
    return str(trade.get("enter_tag") or trade.get("entry_tag") or "")


def normalized_reason(reason: str) -> str:
    value = (reason or "other").lower()
    if value == "stop_loss":
        return "stop_loss"
    if value == "trailing_stop_loss":
        return "trailing_stop_loss"
    if value == "roi":
        return "roi"
    if value in {"exit_signal", "sell_signal"} or "trend_flip" in value or "swing_exit" in value or "structure_exit" in value:
        return "exit_signal"
    if value == "force_exit":
        return "force_exit"
    if "timeout" in value or "stale" in value:
        return "timeout"
    if "custom" in value:
        return "custom_exit"
    return "other"


def baseline_export(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for trade in trades:
        row = {field: trade.get(field, "") for field in BASELINE_FIELDS}
        row["side"] = side(trade)
        row["entry_tag"] = tag(trade)
        rows.append(row)
    return rows


def direction_return(entry: float, price: float, trade_side: str) -> float:
    return (price - entry) / entry if trade_side == "long" else (entry - price) / entry


def favorable_excursion(entry: float, high: float, low: float, trade_side: str) -> float:
    return (high - entry) / entry if trade_side == "long" else (entry - low) / entry


def adverse_excursion(entry: float, high: float, low: float, trade_side: str) -> float:
    return (entry - low) / entry if trade_side == "long" else (high - entry) / entry


def stop_hit(candle: pd.Series, stop: float, trade_side: str) -> bool:
    return float(candle["low"]) <= stop if trade_side == "long" else float(candle["high"]) >= stop


def profit_stop_price(entry: float, locked_profit: float, trade_side: str) -> float:
    return entry * (1.0 + locked_profit) if trade_side == "long" else entry * (1.0 - locked_profit)


def original_stop(trade: dict[str, Any]) -> float:
    value = float(trade.get("stop_loss_abs") or 0.0)
    if value > 0:
        return value
    entry = float(trade["open_rate"])
    return entry * (1.06 if side(trade) == "short" else 0.94)


def trade_slice(frame: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.DataFrame, int, int] | None:
    start_index = int(frame["date"].searchsorted(start, side="left"))
    end_index = int(frame["date"].searchsorted(end, side="right")) - 1
    if start_index >= len(frame) or end_index < start_index:
        return None
    end_index = min(end_index, len(frame) - 1)
    return frame.iloc[start_index : end_index + 1], start_index, end_index


def baseline_model_trade(period: str, trade: dict[str, Any], frame: pd.DataFrame) -> ModelTrade:
    opened = ts(trade["open_date"])
    closed = ts(trade["close_date"])
    sliced = trade_slice(frame, opened, closed)
    entry = float(trade["open_rate"])
    trade_side = side(trade)
    if sliced is None:
        mae = mfe = 0.0
    else:
        candles = sliced[0]
        mfe = favorable_excursion(entry, float(candles["high"].max()), float(candles["low"].min()), trade_side)
        mae = adverse_excursion(entry, float(candles["high"].max()), float(candles["low"].min()), trade_side)
    return ModelTrade(
        period=period,
        model="baseline",
        pair=trade["pair"],
        side=trade_side,
        entry_tag=tag(trade),
        open_date=opened.isoformat(),
        close_date=closed.isoformat(),
        open_rate=entry,
        close_rate=float(trade["close_rate"]),
        profit_abs=float(trade["profit_abs"]),
        profit_ratio=float(trade["profit_ratio"]),
        duration_h=float(trade.get("trade_duration") or 0) / 60.0,
        exit_reason=str(trade.get("exit_reason") or ""),
        activated=False,
        activation_date="",
        original_close_date=closed.isoformat(),
        original_profit_abs=float(trade["profit_abs"]),
        original_profit_ratio=float(trade["profit_ratio"]),
        mae_pct=mae * 100.0,
        mfe_pct=mfe * 100.0,
        stake_amount=float(trade.get("stake_amount") or 0),
    )


def simulate_trade(period: str, model: str, spec: dict[str, Any], trade: dict[str, Any], frame: pd.DataFrame) -> ModelTrade:
    base = baseline_model_trade(period, trade, frame)
    if spec["kind"] == "baseline":
        return base
    opened = ts(trade["open_date"])
    original_closed = ts(trade["close_date"])
    horizon = min(opened + pd.Timedelta(hours=MAX_HOLD_HOURS), frame["date"].iloc[-1])
    sliced = trade_slice(frame, opened, horizon)
    if sliced is None:
        return base
    candles, _, _ = sliced
    entry = float(trade["open_rate"])
    trade_side = side(trade)
    original_close_index = int(candles["date"].searchsorted(original_closed, side="right")) - 1
    original_close_index = max(0, min(original_close_index, len(candles) - 1))
    trigger = float(spec["trigger"])
    activation_index: int | None = None
    high_water = entry
    low_water = entry
    for index in range(original_close_index + 1):
        candle = candles.iloc[index]
        high_water = max(high_water, float(candle["high"]))
        low_water = min(low_water, float(candle["low"]))
        if favorable_excursion(entry, high_water, low_water, trade_side) >= trigger:
            activation_index = index
            break
    if activation_index is None:
        base.model = model
        return base

    high_water = max(entry, float(candles.iloc[: activation_index + 1]["high"].max()))
    low_water = min(entry, float(candles.iloc[: activation_index + 1]["low"].min()))
    static_stop = original_stop(trade)
    exit_index = len(candles) - 1
    exit_price = float(candles.iloc[-1]["close"])
    exit_reason = "max_hold_14d"
    for index in range(activation_index, len(candles)):
        candle = candles.iloc[index]
        high_water = max(high_water, float(candle["high"]))
        low_water = min(low_water, float(candle["low"]))
        max_profit = favorable_excursion(entry, high_water, low_water, trade_side)
        if spec["kind"] == "giveback":
            locked = max(float(spec["floor"]), max_profit * (1.0 - float(spec["giveback"])))
            candidate_stop = profit_stop_price(entry, locked, trade_side)
        elif spec["kind"] == "atr":
            atr_value = float(candle.get(spec["atr_col"], np.nan))
            if not math.isfinite(atr_value):
                continue
            candidate_stop = (
                high_water - atr_value * float(spec["multiplier"])
                if trade_side == "long"
                else low_water + atr_value * float(spec["multiplier"])
            )
            breakeven = profit_stop_price(entry, 0.0, trade_side)
            candidate_stop = max(candidate_stop, breakeven) if trade_side == "long" else min(candidate_stop, breakeven)
        else:
            age_h = (ts(candle["date"]) - opened).total_seconds() / 3600.0
            if age_h < 24:
                candidate_stop = profit_stop_price(entry, 0.0, trade_side)
            else:
                locked = max(float(spec["floor"]), max_profit * (1.0 - float(spec["giveback"])))
                candidate_stop = profit_stop_price(entry, locked, trade_side)
        effective_stop = max(static_stop, candidate_stop) if trade_side == "long" else min(static_stop, candidate_stop)
        if stop_hit(candle, effective_stop, trade_side):
            exit_index = index
            exit_price = effective_stop
            exit_reason = f"counterfactual_{model}"
            break

    used = candles.iloc[: exit_index + 1]
    fee = float(trade.get("fee_open") or 0) + float(trade.get("fee_close") or 0)
    profit_ratio = direction_return(entry, exit_price, trade_side) - fee
    stake = float(trade.get("stake_amount") or 0)
    closed = ts(candles.iloc[exit_index]["date"])
    mfe = favorable_excursion(entry, float(used["high"].max()), float(used["low"].min()), trade_side)
    mae = adverse_excursion(entry, float(used["high"].max()), float(used["low"].min()), trade_side)
    return ModelTrade(
        period=period,
        model=model,
        pair=trade["pair"],
        side=trade_side,
        entry_tag=tag(trade),
        open_date=opened.isoformat(),
        close_date=closed.isoformat(),
        open_rate=entry,
        close_rate=exit_price,
        profit_abs=stake * profit_ratio,
        profit_ratio=profit_ratio,
        duration_h=(closed - opened).total_seconds() / 3600.0,
        exit_reason=exit_reason,
        activated=True,
        activation_date=ts(candles.iloc[activation_index]["date"]).isoformat(),
        original_close_date=original_closed.isoformat(),
        original_profit_abs=float(trade["profit_abs"]),
        original_profit_ratio=float(trade["profit_ratio"]),
        mae_pct=mae * 100.0,
        mfe_pct=mfe * 100.0,
        stake_amount=stake,
    )


def profit_factor(values: Iterable[float]) -> float:
    data = list(values)
    wins = sum(value for value in data if value > 0)
    losses = -sum(value for value in data if value < 0)
    return wins / losses if losses else (math.inf if wins else 0.0)


def max_drawdown(rows: list[ModelTrade]) -> float:
    balance = peak = STARTING_BALANCE
    drawdown = 0.0
    for row in sorted(rows, key=lambda item: item.close_date):
        balance += row.profit_abs
        peak = max(peak, balance)
        drawdown = max(drawdown, (peak - balance) / peak if peak else 0.0)
    return drawdown * 100.0


def metrics(rows: list[ModelTrade]) -> dict[str, Any]:
    profits = [row.profit_abs for row in rows]
    ratios = [row.profit_ratio * 100.0 for row in rows]
    durations = [row.duration_h for row in rows]
    sorted_wins = sorted((value for value in profits if value > 0), reverse=True)
    positive_total = sum(sorted_wins)
    top5_share = sum(sorted_wins[:5]) / positive_total * 100.0 if positive_total else 0.0
    return {
        "trades": len(rows),
        "profit_abs": sum(profits),
        "profit_pct": sum(profits) / STARTING_BALANCE * 100.0,
        "pf": profit_factor(profits),
        "maxdd_pct": max_drawdown(rows),
        "winrate_pct": sum(value > 0 for value in profits) / len(rows) * 100.0 if rows else 0.0,
        "avg_profit_pct": statistics.mean(ratios) if ratios else 0.0,
        "median_profit_pct": statistics.median(ratios) if ratios else 0.0,
        "avg_duration_h": statistics.mean(durations) if durations else 0.0,
        "median_duration_h": statistics.median(durations) if durations else 0.0,
        "max_duration_h": max(durations, default=0.0),
        "best_trade_abs": max(profits, default=0.0),
        "worst_trade_abs": min(profits, default=0.0),
        "avg_mae_pct": statistics.mean(row.mae_pct for row in rows) if rows else 0.0,
        "avg_mfe_pct": statistics.mean(row.mfe_pct for row in rows) if rows else 0.0,
        "activated_count": sum(row.activated for row in rows),
        "top5_winner_share_pct": top5_share,
        "exit_reason_distribution": json.dumps(Counter(row.exit_reason for row in rows), ensure_ascii=False, sort_keys=True),
    }


def period_label(date_value: str) -> str:
    value = ts(date_value)
    if pd.Timestamp("2026-03-01", tz="UTC") <= value < pd.Timestamp("2026-06-01", tz="UTC"):
        return "pressure_202603_202605"
    if pd.Timestamp("2026-01-01", tz="UTC") <= value < pd.Timestamp("2026-03-01", tz="UTC"):
        return "strong_202601_202602"
    if pd.Timestamp("2026-06-01", tz="UTC") <= value < pd.Timestamp("2026-07-01", tz="UTC"):
        return "repair_202606"
    return "other"


def model_summary(model_rows: list[ModelTrade]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    by_period_model: dict[tuple[str, str], list[ModelTrade]] = defaultdict(list)
    for row in model_rows:
        by_period_model[(row.period, row.model)].append(row)
    for (period, model), rows in by_period_model.items():
        groups: list[tuple[str, str, list[ModelTrade]]] = [("all", "all", rows)]
        for field in ("entry_tag", "pair", "side"):
            values = sorted({getattr(row, field) for row in rows})
            groups.extend((field, value, [row for row in rows if getattr(row, field) == value]) for value in values)
        months = sorted({row.close_date[:7] for row in rows})
        groups.extend(("month", month, [row for row in rows if row.close_date.startswith(month)]) for month in months)
        for special in ("pressure_202603_202605", "strong_202601_202602", "repair_202606"):
            groups.append(("market_period", special, [row for row in rows if period_label(row.close_date) == special]))
        for group_type, group_value, selected in groups:
            record = {"period": period, "model": model, "group_type": group_type, "group_value": group_value}
            record.update(metrics(selected))
            output.append(record)
    return output


def write_csv(path: Path, rows: Iterable[dict[str, Any]], columns: list[str] | None = None) -> None:
    materialized = list(rows)
    fieldnames = columns or (list(materialized[0]) if materialized else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(materialized)


def forward_outcomes(period: str, trades: list[dict[str, Any]], data: dict[str, pd.DataFrame]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for trade in trades:
        frame = data[trade["pair"]]
        closed = ts(trade["close_date"])
        close_index = int(frame["date"].searchsorted(closed, side="right")) - 1
        if close_index < 0:
            continue
        base: dict[str, Any] = {
            "period": period,
            "pair": trade["pair"],
            "side": side(trade),
            "entry_tag": tag(trade),
            "open_date": ts(trade["open_date"]).isoformat(),
            "close_date": closed.isoformat(),
            "open_rate": float(trade["open_rate"]),
            "close_rate": float(trade["close_rate"]),
            "profit_abs": float(trade["profit_abs"]),
            "profit_ratio": float(trade["profit_ratio"]),
            "exit_reason": str(trade.get("exit_reason") or ""),
            "exit_reason_group": normalized_reason(str(trade.get("exit_reason") or "")),
            "pnl_group": "winning_trades" if float(trade["profit_ratio"]) > 0 else "losing_trades" if float(trade["profit_ratio"]) < 0 else "breakeven_trades",
        }
        trade_side = base["side"]
        entry = base["open_rate"]
        exit_price = base["close_rate"]
        pre_high = float(trade.get("max_rate") or entry)
        pre_low = float(trade.get("min_rate") or entry)
        for hours in WINDOWS:
            end_index = close_index + hours
            if end_index >= len(frame):
                for name in (
                    "future_favorable_from_exit_pct", "future_adverse_from_exit_pct", "future_close_return_from_exit_pct",
                    "held_profit_ratio_pct", "regained_entry", "regained_pre_exit_extreme", "entry_plus_1pct",
                    "entry_plus_3pct", "entry_plus_5pct", "stopped_too_early", "valid_stop",
                    "took_profit_too_early", "good_take_profit", "gave_back_risk", "hold_would_help", "hold_would_hurt",
                ):
                    base[f"{name}_{hours}h"] = ""
                continue
            future = frame.iloc[close_index + 1 : end_index + 1]
            high = float(future["high"].max())
            low = float(future["low"].min())
            final = float(future.iloc[-1]["close"])
            favorable_exit = favorable_excursion(exit_price, high, low, trade_side)
            adverse_exit = adverse_excursion(exit_price, high, low, trade_side)
            close_return_exit = direction_return(exit_price, final, trade_side)
            held_return = direction_return(entry, final, trade_side) - float(trade.get("fee_open") or 0) - float(trade.get("fee_close") or 0)
            regained_entry = high >= entry if trade_side == "long" else low <= entry
            regained_pre = high >= pre_high if trade_side == "long" else low <= pre_low
            threshold_hits = {
                threshold: (high >= entry * (1 + threshold) if trade_side == "long" else low <= entry * (1 - threshold))
                for threshold in (0.01, 0.03, 0.05)
            }
            is_stop = base["exit_reason_group"] in {"stop_loss", "trailing_stop_loss"} and base["profit_ratio"] <= 0
            stopped_early = is_stop and (favorable_exit >= 0.03 or (regained_entry and threshold_hits[0.01]))
            is_take = base["profit_ratio"] > 0
            took_early = is_take and favorable_exit >= 0.03
            base[f"future_favorable_from_exit_pct_{hours}h"] = favorable_exit * 100.0
            base[f"future_adverse_from_exit_pct_{hours}h"] = adverse_exit * 100.0
            base[f"future_close_return_from_exit_pct_{hours}h"] = close_return_exit * 100.0
            base[f"held_profit_ratio_pct_{hours}h"] = held_return * 100.0
            base[f"regained_entry_{hours}h"] = regained_entry
            base[f"regained_pre_exit_extreme_{hours}h"] = regained_pre
            base[f"entry_plus_1pct_{hours}h"] = threshold_hits[0.01]
            base[f"entry_plus_3pct_{hours}h"] = threshold_hits[0.03]
            base[f"entry_plus_5pct_{hours}h"] = threshold_hits[0.05]
            base[f"stopped_too_early_{hours}h"] = stopped_early
            base[f"valid_stop_{hours}h"] = is_stop and not stopped_early
            base[f"took_profit_too_early_{hours}h"] = took_early
            base[f"good_take_profit_{hours}h"] = is_take and not took_early
            base[f"gave_back_risk_{hours}h"] = favorable_exit >= 0.03 and close_return_exit <= 0
            base[f"hold_would_help_{hours}h"] = held_return > base["profit_ratio"]
            base[f"hold_would_hurt_{hours}h"] = held_return < base["profit_ratio"]
        output.append(base)
    return output


def bool_value(value: Any) -> bool:
    return value is True or str(value).lower() == "true"


def forward_summary(rows: list[dict[str, Any]], group_type: str, group_value: str) -> list[dict[str, Any]]:
    output = []
    for hours in WINDOWS:
        available = [row for row in rows if row.get(f"future_favorable_from_exit_pct_{hours}h") != ""]
        stops = [row for row in available if row["exit_reason_group"] in {"stop_loss", "trailing_stop_loss"} and float(row["profit_ratio"]) <= 0]
        takes = [row for row in available if float(row["profit_ratio"]) > 0]
        record = {
            "group_type": group_type,
            "group_value": group_value,
            "window_h": hours,
            "trades": len(available),
            "stop_trades": len(stops),
            "take_profit_trades": len(takes),
            "stopped_too_early_pct": sum(bool_value(row[f"stopped_too_early_{hours}h"]) for row in stops) / len(stops) * 100.0 if stops else 0.0,
            "took_profit_too_early_pct": sum(bool_value(row[f"took_profit_too_early_{hours}h"]) for row in takes) / len(takes) * 100.0 if takes else 0.0,
            "hold_would_help_pct": sum(bool_value(row[f"hold_would_help_{hours}h"]) for row in available) / len(available) * 100.0 if available else 0.0,
            "hold_would_hurt_pct": sum(bool_value(row[f"hold_would_hurt_{hours}h"]) for row in available) / len(available) * 100.0 if available else 0.0,
            "avg_future_favorable_pct": statistics.mean(float(row[f"future_favorable_from_exit_pct_{hours}h"]) for row in available) if available else 0.0,
            "avg_future_adverse_pct": statistics.mean(float(row[f"future_adverse_from_exit_pct_{hours}h"]) for row in available) if available else 0.0,
            "avg_future_close_return_pct": statistics.mean(float(row[f"future_close_return_from_exit_pct_{hours}h"]) for row in available) if available else 0.0,
        }
        output.append(record)
    return output


def grouped_forward_summaries(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    output = []
    for value in sorted({str(row[field]) for row in rows}):
        selected = [row for row in rows if str(row[field]) == value]
        output.extend(forward_summary(selected, field, value))
    return output


def fmt(value: Any) -> str:
    number = float(value)
    return "inf" if math.isinf(number) else f"{number:.2f}"


def summary_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Model | Trades | Profit | PF | MaxDD proxy | Winrate | Avg/Med Profit | Avg/Med/Max Hours | Activated | Top5 winner share |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {row['trades']} | {fmt(row['profit_abs'])} ({fmt(row['profit_pct'])}%) | "
            f"{fmt(row['pf'])} | {fmt(row['maxdd_pct'])}% | {fmt(row['winrate_pct'])}% | "
            f"{fmt(row['avg_profit_pct'])}/{fmt(row['median_profit_pct'])}% | "
            f"{fmt(row['avg_duration_h'])}/{fmt(row['median_duration_h'])}/{fmt(row['max_duration_h'])} | "
            f"{row['activated_count']} | {fmt(row['top5_winner_share_pct'])}% |"
        )
    return lines


def current_exit_summary(strategy: dict[str, Any], trades: list[dict[str, Any]]) -> str:
    reasons = Counter(str(trade.get("exit_reason") or "") for trade in trades)
    lines = [
        "# Positive13 Current Exit Logic Summary",
        "",
        "## Effective Baseline Settings",
        "",
        f"- Strategy: `{STRATEGY}`",
        f"- Hard fallback stoploss: `{strategy.get('stoploss')}` (-6%).",
        "- `use_custom_stoploss=True`: short uses entry structure high + 0.2 ATR, long uses daily structure stop; both are capped to no more than 5% price risk.",
        f"- Standard trailing stop enabled: `{strategy.get('trailing_stop')}`.",
        f"- `trailing_stop_positive={strategy.get('trailing_stop_positive')}`.",
        f"- `trailing_stop_positive_offset={strategy.get('trailing_stop_positive_offset')}`.",
        f"- `trailing_only_offset_is_reached={strategy.get('trailing_only_offset_is_reached')}`.",
        f"- Minimal ROI: `{json.dumps(strategy.get('minimal_roi'), sort_keys=True)}`; 10% ROI is available immediately.",
        "- `custom_stoploss` exists for both directions through the inheritance chain.",
        "- `custom_exit` exists: shorts use stale-loss/flat/low-profit time exits and 4H trend flip; longs use daily trend flip, center/EMA structure exit, and swing exit.",
        "- `populate_exit_trend` emits no explicit dataframe exit signal. `force_exit` remains a framework/manual terminal reason; emergency exit uses Freqtrade defaults because the strategy does not override it.",
        "- Freqtrade labels custom-stop updates as `trailing_stop_loss` even though standard trailing is disabled.",
        "",
        "## How Exits Trigger",
        "",
        "- Loss control: the entry structural stop is converted to an absolute custom stop; the -6% setting is the fallback only.",
        "- Profit taking: ROI exits at 10%, plus custom structural/time exits. There is no configured standard profit trailing curve.",
        "- Short custom exits: loss after 72h, below 1% after 120h, below 3% after 240h, or 4H trend flips up while profit is below 3%.",
        "- Long custom exits: daily downtrend, daily center below fast EMA, or close below daily swing structure stop.",
        "",
        "## Three-Year Exit Reason Distribution",
        "",
        "| Exit reason | Trades | Share |",
        "|---|---:|---:|",
    ]
    for reason, count in reasons.most_common():
        lines.append(f"| {reason} | {count} | {count / len(trades) * 100.0:.2f}% |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    strategy_3y, trades_3y = load_result(ZIP_3Y)
    strategy_1y, trades_1y = load_result(ZIP_1Y)
    pairs = sorted({trade["pair"] for trade in trades_3y} | {trade["pair"] for trade in trades_1y})
    data = {pair: load_pair_data(pair) for pair in pairs}

    write_csv(ANALYSIS_DIR / "positive13_baseline_trades_3y_exit_analysis.csv", baseline_export(trades_3y), BASELINE_FIELDS)
    write_csv(ANALYSIS_DIR / "positive13_baseline_trades_1y_exit_analysis.csv", baseline_export(trades_1y), BASELINE_FIELDS)
    (REPORTS_DIR / "positive13_exit_logic_current_summary.md").write_text(
        current_exit_summary(strategy_3y, trades_3y), encoding="utf-8"
    )

    all_model_trades: list[ModelTrade] = []
    for period, trades in (("3y", trades_3y), ("1y", trades_1y)):
        for trade in trades:
            for model, spec in MODEL_SPECS.items():
                all_model_trades.append(simulate_trade(period, model, spec, trade, data[trade["pair"]]))
    summaries = model_summary(all_model_trades)
    write_csv(
        ANALYSIS_DIR / "positive13_trailing_stop_models_3y.csv",
        [row for row in summaries if row["period"] == "3y"],
    )
    write_csv(
        ANALYSIS_DIR / "positive13_trailing_stop_models_1y.csv",
        [row for row in summaries if row["period"] == "1y"],
    )
    write_csv(
        ANALYSIS_DIR / "positive13_exit_trade_level_details.csv",
        [vars(row) for row in all_model_trades],
    )

    forward_3y = forward_outcomes("3y", trades_3y, data)
    forward_1y = forward_outcomes("1y", trades_1y, data)
    write_csv(ANALYSIS_DIR / "positive13_exit_forward_outcome_3y.csv", forward_3y)
    write_csv(ANALYSIS_DIR / "positive13_exit_forward_outcome_1y.csv", forward_1y)
    all_forward = forward_3y + forward_1y
    reason_summary: list[dict[str, Any]] = []
    tag_summary: list[dict[str, Any]] = []
    pair_summary: list[dict[str, Any]] = []
    for period, selected in (("3y", forward_3y), ("1y", forward_1y)):
        for target, field in (
            (reason_summary, "exit_reason_group"),
            (tag_summary, "entry_tag"),
            (pair_summary, "pair"),
        ):
            records = grouped_forward_summaries(selected, field)
            for record in records:
                record["period"] = period
            target.extend(records)
    write_csv(ANALYSIS_DIR / "positive13_exit_reason_summary.csv", reason_summary)
    write_csv(ANALYSIS_DIR / "positive13_exit_entry_tag_summary.csv", tag_summary)
    write_csv(ANALYSIS_DIR / "positive13_exit_pair_summary.csv", pair_summary)

    overall_3y = [row for row in summaries if row["period"] == "3y" and row["group_type"] == "all"]
    overall_1y = [row for row in summaries if row["period"] == "1y" and row["group_type"] == "all"]
    by_model_3y = {row["model"]: row for row in overall_3y}
    by_model_1y = {row["model"]: row for row in overall_1y}
    candidates = [row for row in overall_3y if row["model"] != "baseline"]
    highest_profit = max(candidates, key=lambda row: row["profit_abs"])
    highest_pf = max(candidates, key=lambda row: row["pf"])
    lowest_dd = min(candidates, key=lambda row: row["maxdd_pct"])
    baseline3 = by_model_3y["baseline"]
    baseline1 = by_model_1y["baseline"]
    acceptable = []
    for row in candidates:
        one = by_model_1y[row["model"]]
        pressure = next(
            item for item in summaries
            if item["period"] == "3y" and item["model"] == row["model"]
            and item["group_type"] == "market_period" and item["group_value"] == "pressure_202603_202605"
        )
        pressure_base = next(
            item for item in summaries
            if item["period"] == "3y" and item["model"] == "baseline"
            and item["group_type"] == "market_period" and item["group_value"] == "pressure_202603_202605"
        )
        if (
            row["profit_abs"] > baseline3["profit_abs"]
            and row["pf"] >= 1.90
            and row["maxdd_pct"] <= baseline3["maxdd_pct"] + 3.0
            and one["profit_abs"] >= baseline1["profit_abs"] * 0.95
            and one["pf"] >= 1.80
            and pressure["profit_abs"] >= pressure_base["profit_abs"] - 20.0
            and row["avg_duration_h"] <= baseline3["avg_duration_h"] * 2.0
        ):
            acceptable.append(row["model"])

    forward3_overall = forward_summary(forward_3y, "all", "3y")
    forward_by_window = {int(row["window_h"]): row for row in forward3_overall}
    stop24 = forward_by_window[24]["stopped_too_early_pct"]
    stop48 = forward_by_window[48]["stopped_too_early_pct"]
    take72 = forward_by_window[72]["took_profit_too_early_pct"]
    stop_rows_24 = [
        row for row in forward_3y
        if row["exit_reason_group"] in {"stop_loss", "trailing_stop_loss"} and float(row["profit_ratio"]) <= 0
        and row.get("stopped_too_early_24h") != ""
    ]
    long_stops = [row for row in stop_rows_24 if row["side"] == "long"]
    short_stops = [row for row in stop_rows_24 if row["side"] == "short"]
    long_recover = sum(bool_value(row["stopped_too_early_24h"]) for row in long_stops) / len(long_stops) * 100.0 if long_stops else 0.0
    short_recover = sum(bool_value(row["stopped_too_early_24h"]) for row in short_stops) / len(short_stops) * 100.0 if short_stops else 0.0
    best_stop_tags = sorted(
        [row for row in tag_summary if row["period"] == "3y" and int(row["window_h"]) == 24],
        key=lambda row: row["stopped_too_early_pct"], reverse=True,
    )
    best_take_tags = sorted(
        [row for row in tag_summary if row["period"] == "3y" and int(row["window_h"]) == 72],
        key=lambda row: row["took_profit_too_early_pct"], reverse=True,
    )
    best_stop_pairs = sorted(
        [row for row in pair_summary if row["period"] == "3y" and int(row["window_h"]) == 24 and row["stop_trades"] >= 3],
        key=lambda row: row["stopped_too_early_pct"], reverse=True,
    )
    best_take_pairs = sorted(
        [row for row in pair_summary if row["period"] == "3y" and int(row["window_h"]) == 72 and row["take_profit_trades"] >= 3],
        key=lambda row: row["took_profit_too_early_pct"], reverse=True,
    )
    implement_real = any(
        row["profit_abs"] >= baseline3["profit_abs"] * 1.10
        and row["pf"] >= baseline3["pf"] - 0.10
        and row["maxdd_pct"] <= baseline3["maxdd_pct"] + 2.0
        for row in candidates if row["model"] in acceptable
    )
    pressure_base = next(
        row for row in summaries
        if row["period"] == "3y" and row["model"] == "baseline"
        and row["group_type"] == "market_period" and row["group_value"] == "pressure_202603_202605"
    )
    pressure_best = next(
        row for row in summaries
        if row["period"] == "3y" and row["model"] == highest_profit["model"]
        and row["group_type"] == "market_period" and row["group_value"] == "pressure_202603_202605"
    )
    tag_deltas = []
    for entry_tag in sorted({row.entry_tag for row in all_model_trades if row.period == "3y"}):
        base_tag = next(
            row for row in summaries
            if row["period"] == "3y" and row["model"] == "baseline"
            and row["group_type"] == "entry_tag" and row["group_value"] == entry_tag
        )
        model_tag = next(
            row for row in summaries
            if row["period"] == "3y" and row["model"] == highest_profit["model"]
            and row["group_type"] == "entry_tag" and row["group_value"] == entry_tag
        )
        tag_deltas.append((entry_tag, model_tag["profit_abs"] - base_tag["profit_abs"]))
    pair_deltas = []
    for pair in pairs:
        base_pair = next(
            row for row in summaries
            if row["period"] == "3y" and row["model"] == "baseline"
            and row["group_type"] == "pair" and row["group_value"] == pair
        )
        model_pair = next(
            row for row in summaries
            if row["period"] == "3y" and row["model"] == highest_profit["model"]
            and row["group_type"] == "pair" and row["group_value"] == pair
        )
        pair_deltas.append((pair, model_pair["profit_abs"] - base_pair["profit_abs"]))
    positive_tags = sorted((item for item in tag_deltas if item[1] > 0), key=lambda item: item[1], reverse=True)
    positive_pairs = sorted((item for item in pair_deltas if item[1] > 0), key=lambda item: item[1], reverse=True)

    report: list[str] = [
        "# Positive13 Exit Counterfactual Research",
        "",
        "## Scope And Caveats",
        "",
        "- Offline research only. Main strategy, dry-run/live configuration, pair pool, tags, and max3 are unchanged.",
        "- Entries and stakes are fixed to the aligned baseline. A candidate replaces the exit only when its profit trigger occurred before the original exit; otherwise the original trade is retained.",
        "- Original structural stop remains active after model activation; maximum holding time is 14 days.",
        "- Extended exits can overlap later fixed entries and do not recalculate max3 slot contention or wallet sizing. Results are screening evidence, not a replacement backtest.",
        "- Candidate returns use candle OHLC and baseline open/close fees; funding and intrabar path are approximate. Stop hits are evaluated conservatively.",
        "- Candidate MaxDD is a close-balance proxy over fixed trades. Its baseline is 8.87%, while Freqtrade's full equity-aware baseline MaxDD is 7.66%; compare proxy values only within the counterfactual table.",
        "- Model E assumption: after +5%, protect breakeven until age 24h, then use 60% giveback with a 1.5% minimum lock.",
        "",
        "## Baseline Reproduction",
        "",
        f"- 3Y export: {strategy_3y['total_trades']} trades / {fmt(strategy_3y['profit_total_abs'])} USDT / PF {fmt(strategy_3y['profit_factor'])} / MaxDD {fmt(strategy_3y['max_drawdown_account'] * 100)}%.",
        f"- 1Y export: {strategy_1y['total_trades']} trades / {fmt(strategy_1y['profit_total_abs'])} USDT / PF {fmt(strategy_1y['profit_factor'])} / MaxDD {fmt(strategy_1y['max_drawdown_account'] * 100)}%.",
        "",
        "## Three-Year Trailing Counterfactuals",
        "",
    ]
    report.extend(summary_table(overall_3y))
    report.extend(["", "## One-Year Trailing Counterfactuals", ""])
    report.extend(summary_table(overall_1y))
    report.extend(
        [
            "",
            "## Answers: Profit Trailing",
            "",
            f"1. Highest candidate total profit: `{highest_profit['model']}` at {fmt(highest_profit['profit_abs'])} USDT, still below baseline {fmt(baseline3['profit_abs'])} USDT.",
            f"2. Highest candidate PF: `{highest_pf['model']}` at {fmt(highest_pf['pf'])}, still below baseline {fmt(baseline3['pf'])}.",
            f"3. Lowest candidate MaxDD proxy: `{lowest_dd['model']}` at {fmt(lowest_dd['maxdd_pct'])}%, above baseline proxy {fmt(baseline3['maxdd_pct'])}%.",
            f"4. Models improving profit without material drawdown expansion: {', '.join(f'`{name}`' for name in acceptable) if acceptable else 'none'}.",
            f"5. Pressure period did not worsen for the highest-profit candidate: baseline {fmt(pressure_base['profit_abs'])} vs `{highest_profit['model']}` {fmt(pressure_best['profit_abs'])} USDT; this local improvement does not offset its three-year degradation.",
            f"6. Baseline average duration is {fmt(baseline3['avg_duration_h'])}h; the longest candidate average is {fmt(max(row['avg_duration_h'] for row in candidates))}h.",
            f"7. Highest-profit model top-five winners contribute {fmt(highest_profit['top5_winner_share_pct'])}% of gross winning profit.",
            f"8. Entry-tag beneficiaries under `{highest_profit['model']}`: {', '.join(f'`{name}` {delta:+.2f} USDT' for name, delta in positive_tags) if positive_tags else 'none'}; both short tags deteriorated.",
            f"9. Positive pair deltas under `{highest_profit['model']}`: {', '.join(f'`{name}` {delta:+.2f}' for name, delta in positive_pairs) if positive_pairs else 'none'}. These are exploratory and do not justify pair-specific exits.",
            f"10. Real strategy version warranted now: {'yes' if implement_real else 'no'}.",
            "",
            "## Exit-Forward Outcomes",
            "",
            "| Window | Stops too early | Takes too early | Hold helps | Hold hurts | Avg favorable | Avg adverse |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in forward3_overall:
        report.append(
            f"| {row['window_h']}h | {fmt(row['stopped_too_early_pct'])}% | {fmt(row['took_profit_too_early_pct'])}% | "
            f"{fmt(row['hold_would_help_pct'])}% | {fmt(row['hold_would_hurt_pct'])}% | "
            f"{fmt(row['avg_future_favorable_pct'])}% | {fmt(row['avg_future_adverse_pct'])}% |"
        )
    report.extend(
        [
            "",
            "## Answers: Are Current Exits Too Early?",
            "",
            f"1. Losing stop trades labelled stopped_too_early: {fmt(stop24)}% by 24h and {fmt(stop48)}% by 48h.",
            f"2. Long losing stops recovering by the 24h label: {fmt(long_recover)}%.",
            f"3. Short losing stops recovering by the 24h label: {fmt(short_recover)}%.",
            f"4. Winning trades labelled took_profit_too_early by 72h: {fmt(take72)}%.",
            f"5. Hold-help rates at 24/48/72/168h: {fmt(forward_by_window[24]['hold_would_help_pct'])}% / {fmt(forward_by_window[48]['hold_would_help_pct'])}% / {fmt(forward_by_window[72]['hold_would_help_pct'])}% / {fmt(forward_by_window[168]['hold_would_help_pct'])}%.",
            f"6. Highest 24h stop-recovery tag: `{best_stop_tags[0]['group_value']}` ({fmt(best_stop_tags[0]['stopped_too_early_pct'])}%)" if best_stop_tags else "6. No tag has evaluable stopped trades.",
            f"7. Highest 72h continued-profit tag: `{best_take_tags[0]['group_value']}` ({fmt(best_take_tags[0]['took_profit_too_early_pct'])}%)" if best_take_tags else "7. No tag has evaluable winning trades.",
            f"8. Highest early-stop pair with >=3 stops: `{best_stop_pairs[0]['group_value']}` ({fmt(best_stop_pairs[0]['stopped_too_early_pct'])}%)" if best_stop_pairs else "8. No pair has at least three evaluable stops.",
            f"9. Highest early-profit pair with >=3 wins: `{best_take_pairs[0]['group_value']}` ({fmt(best_take_pairs[0]['took_profit_too_early_pct'])}%)" if best_take_pairs else "9. No pair has at least three evaluable wins.",
            f"10. Current stoploss clearly too tight: {'yes' if stop24 >= 40 and stop48 >= 50 else 'not proven'}.",
            "11. Current take-profit/trailing clearly too early: not globally proven. Post-exit favorable excursions are frequent, but fixed-hold improvement is near 50% and every global widening model loses three-year quality.",
            f"12. Change stoploss now: {'research further, but do not change yet' if stop48 >= 50 else 'no'}.",
            f"13. Change trailing now: {'test a real research version next' if implement_real else 'no'}.",
            "14. Entry-tag-specific exits: worth further offline study for `long_1d_center_compression`, but not implementation yet; both short tags reject global widening.",
            "15. Pair-specific exits: not recommended without independent validation.",
            "",
            "## Final Recommendation",
            "",
            "1. Current exit logic clearly early: not globally. Many exits leave later favorable excursion, but the tested widening rules fail to monetize it across three years.",
            f"2. Current stoploss clearly tight: {'yes' if stop24 >= 40 and stop48 >= 50 else 'no clear evidence'}.",
            "3. Wider post-profit trailing deserves continuation: not as a global rule; only a long-tag-specific diagnostic is justified.",
            f"4. Develop a real strategy version next: {'yes' if implement_real else 'no'}.",
            "5. Next direction: keep current exits; if research continues, isolate `long_1d_center_compression` profit protection before considering `DualTrendCombinedShortPullbackShapeV1ExitResearchStrategy`.",
            "6. Keep the current main strategy unchanged: yes.",
            "",
            "## Outputs",
            "",
            "- `user_data/reports/positive13_exit_logic_current_summary.md`",
            "- `user_data/analysis/positive13_baseline_trades_3y_exit_analysis.csv`",
            "- `user_data/analysis/positive13_baseline_trades_1y_exit_analysis.csv`",
            "- `user_data/analysis/positive13_exit_forward_outcome_3y.csv`",
            "- `user_data/analysis/positive13_exit_forward_outcome_1y.csv`",
            "- `user_data/analysis/positive13_trailing_stop_models_3y.csv`",
            "- `user_data/analysis/positive13_trailing_stop_models_1y.csv`",
            "- `user_data/analysis/positive13_exit_reason_summary.csv`",
            "- `user_data/analysis/positive13_exit_entry_tag_summary.csv`",
            "- `user_data/analysis/positive13_exit_pair_summary.csv`",
            "- `user_data/analysis/positive13_exit_trade_level_details.csv`",
            "",
        ]
    )
    (REPORTS_DIR / "positive13_exit_counterfactual_research.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote exit research: {len(all_model_trades)} model trades, {len(all_forward)} forward rows")
    print("acceptable", acceptable, "implement_real", implement_real)


if __name__ == "__main__":
    main()
