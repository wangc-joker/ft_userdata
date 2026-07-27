from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd


CONTROL = "DualTrendPyramidSecondAdd20V1Strategy"
CANDIDATE = "DualTrendPyramidSecondAdd20LongMicroV1Strategy"
MICRO_TAG = "long_pullback_restart_1h_body"
STARTING_BALANCE = 1000.0
SLIPPAGE = {
    "fee2x_slip_light": 0.0003,
    "fee2x_slip_medium": 0.0005,
    "fee2x_slip_heavy": 0.0010,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize corrected LongMicro fee and post-trade slippage stress"
    )
    parser.add_argument("--baseline-zip", required=True)
    parser.add_argument("--fee1p5-zip", required=True)
    parser.add_argument("--fee2-zip", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def load_archive(path: Path) -> dict[str, dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.endswith(".json") and not name.endswith("_config.json")
        ]
        if len(names) != 1:
            raise ValueError(f"Unable to identify result JSON in {path}")
        payload = json.loads(archive.read(names[0]))
    strategies = payload.get("strategy", {})
    missing = [name for name in (CONTROL, CANDIDATE) if name not in strategies]
    if missing:
        raise ValueError(f"Missing strategies {missing} in {path}")
    return strategies


def profit_factor(profits: list[float]) -> float:
    wins = sum(value for value in profits if value > 0)
    losses = -sum(value for value in profits if value < 0)
    if losses == 0:
        return math.inf if wins > 0 else 0.0
    return wins / losses


def approximate_drawdown(trades: list[dict[str, Any]], profits: list[float]) -> float:
    ordered = sorted(
        zip(trades, profits),
        key=lambda item: int(item[0].get("close_timestamp") or item[0].get("open_timestamp") or 0),
    )
    balance = STARTING_BALANCE
    peak = STARTING_BALANCE
    maximum = 0.0
    for _, profit in ordered:
        balance += profit
        peak = max(peak, balance)
        if peak > 0:
            maximum = max(maximum, (peak - balance) / peak)
    return maximum


def adverse_slippage_profit(trade: dict[str, Any], slippage: float) -> float:
    profit_abs = float(trade["profit_abs"])
    amount = float(trade["amount"])
    open_rate = float(trade["open_rate"])
    close_rate = float(trade["close_rate"])
    if bool(trade.get("is_short")):
        original_gross = (open_rate - close_rate) * amount
        stressed_gross = (
            open_rate * (1.0 - slippage) - close_rate * (1.0 + slippage)
        ) * amount
    else:
        original_gross = (close_rate - open_rate) * amount
        stressed_gross = (
            close_rate * (1.0 - slippage) - open_rate * (1.0 + slippage)
        ) * amount
    return profit_abs + stressed_gross - original_gross


def reported_summary(
    scenario: str, strategy_name: str, payload: dict[str, Any], source_zip: Path
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "strategy": strategy_name,
        "trades": int(payload["total_trades"]),
        "profit_abs": float(payload["profit_total_abs"]),
        "profit_pct": float(payload["profit_total"]),
        "profit_factor": float(payload["profit_factor"]),
        "max_drawdown": float(payload["max_drawdown_account"]),
        "winrate": float(payload["winrate"]),
        "reported_or_static": "freqtrade_reported",
        "source_zip": source_zip.name,
    }


def slippage_summary(
    scenario: str,
    strategy_name: str,
    payload: dict[str, Any],
    source_zip: Path,
    slippage: float,
) -> dict[str, Any]:
    trades = list(payload.get("trades", []))
    profits = [adverse_slippage_profit(trade, slippage) for trade in trades]
    return {
        "scenario": scenario,
        "strategy": strategy_name,
        "trades": len(trades),
        "profit_abs": sum(profits),
        "profit_pct": sum(profits) / STARTING_BALANCE,
        "profit_factor": profit_factor(profits),
        "max_drawdown": approximate_drawdown(trades, profits),
        "winrate": sum(value > 0 for value in profits) / len(profits) if profits else 0.0,
        "reported_or_static": f"post_trade_slippage_{slippage:.4%}_per_side",
        "source_zip": source_zip.name,
    }


def micro_rows(
    scenario: str,
    payload: dict[str, Any],
    source_zip: Path,
    slippage: float | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trade in payload.get("trades", []):
        if str(trade.get("enter_tag") or "") != MICRO_TAG:
            continue
        profit_abs = (
            adverse_slippage_profit(trade, slippage)
            if slippage is not None
            else float(trade["profit_abs"])
        )
        stake = float(trade.get("stake_amount") or STARTING_BALANCE)
        rows.append(
            {
                "scenario": scenario,
                "pair": trade["pair"],
                "open_date": trade["open_date"],
                "close_date": trade["close_date"],
                "year": pd.to_datetime(trade["open_date"], utc=True).year,
                "exit_reason": trade.get("exit_reason"),
                "profit_abs": profit_abs,
                "profit_ratio": profit_abs / stake,
                "order_count": len(trade.get("orders") or []),
                "source_zip": source_zip.name,
            }
        )
    return rows


def path_comparison(
    baseline: dict[str, Any], stressed: dict[str, Any], scenario: str, strategy_name: str
) -> dict[str, Any]:
    def key(trade: dict[str, Any]) -> tuple[str, str, str]:
        return (
            str(trade["pair"]),
            str(trade["open_date"]),
            str(trade.get("enter_tag") or ""),
        )

    baseline_by_key = {key(trade): trade for trade in baseline.get("trades", [])}
    stressed_by_key = {key(trade): trade for trade in stressed.get("trades", [])}
    shared = sorted(set(baseline_by_key) & set(stressed_by_key))
    exact_paths = 0
    changed_exits = 0
    changed_orders = 0
    for trade_key in shared:
        left = baseline_by_key[trade_key]
        right = stressed_by_key[trade_key]
        same_exit = (
            left.get("close_date") == right.get("close_date")
            and left.get("exit_reason") == right.get("exit_reason")
        )
        same_orders = len(left.get("orders") or []) == len(right.get("orders") or [])
        if same_exit and same_orders:
            exact_paths += 1
        if not same_exit:
            changed_exits += 1
        if not same_orders:
            changed_orders += 1
    return {
        "scenario": scenario,
        "strategy": strategy_name,
        "baseline_trades": len(baseline_by_key),
        "stressed_trades": len(stressed_by_key),
        "matched_entries": len(shared),
        "baseline_only_entries": len(set(baseline_by_key) - set(stressed_by_key)),
        "stressed_only_entries": len(set(stressed_by_key) - set(baseline_by_key)),
        "exact_exit_and_order_paths": exact_paths,
        "changed_exits": changed_exits,
        "changed_order_counts": changed_orders,
    }


def fmt_pct(value: Any) -> str:
    return f"{float(value) * 100:+.2f}%"


def fmt_pf(value: Any) -> str:
    number = float(value)
    return "inf" if math.isinf(number) else f"{number:.3f}"


def markdown_report(
    summary: pd.DataFrame, micro: pd.DataFrame, paths: pd.DataFrame
) -> str:
    scenario_order = [
        "baseline",
        "fee1p5x",
        "fee2x",
        "fee2x_slip_light",
        "fee2x_slip_medium",
        "fee2x_slip_heavy",
    ]
    by_key = summary.set_index(["scenario", "strategy"])
    lines = [
        "# Corrected LongMicro Execution Stress",
        "",
        "## Portfolio Results",
        "",
        "| Scenario | Control profit | Candidate profit | Candidate delta | Control PF | Candidate PF | Candidate DD |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in scenario_order:
        control = by_key.loc[(scenario, CONTROL)]
        candidate = by_key.loc[(scenario, CANDIDATE)]
        lines.append(
            f"| `{scenario}` | {fmt_pct(control['profit_pct'])} | {fmt_pct(candidate['profit_pct'])} | "
            f"{fmt_pct(candidate['profit_pct'] - control['profit_pct'])} | {fmt_pf(control['profit_factor'])} | "
            f"{fmt_pf(candidate['profit_factor'])} | {fmt_pct(candidate['max_drawdown'])} |"
        )

    lines.extend(
        [
            "",
            "Freqtrade-reported rows propagate fee effects through callbacks, protections, sizing, and later occupancy. Slippage rows are static post-trade estimates from the fee2x trade lists and do not propagate those state changes.",
            "",
            "## Micro Tag",
            "",
            "| Scenario | Trades | Wins | Profit | PF |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for scenario in scenario_order:
        group = micro[micro["scenario"].eq(scenario)]
        profits = group["profit_abs"].astype(float).tolist()
        lines.append(
            f"| `{scenario}` | {len(group)} | {sum(value > 0 for value in profits)} | "
            f"{sum(profits):+.2f} USDT | {fmt_pf(profit_factor(profits))} |"
        )

    lines.extend(
        [
            "",
            "## Micro Tag By Entry Year",
            "",
            "| Scenario | Year | Trades | Profit |",
            "|---|---:|---:|---:|",
        ]
    )
    for scenario in scenario_order:
        scenario_rows = micro[micro["scenario"].eq(scenario)]
        for year, group in scenario_rows.groupby("year", sort=True):
            lines.append(
                f"| `{scenario}` | {year} | {len(group)} | {group['profit_abs'].sum():+.2f} USDT |"
            )

    lines.extend(
        [
            "",
            "## Fee-induced Path Changes",
            "",
            "| Scenario | Strategy | Matched entries | Baseline only | Stress only | Changed exits | Changed order counts |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in paths.iterrows():
        lines.append(
            f"| `{row['scenario']}` | `{row['strategy']}` | {row['matched_entries']} | "
            f"{row['baseline_only_entries']} | {row['stressed_only_entries']} | {row['changed_exits']} | "
            f"{row['changed_order_counts']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    baseline_zip = Path(args.baseline_zip).resolve()
    fee1p5_zip = Path(args.fee1p5_zip).resolve()
    fee2_zip = Path(args.fee2_zip).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    archives = {
        "baseline": (load_archive(baseline_zip), baseline_zip),
        "fee1p5x": (load_archive(fee1p5_zip), fee1p5_zip),
        "fee2x": (load_archive(fee2_zip), fee2_zip),
    }
    summary_rows: list[dict[str, Any]] = []
    micro_details: list[dict[str, Any]] = []
    for scenario, (strategies, source_zip) in archives.items():
        for strategy_name in (CONTROL, CANDIDATE):
            summary_rows.append(
                reported_summary(scenario, strategy_name, strategies[strategy_name], source_zip)
            )
        micro_details.extend(micro_rows(scenario, strategies[CANDIDATE], source_zip))

    fee2_strategies, fee2_source = archives["fee2x"]
    for scenario, slippage in SLIPPAGE.items():
        for strategy_name in (CONTROL, CANDIDATE):
            summary_rows.append(
                slippage_summary(
                    scenario,
                    strategy_name,
                    fee2_strategies[strategy_name],
                    fee2_source,
                    slippage,
                )
            )
        micro_details.extend(
            micro_rows(scenario, fee2_strategies[CANDIDATE], fee2_source, slippage)
        )

    baseline_strategies, _ = archives["baseline"]
    path_rows = [
        path_comparison(
            baseline_strategies[strategy_name],
            archives[scenario][0][strategy_name],
            scenario,
            strategy_name,
        )
        for scenario in ("fee1p5x", "fee2x")
        for strategy_name in (CONTROL, CANDIDATE)
    ]

    summary = pd.DataFrame(summary_rows)
    micro = pd.DataFrame(micro_details)
    paths = pd.DataFrame(path_rows)
    summary.to_csv(output_dir / "execution_stress_summary.csv", index=False)
    micro.to_csv(output_dir / "execution_stress_micro_trades.csv", index=False)
    micro.groupby(["scenario", "year"], as_index=False).agg(
        trades=("pair", "size"),
        wins=("profit_abs", lambda values: int((values > 0).sum())),
        profit_abs=("profit_abs", "sum"),
        profit_ratio_sum=("profit_ratio", "sum"),
    ).to_csv(output_dir / "execution_stress_micro_yearly.csv", index=False)
    paths.to_csv(output_dir / "execution_stress_path_changes.csv", index=False)
    report = markdown_report(summary, micro, paths)
    (output_dir / "execution_stress_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
