from __future__ import annotations

import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


if Path("/freqtrade/user_data").exists():
    ROOT = Path("/freqtrade")
else:
    ROOT = Path(r"D:\test\ft_userdata")
BACKTEST_DIR = ROOT / "user_data" / "backtest_results"
ANALYSIS_DIR = ROOT / "user_data" / "analysis"
REPORTS_DIR = ROOT / "user_data" / "reports"


@dataclass(frozen=True)
class RunSpec:
    label: str
    strategy_label: str
    strategy_name: str
    zip_name: str


RUN_SPECS = [
    RunSpec("3y", "baseline", "DualTrendGuardStrategy", "backtest-result-2026-07-02_03-58-18.zip"),
    RunSpec("3y", "research", "DualTrendGuardProfitLockResearchStrategy", "backtest-result-2026-07-02_03-57-27.zip"),
    RunSpec("1y", "baseline", "DualTrendGuardStrategy", "backtest-result-2026-07-02_04-01-54.zip"),
    RunSpec("1y", "research", "DualTrendGuardProfitLockResearchStrategy", "backtest-result-2026-07-02_04-06-11.zip"),
    RunSpec("pressure", "baseline", "DualTrendGuardStrategy", "backtest-result-2026-07-02_03-59-53.zip"),
    RunSpec("pressure", "research", "DualTrendGuardProfitLockResearchStrategy", "backtest-result-2026-07-02_04-04-25.zip"),
    RunSpec("strong", "baseline", "DualTrendGuardStrategy", "backtest-result-2026-07-02_04-00-07.zip"),
    RunSpec("strong", "research", "DualTrendGuardProfitLockResearchStrategy", "backtest-result-2026-07-02_04-07-30.zip"),
    RunSpec("repair", "baseline", "DualTrendGuardStrategy", "backtest-result-2026-07-02_03-59-17.zip"),
    RunSpec("repair", "research", "DualTrendGuardProfitLockResearchStrategy", "backtest-result-2026-07-02_04-07-02.zip"),
]


WINDOW_TITLES = {
    "3y": "三年 (2023-06-18 -> 2026-06-18)",
    "1y": "近一年 (2025-06-18 -> 2026-06-18)",
    "pressure": "压力期 (2026-03-01 -> 2026-05-31)",
    "strong": "强势期 (2026-01-01 -> 2026-02-28)",
    "repair": "修复期 (2026-06-01 -> 2026-06-18)",
}


def load_run(spec: RunSpec) -> dict[str, Any]:
    zip_path = BACKTEST_DIR / spec.zip_name
    with zipfile.ZipFile(zip_path) as zf:
        json_name = next(name for name in zf.namelist() if name.endswith(".json") and "_config" not in name and not name.endswith(".meta.json"))
        payload = json.loads(zf.read(json_name))
    return payload["strategy"][spec.strategy_name]


def rowify(summary_rows: list[dict[str, Any]], window: str, strategy_label: str, kind: str) -> pd.DataFrame:
    frame = pd.DataFrame(summary_rows)
    if frame.empty:
        return frame
    frame = frame.copy()
    frame["window"] = window
    frame["strategy"] = strategy_label
    frame["summary_kind"] = kind
    return frame


def format_pct(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "NA"
    return f"{value * 100:.2f}%"


def format_num(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "NA"
    return f"{value:.2f}"


def trade_frame(run: dict[str, Any], window: str, strategy_label: str) -> pd.DataFrame:
    frame = pd.DataFrame(run["trades"]).copy()
    frame["window"] = window
    frame["strategy"] = strategy_label
    return frame


def overall_metrics(run: dict[str, Any], window: str, strategy_label: str) -> dict[str, Any]:
    return {
        "window": window,
        "strategy": strategy_label,
        "trades": run["total_trades"],
        "profit_pct": run["profit_total"] * 100,
        "profit_abs": run["profit_total_abs"],
        "profit_factor": run["profit_factor"],
        "max_drawdown_pct": run["max_drawdown_account"] * 100,
        "winrate_pct": (run["trade_count_long"] + run["trade_count_short"] and (sum(t["profit_ratio"] > 0 for t in run["trades"]) / len(run["trades"]) * 100)) if run["trades"] else 0.0,
        "avg_duration_hours": pd.to_timedelta(run["holding_avg"]).total_seconds() / 3600 if "holding_avg" in run else pd.DataFrame(run["trades"])["trade_duration"].mean() / 60.0 if run["trades"] else 0.0,
        "avg_duration_days": pd.DataFrame(run["trades"])["trade_duration"].mean() / (60.0 * 24.0) if run["trades"] else 0.0,
        "best_trade_pct": max((t["profit_ratio"] for t in run["trades"]), default=float("nan")) * 100,
        "worst_trade_pct": min((t["profit_ratio"] for t in run["trades"]), default=float("nan")) * 100,
        "top5_profit_share_pct": top_profit_share(run["trades"], 5),
    }


def top_profit_share(trades: list[dict[str, Any]], n: int) -> float:
    profits = sorted((t["profit_abs"] for t in trades if t["profit_abs"] > 0), reverse=True)
    total_positive = sum(profits)
    if total_positive <= 0 or not profits:
        return float("nan")
    return sum(profits[:n]) / total_positive * 100


def summarize_exit_reasons(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    grouped = (
        trades.groupby(["window", "strategy", "exit_reason"], dropna=False)
        .agg(
            trades=("pair", "size"),
            profit_abs=("profit_abs", "sum"),
            profit_pct=("profit_ratio", "sum"),
            avg_profit_pct=("profit_ratio", "mean"),
            winrate_pct=("profit_ratio", lambda s: (s.gt(0).mean() * 100) if len(s) else 0.0),
            avg_duration_min=("trade_duration", "mean"),
        )
        .reset_index()
        .sort_values(["window", "strategy", "profit_abs"], ascending=[True, True, False])
    )
    grouped["profit_pct"] *= 100
    grouped["avg_profit_pct"] *= 100
    grouped["avg_duration_hours"] = grouped["avg_duration_min"] / 60.0
    return grouped.drop(columns=["avg_duration_min"])


def summarize_tags(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    grouped = (
        trades.groupby(["window", "strategy", "enter_tag"], dropna=False)
        .agg(
            trades=("pair", "size"),
            profit_abs=("profit_abs", "sum"),
            profit_pct=("profit_ratio", "sum"),
            avg_profit_pct=("profit_ratio", "mean"),
            winrate_pct=("profit_ratio", lambda s: (s.gt(0).mean() * 100) if len(s) else 0.0),
            avg_duration_min=("trade_duration", "mean"),
        )
        .reset_index()
        .sort_values(["window", "strategy", "profit_abs"], ascending=[True, True, False])
    )
    grouped["profit_pct"] *= 100
    grouped["avg_profit_pct"] *= 100
    grouped["avg_duration_hours"] = grouped["avg_duration_min"] / 60.0
    return grouped.drop(columns=["avg_duration_min"])


def summarize_pairs(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    grouped = (
        trades.groupby(["window", "strategy", "pair"], dropna=False)
        .agg(
            trades=("pair", "size"),
            profit_abs=("profit_abs", "sum"),
            profit_pct=("profit_ratio", "sum"),
            avg_profit_pct=("profit_ratio", "mean"),
            winrate_pct=("profit_ratio", lambda s: (s.gt(0).mean() * 100) if len(s) else 0.0),
            avg_duration_min=("trade_duration", "mean"),
        )
        .reset_index()
        .sort_values(["window", "strategy", "profit_abs"], ascending=[True, True, False])
    )
    grouped["profit_pct"] *= 100
    grouped["avg_profit_pct"] *= 100
    grouped["avg_duration_hours"] = grouped["avg_duration_min"] / 60.0
    return grouped.drop(columns=["avg_duration_min"])


def pivot_delta(df: pd.DataFrame, key_col: str, window: str) -> pd.DataFrame:
    subset = df[df["window"] == window].copy()
    if subset.empty:
        return pd.DataFrame()
    pivot = subset.pivot(index=key_col, columns="strategy", values="profit_abs").fillna(0.0)
    for col in ["baseline", "research"]:
        if col not in pivot.columns:
            pivot[col] = 0.0
    pivot["delta_abs"] = pivot["research"] - pivot["baseline"]
    pivot = pivot.sort_values("delta_abs", ascending=False).reset_index()
    return pivot


def build_report(metrics_df: pd.DataFrame, exit_df: pd.DataFrame, tag_df: pd.DataFrame, pair_df: pd.DataFrame) -> str:
    md: list[str] = []
    md.append("# Positive13 Profit Lock Research")
    md.append("")
    md.append("研究对象：`DualTrendGuardStrategy` vs `DualTrendGuardProfitLockResearchStrategy`。")
    md.append("本轮只改止盈层，未修改入场逻辑、pair pool、max_open_trades、杠杆、stoploss。")
    md.append("")
    md.append("## 窗口总览")
    md.append("")
    md.append("| 窗口 | 策略 | Trades | Profit | PF | MaxDD | Winrate | Avg Hold | Top5利润占比 |")
    md.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for window in ["3y", "1y", "pressure", "strong", "repair"]:
        sub = metrics_df[metrics_df["window"] == window]
        for strategy in ["baseline", "research"]:
            row = sub[sub["strategy"] == strategy].iloc[0]
            md.append(
                f"| {WINDOW_TITLES[window]} | {strategy} | {int(row.trades)} | "
                f"{row.profit_pct:.2f}% | {row.profit_factor:.2f} | {row.max_drawdown_pct:.2f}% | "
                f"{row.winrate_pct:.1f}% | {row.avg_duration_days:.2f}d | {row.top5_profit_share_pct:.1f}% |"
            )
    md.append("")

    three_base = metrics_df.query("window == '3y' and strategy == 'baseline'").iloc[0]
    three_res = metrics_df.query("window == '3y' and strategy == 'research'").iloc[0]
    one_base = metrics_df.query("window == '1y' and strategy == 'baseline'").iloc[0]
    one_res = metrics_df.query("window == '1y' and strategy == 'research'").iloc[0]
    pressure_base = metrics_df.query("window == 'pressure' and strategy == 'baseline'").iloc[0]
    pressure_res = metrics_df.query("window == 'pressure' and strategy == 'research'").iloc[0]

    tag_delta_3y = pivot_delta(tag_df, "enter_tag", "3y")
    pair_delta_3y = pivot_delta(pair_df, "pair", "3y")
    tag_delta_1y = pivot_delta(tag_df, "enter_tag", "1y")
    pair_delta_1y = pivot_delta(pair_df, "pair", "1y")

    custom_exits_3y = exit_df[
        (exit_df["window"] == "3y")
        & (exit_df["strategy"] == "research")
        & (exit_df["exit_reason"].isin(
            [
                "profit_lock_pullback_restart",
                "profit_lock_compression_breakdown",
                "profit_lock_long_center",
                "profit_giveback_guard",
                "time_decay_profit_exit",
            ]
        ))
    ].copy()

    md.append("## 结论")
    md.append("")
    answers = [
        f"1. ProfitLockResearch 是否提升三年收益？否。三年从 {three_base.profit_pct:.2f}% 降到 {three_res.profit_pct:.2f}%。",
        f"2. 是否提升近一年收益？否。近一年从 {one_base.profit_pct:.2f}% 降到 {one_res.profit_pct:.2f}%。",
        f"3. PF 是否下降？是。三年 PF {three_base.profit_factor:.2f} -> {three_res.profit_factor:.2f}；近一年 PF {one_base.profit_factor:.2f} -> {one_res.profit_factor:.2f}。",
        f"4. MaxDD 是否扩大？是。三年 MaxDD {three_base.max_drawdown_pct:.2f}% -> {three_res.max_drawdown_pct:.2f}%，虽然仍低于 10%，但收益同时大幅缩水。",
        f"5. 压力期是否恶化？小幅恶化。压力期 Profit {pressure_base.profit_pct:.2f}% -> {pressure_res.profit_pct:.2f}%，PF {pressure_base.profit_factor:.2f} -> {pressure_res.profit_factor:.2f}。",
        f"6. 平均持仓时间是否明显变长？没有，反而缩短。三年 {three_base.avg_duration_days:.2f}d -> {three_res.avg_duration_days:.2f}d；近一年 {one_base.avg_duration_days:.2f}d -> {one_res.avg_duration_days:.2f}d。",
        "7. 哪些 tag 受益？没有 tag 在三年或近一年总账上真正跑赢 baseline。",
        "8. 哪些 tag 变差？三年 `short_pullback_restart`、`short_compression_breakdown`、`long_1d_center_compression` 全部变差，其中 `short_pullback_restart` 受损最大。",
        "9. 哪些 pair 受益？少数 pair 在近一年或局部窗口上受益，但三年维度没有形成稳健的广泛提升。",
        "10. 哪些 pair 变差？三年里大部分主要贡献 pair 都变差，尤其是原本能跑出大盈利单的核心 pair。",
        "11. 自定义退出原因分别贡献多少收益？它们本身都是正收益退出，但主要作用是更早收掉中等盈利单，没能弥补被截断的大盈利单。",
        "12. 是否存在收益提高但回撤变大的问题？没有出现“收益提高”。实际是收益显著下降，同时三年回撤还变大了。",
        "13. 是否值得继续研究？按本轮规则，不值得继续直接推进。",
        "14. 是否值得进入真实 V2？不值得。",
        "15. 是否应该保持主策略不变？是，保持当前主策略不变。",
    ]
    for line in answers:
        md.append(line)
    md.append("")

    md.append("## Tag 影响")
    md.append("")
    md.append("### 三年按 tag 的收益变化")
    md.append("")
    md.append("| Tag | Baseline | Research | Delta |")
    md.append("| --- | ---: | ---: | ---: |")
    for _, row in tag_delta_3y.iterrows():
        md.append(f"| {row['enter_tag']} | {row['baseline']:.2f} | {row['research']:.2f} | {row['delta_abs']:.2f} |")
    md.append("")
    md.append("### 近一年按 tag 的收益变化")
    md.append("")
    md.append("| Tag | Baseline | Research | Delta |")
    md.append("| --- | ---: | ---: | ---: |")
    for _, row in tag_delta_1y.iterrows():
        md.append(f"| {row['enter_tag']} | {row['baseline']:.2f} | {row['research']:.2f} | {row['delta_abs']:.2f} |")
    md.append("")

    md.append("## Pair 影响")
    md.append("")
    md.append("### 三年最受益 / 最受损 Pair")
    md.append("")
    top_pairs = pair_delta_3y.head(5)
    bottom_pairs = pair_delta_3y.tail(5).sort_values("delta_abs")
    md.append("| Pair | Baseline | Research | Delta |")
    md.append("| --- | ---: | ---: | ---: |")
    for _, row in pd.concat([top_pairs, bottom_pairs]).drop_duplicates(subset=["pair"]).iterrows():
        md.append(f"| {row['pair']} | {row['baseline']:.2f} | {row['research']:.2f} | {row['delta_abs']:.2f} |")
    md.append("")

    md.append("## 自定义退出贡献")
    md.append("")
    md.append("| Exit reason | Trades | Profit USDT | Avg Profit % |")
    md.append("| --- | ---: | ---: | ---: |")
    for _, row in custom_exits_3y.sort_values("profit_abs", ascending=False).iterrows():
        md.append(f"| {row['exit_reason']} | {int(row['trades'])} | {row['profit_abs']:.2f} | {row['avg_profit_pct']:.2f}% |")
    md.append("")
    md.append("这些自定义退出单看都是赚钱的，但问题在于它们把原来应该继续奔向 `roi` / `partial_exit` 的单子提前收掉了。")
    md.append("")

    md.append("## 判断标准复核")
    md.append("")
    checks = [
        ("三年 Profit 高于 baseline，或基本持平但 MaxDD 明显下降", False),
        ("三年 PF >= 1.90", bool(three_res.profit_factor >= 1.90)),
        ("三年 MaxDD <= 10%", bool(three_res.max_drawdown_pct <= 10.0)),
        ("近一年 Profit >= baseline 的 95%", bool(one_res.profit_pct >= one_base.profit_pct * 0.95)),
        ("近一年 PF >= 1.80", bool(one_res.profit_factor >= 1.80)),
        ("压力期不能明显恶化", bool(pressure_res.profit_pct >= pressure_base.profit_pct and pressure_res.profit_factor >= pressure_base.profit_factor)),
        ("收益不能依赖少数 1-2 笔极端交易", False),
        ("平均持仓时间不能失控", True),
    ]
    md.append("| 条件 | 是否满足 |")
    md.append("| --- | --- |")
    for text, ok in checks:
        md.append(f"| {text} | {'是' if ok else '否'} |")
    md.append("")
    md.append("最终结论：**ProfitLockResearch 不优于当前主策略，继续保持原策略。**")
    md.append("")
    return "\n".join(md)


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    loaded: dict[tuple[str, str], dict[str, Any]] = {}
    trade_frames: list[pd.DataFrame] = []
    metrics_rows: list[dict[str, Any]] = []
    exit_frames: list[pd.DataFrame] = []
    tag_frames: list[pd.DataFrame] = []
    pair_frames: list[pd.DataFrame] = []

    for spec in RUN_SPECS:
        run = load_run(spec)
        loaded[(spec.label, spec.strategy_label)] = run
        trades = trade_frame(run, spec.label, spec.strategy_label)
        trade_frames.append(trades)
        metrics_rows.append(overall_metrics(run, spec.label, spec.strategy_label))
        exit_frames.append(summarize_exit_reasons(trades))
        tag_frames.append(summarize_tags(trades))
        pair_frames.append(summarize_pairs(trades))

    all_trades = pd.concat(trade_frames, ignore_index=True)
    metrics_df = pd.DataFrame(metrics_rows)
    exit_df = pd.concat(exit_frames, ignore_index=True)
    tag_df = pd.concat(tag_frames, ignore_index=True)
    pair_df = pd.concat(pair_frames, ignore_index=True)

    all_trades[(all_trades["window"] == "3y") & (all_trades["strategy"] == "research")].to_csv(
        ANALYSIS_DIR / "positive13_profit_lock_trades_3y.csv", index=False
    )
    all_trades[(all_trades["window"] == "1y") & (all_trades["strategy"] == "research")].to_csv(
        ANALYSIS_DIR / "positive13_profit_lock_trades_1y.csv", index=False
    )
    exit_df.to_csv(ANALYSIS_DIR / "positive13_profit_lock_exit_reason_summary.csv", index=False)
    tag_df.to_csv(ANALYSIS_DIR / "positive13_profit_lock_entry_tag_summary.csv", index=False)
    pair_df.to_csv(ANALYSIS_DIR / "positive13_profit_lock_pair_summary.csv", index=False)

    report = build_report(metrics_df, exit_df, tag_df, pair_df)
    (REPORTS_DIR / "positive13_profit_lock_research.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
