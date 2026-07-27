from __future__ import annotations

import argparse
import io
import json
import math
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Join max3 rejected signals to fixed-stake max100 counterfactual trades"
    )
    parser.add_argument("--constrained-zip", required=True)
    parser.add_argument("--counterfactual-zip", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--title", default="DualTrend signal collision replay")
    return parser.parse_args()


def archive_member(archive: zipfile.ZipFile, suffix: str) -> str:
    matches = [name for name in archive.namelist() if name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"Expected one *{suffix} member, found {matches}")
    return matches[0]


def strategy_payload(path: Path) -> tuple[str, dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.endswith(".json") and not n.endswith("_config.json")]
        if len(names) != 1:
            raise ValueError(f"Unable to identify result JSON in {path}")
        name = names[0]
        payload = json.loads(archive.read(name))
    strategy_name = next(iter(payload["strategy"]))
    return strategy_name, payload["strategy"][strategy_name]


def rejected_signals(path: Path) -> tuple[str, pd.DataFrame]:
    with zipfile.ZipFile(path) as archive:
        name = archive_member(archive, "_rejected.pkl")
        nested = joblib.load(io.BytesIO(archive.read(name)))
    strategy_name = next(iter(nested))
    frames = []
    for pair, frame in nested[strategy_name].items():
        if frame.empty:
            continue
        item = frame.copy()
        item["pair"] = pair
        frames.append(item)
    if not frames:
        return strategy_name, pd.DataFrame(columns=["date", "pair", "enter_tag"])
    result = pd.concat(frames, ignore_index=True)
    result["date"] = pd.to_datetime(result["date"], utc=True)
    return strategy_name, result.sort_values(["date", "pair", "enter_tag"]).reset_index(drop=True)


def trades_frame(payload: dict[str, Any]) -> pd.DataFrame:
    frame = pd.DataFrame(payload.get("trades", []))
    if frame.empty:
        return frame
    for column in ("open_date", "close_date"):
        frame[column] = pd.to_datetime(frame[column], utc=True, errors="coerce")
    return frame.sort_values(["open_date", "pair"]).reset_index(drop=True)


def occupants_at(trades: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame:
    if trades.empty:
        return trades
    return trades[
        (trades["open_date"] <= timestamp)
        & (trades["close_date"].isna() | (trades["close_date"] > timestamp))
    ]


def exact_counterfactual(
    trades: pd.DataFrame, pair: str, tag: str, timestamp: pd.Timestamp
) -> pd.Series | None:
    if trades.empty:
        return None
    matched = trades[
        trades["pair"].eq(pair)
        & trades["enter_tag"].fillna("").eq(tag)
        & trades["open_date"].eq(timestamp)
    ]
    return matched.iloc[0] if not matched.empty else None


def active_counterfactual(
    trades: pd.DataFrame, pair: str, tag: str, timestamp: pd.Timestamp
) -> pd.Series | None:
    if trades.empty:
        return None
    matched = trades[
        trades["pair"].eq(pair)
        & trades["enter_tag"].fillna("").eq(tag)
        & (trades["open_date"] < timestamp)
        & (trades["close_date"].isna() | (trades["close_date"] > timestamp))
    ]
    return matched.iloc[-1] if not matched.empty else None


def safe_number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def collision_rows(
    rejected: pd.DataFrame,
    constrained_trades: pd.DataFrame,
    counterfactual_trades: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    feature_names = (
        "close",
        "enter_initial_stop",
        "enter_risk_pct",
        "atr_pct",
        "body_pct_of_range",
        "close_position",
        "compression_width_pct",
        "pullback_depth_short",
        "pullback_depth_long_1h",
        "trend_up_4h",
        "trend_down_4h",
        "long_strong_trend_context",
    )
    for _, signal in rejected.iterrows():
        timestamp = signal["date"]
        pair = str(signal["pair"])
        tag = str(signal.get("enter_tag") or "")
        occupants = occupants_at(constrained_trades, timestamp)
        exact = exact_counterfactual(counterfactual_trades, pair, tag, timestamp)
        active = active_counterfactual(counterfactual_trades, pair, tag, timestamp)
        if exact is not None:
            status = "matched_counterfactual_entry"
            counterfactual = exact
        elif active is not None:
            status = "duplicate_signal_while_counterfactual_open"
            counterfactual = active
        else:
            status = "unresolved"
            counterfactual = None

        row: dict[str, Any] = {
            "signal_date": timestamp,
            "pair": pair,
            "side": "long" if tag.startswith("long_") else "short",
            "entry_tag": tag,
            "open_slots": len(occupants),
            "occupant_pairs": "|".join(occupants["pair"].astype(str)),
            "occupant_tags": "|".join(occupants["enter_tag"].fillna("").astype(str)),
            "match_status": status,
            "counterfactual_open_date": counterfactual.get("open_date") if counterfactual is not None else pd.NaT,
            "counterfactual_close_date": counterfactual.get("close_date") if counterfactual is not None else pd.NaT,
            "counterfactual_profit_ratio": safe_number(counterfactual.get("profit_ratio")) if counterfactual is not None else None,
            "counterfactual_exit_reason": counterfactual.get("exit_reason") if counterfactual is not None else None,
        }
        for name in feature_names:
            if name in signal:
                row[name] = signal.get(name)
        rows.append(row)
    return pd.DataFrame(rows)


def profit_factor(values: pd.Series) -> float | None:
    wins = values[values > 0].sum()
    losses = values[values < 0].sum()
    if losses == 0:
        return None
    return float(wins / abs(losses))


def fmt_pct(value: Any) -> str:
    number = safe_number(value)
    return "n/a" if number is None else f"{number * 100:+.2f}%"


def summary_rows(frame: pd.DataFrame, group_column: str) -> list[tuple[str, int, int, int, float, float | None]]:
    rows: list[tuple[str, int, int, int, float, float | None]] = []
    for key, group in frame.groupby(group_column, sort=True):
        values = pd.to_numeric(group["counterfactual_profit_ratio"], errors="coerce").dropna()
        rows.append(
            (
                str(key),
                len(values),
                int((values > 0).sum()),
                int((values < 0).sum()),
                float(values.sum()),
                profit_factor(values),
            )
        )
    return rows


def markdown_report(
    title: str,
    constrained_name: str,
    counterfactual_name: str,
    constrained_payload: dict[str, Any],
    rejected: pd.DataFrame,
    audit: pd.DataFrame,
) -> str:
    episodes = audit[audit["match_status"].eq("matched_counterfactual_entry")].copy()
    episodes["year"] = pd.to_datetime(episodes["signal_date"], utc=True).dt.year
    duplicate_count = int(audit["match_status"].eq("duplicate_signal_while_counterfactual_open").sum())
    unresolved_count = int(audit["match_status"].eq("unresolved").sum())
    profits = pd.to_numeric(episodes.get("counterfactual_profit_ratio"), errors="coerce").dropna()
    pf = profit_factor(profits)
    tag_counts = Counter(rejected.get("enter_tag", pd.Series(dtype=str)).fillna("").astype(str))
    occupancy_counts: Counter[str] = Counter()
    for tags in audit.get("occupant_tags", pd.Series(dtype=str)).fillna(""):
        occupancy_counts.update(tag for tag in tags.split("|") if tag)
    blocked_long = episodes[episodes["side"].eq("long")]
    blocked_micro = episodes[episodes["entry_tag"].eq("long_pullback_restart_1h_body")]
    micro_occupancy = audit[audit.get("occupant_tags", pd.Series(dtype=str)).fillna("").str.contains(
        "long_pullback_restart_1h_body", regex=False
    )]

    lines = [
        f"# {title}",
        "",
        f"> Generated {datetime.now(timezone.utc).isoformat()} from Freqtrade native signal exports.",
        "",
        "## Scope",
        "",
        f"- Constrained strategy: `{constrained_name}`",
        f"- Counterfactual strategy: `{counterfactual_name}`",
        f"- Constrained timerange: `{constrained_payload.get('backtest_start')} -> {constrained_payload.get('backtest_end')}`",
        f"- Constrained trades: `{len(constrained_payload.get('trades', []))}`",
        f"- Exported max-slot collision candles: `{len(rejected)}`",
        f"- Distinct counterfactual entry episodes: `{len(episodes)}`",
        f"- Repeated signals while the same counterfactual trade was open: `{duplicate_count}`",
        f"- Unresolved collision candles: `{unresolved_count}`",
        "",
        "The max100 run uses a fixed diagnostic stake and no protections. Its portfolio return is intentionally ignored; only the trade path of a rejected signal is used as a counterfactual outcome.",
        "",
        "## Counterfactual Outcome",
        "",
        f"- Wins / losses: `{int((profits > 0).sum())} / {int((profits < 0).sum())}`",
        f"- Sum of trade returns: `{fmt_pct(profits.sum()) if not profits.empty else 'n/a'}`",
        f"- Mean trade return: `{fmt_pct(profits.mean()) if not profits.empty else 'n/a'}`",
        f"- Profit factor on return ratios: `{pf:.3f}`" if pf is not None else "- Profit factor on return ratios: `n/a`",
        "",
        "## Blocked Tags",
        "",
        "| Tag | Collision candles |",
        "|---|---:|",
    ]
    lines.extend(f"| `{tag}` | {count} |" for tag, count in tag_counts.most_common())
    lines.extend(
        [
            "",
            "## Outcome By Blocked Tag",
            "",
            "| Blocked tag | Episodes | Win | Loss | Sum returns | PF |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for tag, count, wins, losses, total, tag_pf in summary_rows(episodes, "entry_tag"):
        pf_text = "n/a" if tag_pf is None else f"{tag_pf:.3f}"
        lines.append(f"| `{tag}` | {count} | {wins} | {losses} | {fmt_pct(total)} | {pf_text} |")
    lines.extend(
        [
            "",
            "## Outcome By Year",
            "",
            "| Year | Episodes | Win | Loss | Sum returns | PF |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for year, count, wins, losses, total, year_pf in summary_rows(episodes, "year"):
        pf_text = "n/a" if year_pf is None else f"{year_pf:.3f}"
        lines.append(f"| {year} | {count} | {wins} | {losses} | {fmt_pct(total)} | {pf_text} |")
    lines.extend(["", "## Slot Occupants", "", "| Occupying tag | Collision-candle appearances |", "|---|---:|"])
    lines.extend(f"| `{tag}` | {count} |" for tag, count in occupancy_counts.most_common())
    blocked_long_sum = pd.to_numeric(
        blocked_long.get("counterfactual_profit_ratio"), errors="coerce"
    ).sum()
    lines.extend(
        [
            "",
            "## Long-Side Squeeze Check",
            "",
            f"- Rejected long entry episodes: `{len(blocked_long)}`, sum returns `{fmt_pct(blocked_long_sum)}`.",
            f"- Rejected LongMicro episodes: `{len(blocked_micro)}`.",
            f"- Collision candles where LongMicro occupied a slot: `{len(micro_occupancy)}`.",
            "- A slot appearance is not evidence of harmful displacement; inspect the corresponding counterfactual outcome before changing priority.",
        ]
    )
    lines.extend(
        [
            "",
            "## Counterfactual Episodes",
            "",
            "| Signal time | Pair | Blocked tag | Outcome | Exit | Occupying tags |",
            "|---|---|---|---:|---|---|",
        ]
    )
    for _, row in episodes.iterrows():
        lines.append(
            f"| {row['signal_date']} | `{row['pair']}` | `{row['entry_tag']}` | "
            f"{fmt_pct(row['counterfactual_profit_ratio'])} | `{row['counterfactual_exit_reason']}` | "
            f"`{row['occupant_tags']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Rules",
            "",
            "- A collision candle is not automatically one missed trade; repeated same-pair signals are collapsed by the counterfactual trade path.",
            "- This audit diagnoses opportunity quality. It does not prove which open position should be replaced at collision time.",
            "- Do not promote a ranking rule from a tiny tag or yearly subset. Require stable direction across five-year, yearly, and dry-run shadow evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    constrained_path = Path(args.constrained_zip)
    counterfactual_path = Path(args.counterfactual_zip)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rejected_name, rejected = rejected_signals(constrained_path)
    constrained_name, constrained_payload = strategy_payload(constrained_path)
    counterfactual_name, counterfactual_payload = strategy_payload(counterfactual_path)
    if rejected_name != constrained_name:
        raise ValueError(f"Rejected export strategy {rejected_name} != result strategy {constrained_name}")

    constrained_trades = trades_frame(constrained_payload)
    counterfactual_trades = trades_frame(counterfactual_payload)
    audit = collision_rows(rejected, constrained_trades, counterfactual_trades)
    audit.to_csv(output_dir / "collision_signals.csv", index=False)
    report = markdown_report(
        args.title,
        constrained_name,
        counterfactual_name,
        constrained_payload,
        rejected,
        audit,
    )
    (output_dir / "collision_replay.md").write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
