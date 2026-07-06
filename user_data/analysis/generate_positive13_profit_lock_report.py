from __future__ import annotations

import json
import zipfile
import csv
from pathlib import Path


ROOT = Path(r"D:\test\ft_userdata")
BACKTEST_DIR = ROOT / "user_data" / "backtest_results"
ANALYSIS_DIR = ROOT / "user_data" / "analysis"
REPORTS_DIR = ROOT / "user_data" / "reports"


RUNS = [
    {
        "variant": "raw_3y",
        "zip": "backtest-result-2026-07-02_04-27-35.zip",
        "label": "Raw",
        "window": "3y",
        "family": "baseline",
    },
    {
        "variant": "raw_be_3y",
        "zip": "backtest-result-2026-07-02_04-25-53.zip",
        "label": "Raw + Breakeven",
        "window": "3y",
        "family": "baseline",
    },
    {
        "variant": "raw_be_guard_3y",
        "zip": "backtest-result-2026-07-02_04-25-50.zip",
        "label": "Raw + Breakeven + Guard",
        "window": "3y",
        "family": "baseline",
    },
    {
        "variant": "raw_1y",
        "zip": "backtest-result-2026-07-02_04-32-02.zip",
        "label": "Raw",
        "window": "1y",
        "family": "baseline",
    },
    {
        "variant": "raw_be_1y",
        "zip": "backtest-result-2026-07-02_04-31-14.zip",
        "label": "Raw + Breakeven",
        "window": "1y",
        "family": "baseline",
    },
    {
        "variant": "raw_be_guard_1y",
        "zip": "backtest-result-2026-07-02_04-31-12.zip",
        "label": "Raw + Breakeven + Guard",
        "window": "1y",
        "family": "baseline",
    },
    {
        "variant": "raw_be_profit_lock_3y",
        "zip": "backtest-result-2026-07-02_04-44-53.zip",
        "label": "Raw + Breakeven + ProfitLock",
        "window": "3y",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_guard_profit_lock_3y",
        "zip": "backtest-result-2026-07-02_04-44-50.zip",
        "label": "Raw + Breakeven + Guard + ProfitLock",
        "window": "3y",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_profit_lock_1y",
        "zip": "backtest-result-2026-07-02_04-41-45.zip",
        "label": "Raw + Breakeven + ProfitLock",
        "window": "1y",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_guard_profit_lock_1y",
        "zip": "backtest-result-2026-07-02_04-41-43.zip",
        "label": "Raw + Breakeven + Guard + ProfitLock",
        "window": "1y",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_profit_lock_strong",
        "zip": "backtest-result-2026-07-02_04-46-22.zip",
        "label": "Raw + Breakeven + ProfitLock",
        "window": "strong_2026_01_01_2026_02_28",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_profit_lock_pressure",
        "zip": "backtest-result-2026-07-02_04-46-13.zip",
        "label": "Raw + Breakeven + ProfitLock",
        "window": "pressure_2026_03_01_2026_05_31",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_profit_lock_repair",
        "zip": "backtest-result-2026-07-02_05-00-03.zip",
        "label": "Raw + Breakeven + ProfitLock",
        "window": "repair_2026_06_01_2026_06_18",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_guard_profit_lock_strong",
        "zip": "backtest-result-2026-07-02_04-50-20.zip",
        "label": "Raw + Breakeven + Guard + ProfitLock",
        "window": "strong_2026_01_01_2026_02_28",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_guard_profit_lock_pressure",
        "zip": "backtest-result-2026-07-02_04-50-12.zip",
        "label": "Raw + Breakeven + Guard + ProfitLock",
        "window": "pressure_2026_03_01_2026_05_31",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_guard_profit_lock_repair",
        "zip": "backtest-result-2026-07-02_04-52-33.zip",
        "label": "Raw + Breakeven + Guard + ProfitLock",
        "window": "repair_2026_06_01_2026_06_18",
        "family": "profit_lock",
    },
    {
        "variant": "raw_be_strong",
        "zip": "backtest-result-2026-07-02_04-54-17.zip",
        "label": "Raw + Breakeven",
        "window": "strong_2026_01_01_2026_02_28",
        "family": "baseline",
    },
    {
        "variant": "raw_be_pressure",
        "zip": "backtest-result-2026-07-02_04-54-16.zip",
        "label": "Raw + Breakeven",
        "window": "pressure_2026_03_01_2026_05_31",
        "family": "baseline",
    },
    {
        "variant": "raw_be_repair",
        "zip": "backtest-result-2026-07-02_04-53-54.zip",
        "label": "Raw + Breakeven",
        "window": "repair_2026_06_01_2026_06_18",
        "family": "baseline",
    },
    {
        "variant": "raw_be_guard_strong",
        "zip": "backtest-result-2026-07-02_04-54-19.zip",
        "label": "Raw + Breakeven + Guard",
        "window": "strong_2026_01_01_2026_02_28",
        "family": "baseline",
    },
    {
        "variant": "raw_be_guard_pressure",
        "zip": "backtest-result-2026-07-02_04-54-18.zip",
        "label": "Raw + Breakeven + Guard",
        "window": "pressure_2026_03_01_2026_05_31",
        "family": "baseline",
    },
    {
        "variant": "raw_be_guard_repair",
        "zip": "backtest-result-2026-07-02_04-53-55.zip",
        "label": "Raw + Breakeven + Guard",
        "window": "repair_2026_06_01_2026_06_18",
        "family": "baseline",
    },
]


PARENT_MAP = {
    "raw_be_profit_lock": "Raw + Breakeven",
    "raw_be_guard_profit_lock": "Raw + Breakeven + Guard",
}


def load_run(run: dict) -> dict:
    zip_path = BACKTEST_DIR / run["zip"]
    with zipfile.ZipFile(zip_path) as zf:
        json_name = next(name for name in zf.namelist() if name.endswith(".json") and "_config" not in name)
        payload = json.loads(zf.read(json_name))
    strategy_name, strategy = next(iter(payload["strategy"].items()))
    result = {
        **run,
        "strategy_name": strategy_name,
        "strategy": strategy,
    }
    return result


def fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def fmt_num(value: float) -> str:
    return f"{value:.2f}"


loaded = [load_run(run) for run in RUNS]

summary_rows = []
trades_rows = []
pair_rows = []
tag_rows = []
exit_rows = []

for run in loaded:
    strategy = run["strategy"]
    summary_rows.append(
        {
            "variant": run["variant"],
            "label": run["label"],
            "family": run["family"],
            "window": run["window"],
            "strategy_name": run["strategy_name"],
            "trades": strategy["total_trades"],
            "profit_total_pct": strategy["profit_total"] * 100,
            "profit_total_abs": strategy["profit_total_abs"],
            "profit_factor": strategy["profit_factor"],
            "max_drawdown_pct": strategy["max_drawdown_account"] * 100,
            "winrate_pct": strategy["winrate"] * 100,
            "holding_avg": strategy["holding_avg"],
            "trades_per_day": strategy["trades_per_day"],
            "rejected_signals": strategy["rejected_signals"],
        }
    )

    for trade in strategy["trades"]:
        trade_copy = {
            "variant": run["variant"],
            "label": run["label"],
            "window": run["window"],
            "family": run["family"],
            **trade,
        }
        trades_rows.append(trade_copy)

    for pair in strategy["results_per_pair"]:
        pair_rows.append(
            {
                "variant": run["variant"],
                "label": run["label"],
                "window": run["window"],
                "family": run["family"],
                **pair,
            }
        )

    for tag in strategy["results_per_enter_tag"]:
        tag_rows.append(
            {
                "variant": run["variant"],
                "label": run["label"],
                "window": run["window"],
                "family": run["family"],
                **tag,
            }
        )

    for exit_reason in strategy["exit_reason_summary"]:
        exit_rows.append(
            {
                "variant": run["variant"],
                "label": run["label"],
                "window": run["window"],
                "family": run["family"],
                **exit_reason,
            }
        )

summary_rows_by_variant_window = {
    (row["variant"], row["window"]): row for row in summary_rows
}


def variant_summary(variant: str, window: str) -> dict:
    row = summary_rows_by_variant_window.get((variant, window))
    if not row:
        raise KeyError(f"missing summary for {variant=} {window=}")
    return row


def compare_section(child_variant: str, parent_variant: str, window: str) -> dict:
    child = variant_summary(child_variant, window)
    parent = variant_summary(parent_variant, window)
    return {
        "child": child,
        "parent": parent,
        "profit_delta": child["profit_total_pct"] - parent["profit_total_pct"],
        "pf_delta": child["profit_factor"] - parent["profit_factor"],
        "dd_delta": child["max_drawdown_pct"] - parent["max_drawdown_pct"],
        "trades_delta": child["trades"] - parent["trades"],
    }


comparisons = {
    "be_3y": compare_section("raw_be_profit_lock_3y", "raw_be_3y", "3y"),
    "be_1y": compare_section("raw_be_profit_lock_1y", "raw_be_1y", "1y"),
    "be_pressure": compare_section("raw_be_profit_lock_pressure", "raw_be_pressure", "pressure_2026_03_01_2026_05_31"),
    "be_strong": compare_section("raw_be_profit_lock_strong", "raw_be_strong", "strong_2026_01_01_2026_02_28"),
    "be_repair": compare_section("raw_be_profit_lock_repair", "raw_be_repair", "repair_2026_06_01_2026_06_18"),
    "guard_3y": compare_section("raw_be_guard_profit_lock_3y", "raw_be_guard_3y", "3y"),
    "guard_1y": compare_section("raw_be_guard_profit_lock_1y", "raw_be_guard_1y", "1y"),
    "guard_pressure": compare_section("raw_be_guard_profit_lock_pressure", "raw_be_guard_pressure", "pressure_2026_03_01_2026_05_31"),
    "guard_strong": compare_section("raw_be_guard_profit_lock_strong", "raw_be_guard_strong", "strong_2026_01_01_2026_02_28"),
    "guard_repair": compare_section("raw_be_guard_profit_lock_repair", "raw_be_guard_repair", "repair_2026_06_01_2026_06_18"),
}


profit_lock_pair_rows = [row for row in pair_rows if row["family"] == "profit_lock"]
profit_lock_tag_rows = [row for row in tag_rows if row["family"] == "profit_lock"]
profit_lock_exit_rows = [row for row in exit_rows if row["family"] == "profit_lock"]

trades_3y_rows = [
    row for row in trades_rows if row["variant"] in {"raw_be_profit_lock_3y", "raw_be_guard_profit_lock_3y"}
]
trades_1y_rows = [
    row for row in trades_rows if row["variant"] in {"raw_be_profit_lock_1y", "raw_be_guard_profit_lock_1y"}
]

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    fieldnames = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


write_csv(ANALYSIS_DIR / "positive13_profit_lock_trades_3y.csv", trades_3y_rows)
write_csv(ANALYSIS_DIR / "positive13_profit_lock_trades_1y.csv", trades_1y_rows)
write_csv(ANALYSIS_DIR / "positive13_profit_lock_exit_reason_summary.csv", profit_lock_exit_rows)
write_csv(ANALYSIS_DIR / "positive13_profit_lock_entry_tag_summary.csv", profit_lock_tag_rows)
write_csv(ANALYSIS_DIR / "positive13_profit_lock_pair_summary.csv", profit_lock_pair_rows)
write_csv(ANALYSIS_DIR / "positive13_profit_lock_overview.csv", summary_rows)


def top_items(rows: list[dict], variant: str, window: str, group_col: str, profit_col: str = "profit_total_abs", n: int = 3):
    subset = [
        row
        for row in rows
        if row["variant"] == variant and row["window"] == window and row.get(group_col) != "TOTAL"
    ]
    if not subset:
        return [], []
    top = sorted(subset, key=lambda row: row[profit_col], reverse=True)[:n]
    bottom = sorted(subset, key=lambda row: row[profit_col])[:n]
    return (
        [[row[group_col], row[profit_col]] for row in top],
        [[row[group_col], row[profit_col]] for row in bottom],
    )


be_tag_top, be_tag_bottom = top_items(profit_lock_tag_rows, "raw_be_profit_lock_3y", "3y", "key")
guard_tag_top, guard_tag_bottom = top_items(profit_lock_tag_rows, "raw_be_guard_profit_lock_3y", "3y", "key")
be_pair_top, be_pair_bottom = top_items(profit_lock_pair_rows, "raw_be_profit_lock_3y", "3y", "key")
guard_pair_top, guard_pair_bottom = top_items(profit_lock_pair_rows, "raw_be_guard_profit_lock_3y", "3y", "key")


def exit_reason_text(variant: str, window: str) -> str:
    subset = [
        row
        for row in profit_lock_exit_rows
        if row["variant"] == variant and row["window"] == window and row.get("key") != "TOTAL"
    ]
    if not subset:
        return "无"
    subset = sorted(subset, key=lambda row: row["profit_total_abs"], reverse=True)
    parts = []
    for row in subset:
        parts.append(f"{row['key']}: {row['profit_total_abs']:.2f}U ({row['profit_total_pct']:.2f}%)")
    return "; ".join(parts)


def list_text(items) -> str:
    if not items:
        return "无"
    return "; ".join(f"{name}: {value:.2f}U" for name, value in items)


report = f"""# Positive13 Profit Lock Research

生成日期: 2026-07-02

## 本轮基线定义

- Raw 基线: `DualTrendRawStrategy`
- 候选基线 1: `DualTrendRawBreakevenStrategy`
- 候选基线 2: `DualTrendRawBreakevenGuardStrategy`
- 止盈研究候选 1: `DualTrendRawBreakevenProfitLockResearchStrategy`
- 止盈研究候选 2: `DualTrendRawBreakevenGuardProfitLockResearchStrategy`

## 核心结论

1. ProfitLockResearch **没有提升三年收益**。  
   - `Raw + Breakeven`: {fmt_num(comparisons['be_3y']['parent']['profit_total_pct'])}% -> {fmt_num(comparisons['be_3y']['child']['profit_total_pct'])}%，变化 {fmt_num(comparisons['be_3y']['profit_delta'])} pct
   - `Raw + Breakeven + Guard`: {fmt_num(comparisons['guard_3y']['parent']['profit_total_pct'])}% -> {fmt_num(comparisons['guard_3y']['child']['profit_total_pct'])}%，变化 {fmt_num(comparisons['guard_3y']['profit_delta'])} pct

2. ProfitLockResearch **也没有提升近一年收益**。  
   - `Raw + Breakeven`: {fmt_num(comparisons['be_1y']['parent']['profit_total_pct'])}% -> {fmt_num(comparisons['be_1y']['child']['profit_total_pct'])}%，变化 {fmt_num(comparisons['be_1y']['profit_delta'])} pct
   - `Raw + Breakeven + Guard`: {fmt_num(comparisons['guard_1y']['parent']['profit_total_pct'])}% -> {fmt_num(comparisons['guard_1y']['child']['profit_total_pct'])}%，变化 {fmt_num(comparisons['guard_1y']['profit_delta'])} pct

3. PF 没有更强。  
   - `Raw + Breakeven`: 3y PF {fmt_num(comparisons['be_3y']['parent']['profit_factor'])} -> {fmt_num(comparisons['be_3y']['child']['profit_factor'])}
   - `Raw + Breakeven + Guard`: 3y PF {fmt_num(comparisons['guard_3y']['parent']['profit_factor'])} -> {fmt_num(comparisons['guard_3y']['child']['profit_factor'])}

4. MaxDD 没有带来足够补偿。  
   - `Raw + Breakeven`: 3y MaxDD {fmt_num(comparisons['be_3y']['parent']['max_drawdown_pct'])}% -> {fmt_num(comparisons['be_3y']['child']['max_drawdown_pct'])}%
   - `Raw + Breakeven + Guard`: 3y MaxDD {fmt_num(comparisons['guard_3y']['parent']['max_drawdown_pct'])}% -> {fmt_num(comparisons['guard_3y']['child']['max_drawdown_pct'])}%

5. 压力期单窗口没有恶化，但这种改善不足以支撑整体采用。  
   - `Raw + Breakeven`: {fmt_num(comparisons['be_pressure']['parent']['profit_total_pct'])}% -> {fmt_num(comparisons['be_pressure']['child']['profit_total_pct'])}%
   - `Raw + Breakeven + Guard`: {fmt_num(comparisons['guard_pressure']['parent']['profit_total_pct'])}% -> {fmt_num(comparisons['guard_pressure']['child']['profit_total_pct'])}%

6. 这轮研究的主要效果，不是放大利润，而是**把更多单子提前锁成小盈利/小回吐**，结果是胜率更好看，但大盈利单被切短。

## 总体对照

### 3年

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw | {int(variant_summary('raw_3y', '3y')['trades'])} | {fmt_num(variant_summary('raw_3y', '3y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_3y', '3y')['profit_factor'])} | {fmt_num(variant_summary('raw_3y', '3y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_3y', '3y')['winrate_pct'])}% |
| Raw + Breakeven | {int(variant_summary('raw_be_3y', '3y')['trades'])} | {fmt_num(variant_summary('raw_be_3y', '3y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_be_3y', '3y')['profit_factor'])} | {fmt_num(variant_summary('raw_be_3y', '3y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_be_3y', '3y')['winrate_pct'])}% |
| Raw + Breakeven + Guard | {int(variant_summary('raw_be_guard_3y', '3y')['trades'])} | {fmt_num(variant_summary('raw_be_guard_3y', '3y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_be_guard_3y', '3y')['profit_factor'])} | {fmt_num(variant_summary('raw_be_guard_3y', '3y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_be_guard_3y', '3y')['winrate_pct'])}% |
| Raw + Breakeven + ProfitLock | {int(variant_summary('raw_be_profit_lock_3y', '3y')['trades'])} | {fmt_num(variant_summary('raw_be_profit_lock_3y', '3y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_be_profit_lock_3y', '3y')['profit_factor'])} | {fmt_num(variant_summary('raw_be_profit_lock_3y', '3y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_be_profit_lock_3y', '3y')['winrate_pct'])}% |
| Raw + Breakeven + Guard + ProfitLock | {int(variant_summary('raw_be_guard_profit_lock_3y', '3y')['trades'])} | {fmt_num(variant_summary('raw_be_guard_profit_lock_3y', '3y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_be_guard_profit_lock_3y', '3y')['profit_factor'])} | {fmt_num(variant_summary('raw_be_guard_profit_lock_3y', '3y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_be_guard_profit_lock_3y', '3y')['winrate_pct'])}% |

### 近1年

| 版本 | Trades | Profit | PF | MaxDD | Winrate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw | {int(variant_summary('raw_1y', '1y')['trades'])} | {fmt_num(variant_summary('raw_1y', '1y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_1y', '1y')['profit_factor'])} | {fmt_num(variant_summary('raw_1y', '1y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_1y', '1y')['winrate_pct'])}% |
| Raw + Breakeven | {int(variant_summary('raw_be_1y', '1y')['trades'])} | {fmt_num(variant_summary('raw_be_1y', '1y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_be_1y', '1y')['profit_factor'])} | {fmt_num(variant_summary('raw_be_1y', '1y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_be_1y', '1y')['winrate_pct'])}% |
| Raw + Breakeven + Guard | {int(variant_summary('raw_be_guard_1y', '1y')['trades'])} | {fmt_num(variant_summary('raw_be_guard_1y', '1y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_be_guard_1y', '1y')['profit_factor'])} | {fmt_num(variant_summary('raw_be_guard_1y', '1y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_be_guard_1y', '1y')['winrate_pct'])}% |
| Raw + Breakeven + ProfitLock | {int(variant_summary('raw_be_profit_lock_1y', '1y')['trades'])} | {fmt_num(variant_summary('raw_be_profit_lock_1y', '1y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_be_profit_lock_1y', '1y')['profit_factor'])} | {fmt_num(variant_summary('raw_be_profit_lock_1y', '1y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_be_profit_lock_1y', '1y')['winrate_pct'])}% |
| Raw + Breakeven + Guard + ProfitLock | {int(variant_summary('raw_be_guard_profit_lock_1y', '1y')['trades'])} | {fmt_num(variant_summary('raw_be_guard_profit_lock_1y', '1y')['profit_total_pct'])}% | {fmt_num(variant_summary('raw_be_guard_profit_lock_1y', '1y')['profit_factor'])} | {fmt_num(variant_summary('raw_be_guard_profit_lock_1y', '1y')['max_drawdown_pct'])}% | {fmt_num(variant_summary('raw_be_guard_profit_lock_1y', '1y')['winrate_pct'])}% |

## 分窗口观察

### Raw + Breakeven vs ProfitLock

| 窗口 | 基线 Profit | ProfitLock Profit | Delta | 基线 PF | ProfitLock PF |
| --- | ---: | ---: | ---: | ---: | ---: |
| Strong | {fmt_num(comparisons['be_strong']['parent']['profit_total_pct'])}% | {fmt_num(comparisons['be_strong']['child']['profit_total_pct'])}% | {fmt_num(comparisons['be_strong']['profit_delta'])} pct | {fmt_num(comparisons['be_strong']['parent']['profit_factor'])} | {fmt_num(comparisons['be_strong']['child']['profit_factor'])} |
| Pressure | {fmt_num(comparisons['be_pressure']['parent']['profit_total_pct'])}% | {fmt_num(comparisons['be_pressure']['child']['profit_total_pct'])}% | {fmt_num(comparisons['be_pressure']['profit_delta'])} pct | {fmt_num(comparisons['be_pressure']['parent']['profit_factor'])} | {fmt_num(comparisons['be_pressure']['child']['profit_factor'])} |
| Repair | {fmt_num(comparisons['be_repair']['parent']['profit_total_pct'])}% | {fmt_num(comparisons['be_repair']['child']['profit_total_pct'])}% | {fmt_num(comparisons['be_repair']['profit_delta'])} pct | {fmt_num(comparisons['be_repair']['parent']['profit_factor'])} | {fmt_num(comparisons['be_repair']['child']['profit_factor'])} |

### Raw + Breakeven + Guard vs ProfitLock

| 窗口 | 基线 Profit | ProfitLock Profit | Delta | 基线 PF | ProfitLock PF |
| --- | ---: | ---: | ---: | ---: | ---: |
| Strong | {fmt_num(comparisons['guard_strong']['parent']['profit_total_pct'])}% | {fmt_num(comparisons['guard_strong']['child']['profit_total_pct'])}% | {fmt_num(comparisons['guard_strong']['profit_delta'])} pct | {fmt_num(comparisons['guard_strong']['parent']['profit_factor'])} | {fmt_num(comparisons['guard_strong']['child']['profit_factor'])} |
| Pressure | {fmt_num(comparisons['guard_pressure']['parent']['profit_total_pct'])}% | {fmt_num(comparisons['guard_pressure']['child']['profit_total_pct'])}% | {fmt_num(comparisons['guard_pressure']['profit_delta'])} pct | {fmt_num(comparisons['guard_pressure']['parent']['profit_factor'])} | {fmt_num(comparisons['guard_pressure']['child']['profit_factor'])} |
| Repair | {fmt_num(comparisons['guard_repair']['parent']['profit_total_pct'])}% | {fmt_num(comparisons['guard_repair']['child']['profit_total_pct'])}% | {fmt_num(comparisons['guard_repair']['profit_delta'])} pct | {fmt_num(comparisons['guard_repair']['parent']['profit_factor'])} | {fmt_num(comparisons['guard_repair']['child']['profit_factor'])} |

## 哪些 tag 受益 / 变差

### Raw + Breakeven + ProfitLock (3y)

- 贡献最大的 tag: {list_text(be_tag_top)}
- 拖累最大的 tag: {list_text(be_tag_bottom)}

### Raw + Breakeven + Guard + ProfitLock (3y)

- 贡献最大的 tag: {list_text(guard_tag_top)}
- 拖累最大的 tag: {list_text(guard_tag_bottom)}

结论:
- 两个 ProfitLock 版本里，`short_pullback_restart` 仍然是主利润来源。
- `short_compression_breakdown` 在 ProfitLock 下仍然更弱，没有因为锁盈逻辑被明显修好。

## 哪些 pair 受益 / 变差

### Raw + Breakeven + ProfitLock (3y)

- 贡献最大的 pair: {list_text(be_pair_top)}
- 拖累最大的 pair: {list_text(be_pair_bottom)}

### Raw + Breakeven + Guard + ProfitLock (3y)

- 贡献最大的 pair: {list_text(guard_pair_top)}
- 拖累最大的 pair: {list_text(guard_pair_bottom)}

## 自定义退出原因贡献

### Raw + Breakeven + ProfitLock

{exit_reason_text('raw_be_profit_lock_3y', '3y')}

### Raw + Breakeven + Guard + ProfitLock

{exit_reason_text('raw_be_guard_profit_lock_3y', '3y')}

解读:
- `profit_giveback_guard`、`profit_lock_pullback_restart`、`profit_lock_compression_breakdown` 都能制造大量小正收益。
- 但它们没有替代掉 `roi` 贡献的大盈利结构，反而把一部分原本能走到更远的单子提前结束了。

## 对 14 个问题的直接回答

1. ProfitLockResearch 是否提升三年收益？  
   否，两个 ProfitLock 版本都显著低于各自基线。

2. 是否提升近一年收益？  
   否，两个 ProfitLock 版本都低于各自基线。

3. PF 是否下降？  
   是，3y 和 1y 都下降。

4. MaxDD 是否扩大？  
   有的版本略降、有的接近持平，但幅度不足以补偿利润损失。

5. 压力期是否恶化？  
   没有单独恶化，Pressure 窗口略好一些；但 Repair 窗口和整体 3y/1y 表现明显更差。

6. 平均持仓时间是否明显变长？  
   没有失控，但也没有换来更高收益。

7. 哪些 tag 受益？  
   主要还是 `short_pullback_restart` 受益。

8. 哪些 tag 变差？  
   `short_compression_breakdown` 依旧偏弱；长仓 tag 没有展示出稳定的额外增益。

9. 哪些 pair 受益？  
   主要是 XRP / ETH / PAXG / BNB 一类的顺势单。

10. 哪些 pair 变差？  
   BTC / LINK / ZEC / SOL 一类回吐更明显的单子仍然拖累。

11. 自定义退出原因分别贡献多少收益？  
   见上面“自定义退出原因贡献”和 CSV 文件。

12. 是否存在收益提高但回撤变大的问题？  
   这轮没有出现“收益提高”的前提，所以更准确说法是：收益下降，回撤改善也不够大。

13. 是否值得继续研究？  
   就这套参数和规则而言，不值得继续深挖。

14. 是否值得进入真实 V2？  
   不值得。

15. 是否应该保持主策略不变？  
   是。当前应保持 `Raw + Breakeven` / `Raw + Breakeven + Guard` 主线，不把这套 ProfitLock 并入主策略。

## 最终判断

按你给的判断标准，这轮 ProfitLockResearch **不优于当前主策略**：

- 3年收益没有高于基线，且不是“基本持平”；
- 近1年收益也没有达到基线 95%；
- 压力期虽略有改善，但不足以抵消整体收益退化；
- 收益结构更像是把大盈利单切成了很多小盈利单。

最终结论:

**ProfitLockResearch 不优于当前主策略，继续保持原策略。**
"""

(REPORTS_DIR / "positive13_profit_lock_research.md").write_text(report, encoding="utf-8")
print("generated report and csv outputs")
