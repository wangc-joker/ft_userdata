from __future__ import annotations

import argparse
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCENARIO_ORDER = [
    "baseline",
    "fee1p5x",
    "fee2x",
    "fee2x_slip_light",
    "fee2x_slip_medium",
    "fee2x_slip_heavy",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit LongMicro sample uncertainty and profit concentration"
    )
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--top20-zip", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--iterations", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=20_260_727)
    return parser.parse_args()


def profit_factor(values: pd.Series | np.ndarray) -> float:
    array = np.asarray(values, dtype=float)
    wins = array[array > 0].sum()
    losses = -array[array < 0].sum()
    if losses == 0:
        return math.inf if wins > 0 else 0.0
    return float(wins / losses)


def wilson_interval(wins: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return math.nan, math.nan
    rate = wins / total
    denominator = 1.0 + z * z / total
    center = (rate + z * z / (2.0 * total)) / denominator
    margin = (
        z
        * math.sqrt(rate * (1.0 - rate) / total + z * z / (4.0 * total * total))
        / denominator
    )
    return center - margin, center + margin


def bootstrap_rows(
    frame: pd.DataFrame, iterations: int, seed: int
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset, scenario in enumerate(SCENARIO_ORDER):
        group = frame[frame["scenario"].eq(scenario)]
        ratios = group["profit_ratio"].to_numpy(dtype=float)
        profits = group["profit_abs"].to_numpy(dtype=float)
        if not len(ratios):
            continue
        rng = np.random.default_rng(seed + offset)
        choices = rng.integers(0, len(ratios), size=(iterations, len(ratios)))
        ratio_sums = ratios[choices].sum(axis=1)
        profit_sums = profits[choices].sum(axis=1)
        rows.append(
            {
                "scenario": scenario,
                "iterations": iterations,
                "observed_ratio_sum": ratios.sum(),
                "bootstrap_positive_probability": float((ratio_sums > 0).mean()),
                "ratio_sum_p2p5": float(np.quantile(ratio_sums, 0.025)),
                "ratio_sum_median": float(np.quantile(ratio_sums, 0.5)),
                "ratio_sum_p97p5": float(np.quantile(ratio_sums, 0.975)),
                "profit_abs_p2p5": float(np.quantile(profit_sums, 0.025)),
                "profit_abs_median": float(np.quantile(profit_sums, 0.5)),
                "profit_abs_p97p5": float(np.quantile(profit_sums, 0.975)),
            }
        )
    return rows


def scenario_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in SCENARIO_ORDER:
        group = frame[frame["scenario"].eq(scenario)].copy()
        if group.empty:
            continue
        wins = int(group["profit_abs"].gt(0).sum())
        low, high = wilson_interval(wins, len(group))
        roi = group[group["exit_reason"].eq("roi")]
        non_roi = group[~group["exit_reason"].eq("roi")]
        best = group.loc[group["profit_abs"].idxmax()]
        capped_5 = group["profit_ratio"].clip(upper=0.05).sum()
        capped_3 = group["profit_ratio"].clip(upper=0.03).sum()
        rows.append(
            {
                "scenario": scenario,
                "trades": len(group),
                "wins": wins,
                "winrate": wins / len(group),
                "wilson95_low": low,
                "wilson95_high": high,
                "profit_abs": group["profit_abs"].sum(),
                "profit_ratio_sum": group["profit_ratio"].sum(),
                "profit_factor_ratio": profit_factor(group["profit_ratio"]),
                "best_trade_pair": best["pair"],
                "best_trade_profit_abs": best["profit_abs"],
                "best_trade_share_of_net_profit": best["profit_abs"]
                / group["profit_abs"].sum(),
                "roi_trades": len(roi),
                "roi_profit_abs": roi["profit_abs"].sum(),
                "non_roi_profit_abs": non_roi["profit_abs"].sum(),
                "non_roi_profit_ratio_sum": non_roi["profit_ratio"].sum(),
                "profit_ratio_sum_cap_wins_5pct": capped_5,
                "profit_ratio_sum_cap_wins_3pct": capped_3,
            }
        )
    return rows


def grouped_rows(frame: pd.DataFrame, group_column: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in SCENARIO_ORDER:
        scenario_frame = frame[frame["scenario"].eq(scenario)]
        for key, group in scenario_frame.groupby(group_column, sort=True):
            remainder = scenario_frame.drop(group.index)
            rows.append(
                {
                    "scenario": scenario,
                    "group_type": group_column,
                    "group_value": key,
                    "group_trades": len(group),
                    "group_profit_abs": group["profit_abs"].sum(),
                    "group_profit_ratio_sum": group["profit_ratio"].sum(),
                    "profit_abs_without_group": remainder["profit_abs"].sum(),
                    "profit_ratio_without_group": remainder["profit_ratio"].sum(),
                }
            )
    return rows


def leave_one_trade_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in SCENARIO_ORDER:
        scenario_frame = frame[frame["scenario"].eq(scenario)]
        for index, trade in scenario_frame.iterrows():
            remainder = scenario_frame.drop(index)
            rows.append(
                {
                    "scenario": scenario,
                    "removed_pair": trade["pair"],
                    "removed_open_date": trade["open_date"],
                    "removed_exit_reason": trade["exit_reason"],
                    "removed_profit_abs": trade["profit_abs"],
                    "remaining_profit_abs": remainder["profit_abs"].sum(),
                    "remaining_profit_ratio_sum": remainder["profit_ratio"].sum(),
                }
            )
    return rows


def top20_micro_rows(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.endswith(".json") and not name.endswith("_config.json")
        ]
        if len(names) != 1:
            raise ValueError(f"Unable to identify result JSON in {path}")
        payload = json.loads(archive.read(names[0]))
    strategy = payload["strategy"]["DualTrendPyramidSecondAdd20LongMicroV1Strategy"]
    rows = [
        {
            "pair": trade["pair"],
            "open_date": trade["open_date"],
            "close_date": trade["close_date"],
            "exit_reason": trade.get("exit_reason"),
            "profit_abs": trade["profit_abs"],
            "profit_ratio": trade["profit_ratio"],
        }
        for trade in strategy.get("trades", [])
        if str(trade.get("enter_tag") or "") == "long_pullback_restart_1h_body"
    ]
    return pd.DataFrame(rows)


def fmt_pct(value: Any) -> str:
    return f"{float(value) * 100:+.2f}%"


def markdown_report(
    summary: pd.DataFrame,
    bootstrap: pd.DataFrame,
    groups: pd.DataFrame,
    leave_one: pd.DataFrame,
    top20: pd.DataFrame,
) -> str:
    by_scenario = summary.set_index("scenario")
    boot = bootstrap.set_index("scenario")
    baseline = by_scenario.loc["baseline"]
    heavy = by_scenario.loc["fee2x_slip_heavy"]
    baseline_pairs = groups[
        groups["scenario"].eq("baseline") & groups["group_type"].eq("pair")
    ]
    baseline_years = groups[
        groups["scenario"].eq("baseline") & groups["group_type"].eq("year")
    ]
    worst_loo = leave_one[leave_one["scenario"].eq("baseline")].sort_values(
        "remaining_profit_abs"
    ).iloc[0]
    top20_profit = top20["profit_abs"].sum()

    lines = [
        "# LongMicro Sample Concentration Audit",
        "",
        "## Sample Uncertainty",
        "",
        f"- Trades / wins / losses: `{int(baseline['trades'])} / {int(baseline['wins'])} / {int(baseline['trades'] - baseline['wins'])}`",
        f"- Win rate: `{baseline['winrate']:.2%}`; Wilson 95% interval: `{baseline['wilson95_low']:.2%} -> {baseline['wilson95_high']:.2%}`",
        f"- IID trade bootstrap probability of a positive seven-trade sum: `{boot.loc['baseline', 'bootstrap_positive_probability']:.2%}` baseline, `{boot.loc['fee2x_slip_heavy', 'bootstrap_positive_probability']:.2%}` under heavy execution stress",
        f"- Baseline bootstrap 95% interval for seven-trade return-ratio sum: `{fmt_pct(boot.loc['baseline', 'ratio_sum_p2p5'])} -> {fmt_pct(boot.loc['baseline', 'ratio_sum_p97p5'])}`",
        "",
        "The bootstrap interval includes losses. It also assumes the seven observations are independent and identically distributed, which is optimistic because five trades come from one pair.",
        "",
        "## Profit Concentration",
        "",
        f"- Baseline net Micro profit: `{baseline['profit_abs']:+.2f} USDT`",
        f"- Best single trade: `{baseline['best_trade_profit_abs']:+.2f} USDT`, `{baseline['best_trade_share_of_net_profit']:.2%}` of net profit",
        f"- Two ROI trades: `{baseline['roi_profit_abs']:+.2f} USDT`; all five non-ROI trades: `{baseline['non_roi_profit_abs']:+.2f} USDT`",
        f"- Return-ratio sum after capping winners at +5%: `{fmt_pct(baseline['profit_ratio_sum_cap_wins_5pct'])}`; at +3%: `{fmt_pct(baseline['profit_ratio_sum_cap_wins_3pct'])}`",
        f"- Removing the best single trade leaves `{worst_loo['remaining_profit_abs']:+.2f} USDT`",
        f"- Heavy execution stress still leaves `{heavy['profit_abs']:+.2f} USDT`, but non-ROI trades remain `{heavy['non_roi_profit_abs']:+.2f} USDT`",
        "",
        "## Pair Leave-out",
        "",
        "| Removed pair | Removed trades | Removed profit | Remaining profit | Remaining return-ratio sum |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in baseline_pairs.iterrows():
        lines.append(
            f"| `{row['group_value']}` | {row['group_trades']} | {row['group_profit_abs']:+.2f} USDT | "
            f"{row['profit_abs_without_group']:+.2f} USDT | {fmt_pct(row['profit_ratio_without_group'])} |"
        )
    lines.extend(
        [
            "",
            "## Year Leave-out",
            "",
            "| Removed year | Removed trades | Removed profit | Remaining profit |",
            "|---:|---:|---:|---:|",
        ]
    )
    for _, row in baseline_years.iterrows():
        lines.append(
            f"| {row['group_value']} | {row['group_trades']} | {row['group_profit_abs']:+.2f} USDT | "
            f"{row['profit_abs_without_group']:+.2f} USDT |"
        )
    lines.extend(
        [
            "",
            "## Cross-universe Duplication",
            "",
            f"- Top20/max6 Micro trades: `{len(top20)}`, profit `{top20_profit:+.2f} USDT`",
            "- All seven Top20/max6 Micro entries are the same pair and timestamp entries as Positive13/max3.",
            "- Top20 therefore confirms that the surrounding portfolio stays profitable, but it does not add an independent Micro signal observation or reduce the BNB concentration risk.",
            "",
            "## Decision",
            "",
            "Execution-cost robustness does not remove sample uncertainty. The candidate remains observation-only until independent out-of-sample trades broaden the pair and market-period distribution. Do not create a BNB-only rule from this audit; that would fit the only profitable historical cluster.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_csv).resolve()
    top20_path = Path(args.top20_zip).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(input_path)
    frame["open_date"] = pd.to_datetime(frame["open_date"], utc=True)

    counts = frame.groupby("scenario").size()
    missing = [scenario for scenario in SCENARIO_ORDER if counts.get(scenario, 0) != 7]
    if missing:
        raise ValueError(f"Expected seven trades in every scenario, invalid: {missing}")

    summary = pd.DataFrame(scenario_rows(frame))
    bootstrap = pd.DataFrame(bootstrap_rows(frame, args.iterations, args.seed))
    groups = pd.DataFrame(grouped_rows(frame, "pair") + grouped_rows(frame, "year"))
    leave_one = pd.DataFrame(leave_one_trade_rows(frame))
    top20 = top20_micro_rows(top20_path)
    baseline_keys = set(
        zip(
            frame[frame["scenario"].eq("baseline")]["pair"],
            frame[frame["scenario"].eq("baseline")]["open_date"].astype(str),
        )
    )
    top20_keys = set(zip(top20["pair"], pd.to_datetime(top20["open_date"], utc=True).astype(str)))
    if baseline_keys != top20_keys:
        raise ValueError("Top20 and Positive13 Micro entry sets are not identical")
    report = markdown_report(summary, bootstrap, groups, leave_one, top20)

    summary.to_csv(output_dir / "sample_concentration_summary.csv", index=False)
    bootstrap.to_csv(output_dir / "sample_bootstrap.csv", index=False)
    groups.to_csv(output_dir / "sample_group_leaveout.csv", index=False)
    leave_one.to_csv(output_dir / "sample_trade_leaveout.csv", index=False)
    top20.to_csv(output_dir / "sample_top20_micro_trades.csv", index=False)
    (output_dir / "sample_concentration_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
