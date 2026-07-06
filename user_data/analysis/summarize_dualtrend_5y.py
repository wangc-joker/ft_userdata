import csv
import json
import math
import zipfile
from collections import OrderedDict
from datetime import datetime
from pathlib import Path


ROOT = Path(r"D:\test\ft_userdata")
RESULTS_DIR = ROOT / "user_data" / "backtest_results"
REPORTS_DIR = ROOT / "user_data" / "reports"
ANALYSIS_DIR = ROOT / "user_data" / "analysis"

STRATEGIES = OrderedDict(
    [
        (
            "DualTrendRawStrategy",
            {
                "file": "DualTrendMainStrategies.py",
                "zip": "backtest-result-2026-07-03_06-37-52.zip",
                "desc": "原始双顺主策略，保留已验证的入场与形态过滤，不加保本，不加 guard。",
                "role": "原始基线",
            },
        ),
        (
            "DualTrendRawBreakevenStrategy",
            {
                "file": "DualTrendMainStrategies.py",
                "zip": "backtest-result-2026-07-03_06-35-54.zip",
                "desc": "在 Raw 基础上只加 +2% 保本保护，不加 guard，不做 +5% 强弱单分流。",
                "role": "保本对照",
            },
        ),
        (
            "DualTrendRawBreakevenGuardStrategy",
            {
                "file": "DualTrendMainStrategies.py",
                "zip": "backtest-result-2026-07-03_06-35-53.zip",
                "desc": "在 Raw + 保本基础上，再加 short_compression_breakdown 的 flush guard。",
                "role": "保本+guard 对照",
            },
        ),
        (
            "DualTrendBaselineStrategy",
            {
                "file": "DualTrendMainStrategies.py",
                "zip": "backtest-result-2026-07-03_06-46-14.zip",
                "desc": "主线 baseline：+2% 保本；到 +5% 后区分强弱单，弱单直接走，强单继续看 10%。",
                "role": "旧主基线",
            },
        ),
        (
            "DualTrendGuardStrategy",
            {
                "file": "DualTrendMainStrategies.py",
                "zip": "backtest-result-2026-07-03_06-46-15.zip",
                "desc": "在 Baseline 基础上增加 short_compression_breakdown 的 flush guard。",
                "role": "旧主 guard",
            },
        ),
        (
            "DualTrendRawBreakevenGuardStrongRunnerStructureStrategy",
            {
                "file": "DualTrendMainStrategies.py",
                "zip": "backtest-result-2026-07-03_06-45-45.zip",
                "desc": "当前候选主线：Raw + 保本 + guard；只在 short_pullback_restart 达到 +5% 后，用结构条件识别强趋势单并放行。",
                "role": "当前主候选",
            },
        ),
    ]
)


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def pct_num(value: float) -> float:
    return round(value * 100, 2)


def safe_pf(win_sum: float, loss_sum_abs: float) -> float:
    if loss_sum_abs == 0:
        return math.inf if win_sum > 0 else 0.0
    return win_sum / loss_sum_abs


def fmt_pf(value: float) -> str:
    if math.isinf(value):
        return "inf"
    return f"{value:.2f}"


def fmt_pct_num(value: float) -> str:
    return f"{value:.2f}%"


def load_strategy_payload(zip_name: str, strategy_name: str) -> dict:
    path = RESULTS_DIR / zip_name
    with zipfile.ZipFile(path) as zf:
        json_name = [n for n in zf.namelist() if n.endswith(".json") and "_config" not in n][0]
        data = json.loads(zf.read(json_name))
    return data["strategy"][strategy_name]


def compute_year_rows(payload: dict) -> list[dict]:
    trades = sorted(payload["trades"], key=lambda x: x["close_timestamp"])
    years: OrderedDict[int, list] = OrderedDict()
    for trade in trades:
        year = datetime.fromtimestamp(trade["close_timestamp"] / 1000).year
        years.setdefault(year, []).append(trade)

    balance = float(payload["starting_balance"])
    rows = []
    for year, year_trades in years.items():
        start_balance = balance
        cum_balance = start_balance
        peak = start_balance
        max_dd = 0.0
        win_sum = 0.0
        loss_sum_abs = 0.0
        wins = 0
        losses = 0

        for trade in year_trades:
            profit_abs = float(trade["profit_abs"])
            cum_balance += profit_abs
            peak = max(peak, cum_balance)
            if peak > 0:
                max_dd = max(max_dd, (peak - cum_balance) / peak)
            if profit_abs > 0:
                wins += 1
                win_sum += profit_abs
            elif profit_abs < 0:
                losses += 1
                loss_sum_abs += abs(profit_abs)

        profit_abs_total = sum(float(t["profit_abs"]) for t in year_trades)
        balance = start_balance + profit_abs_total
        trades_count = len(year_trades)
        rows.append(
            {
                "year": year,
                "start_balance": start_balance,
                "end_balance": balance,
                "profit_abs": profit_abs_total,
                "return_pct": (profit_abs_total / start_balance * 100.0) if start_balance else 0.0,
                "trades": trades_count,
                "winrate": (wins / trades_count * 100.0) if trades_count else 0.0,
                "profit_factor": safe_pf(win_sum, loss_sum_abs),
                "max_drawdown": max_dd * 100.0,
            }
        )
    return rows


def main() -> None:
    report_path = REPORTS_DIR / "dualtrend_5y_strategy_overview_2026-07-03.md"
    csv_path = ANALYSIS_DIR / "dualtrend_5y_strategy_overview_2026-07-03.csv"

    overall_rows = []
    yearly_rows = []
    detail_blocks = []

    for strategy_name, meta in STRATEGIES.items():
        payload = load_strategy_payload(meta["zip"], strategy_name)
        year_rows = compute_year_rows(payload)

        overall_row = {
            "strategy_name": strategy_name,
            "strategy_file": meta["file"],
            "role": meta["role"],
            "sample_start": payload["backtest_start"],
            "sample_end": payload["backtest_end"],
            "trades": payload["total_trades"],
            "profit_pct": pct_num(payload["profit_total"]),
            "final_balance": round(float(payload["final_balance"]), 3),
            "winrate": round(float(payload["winrate"]) * 100.0, 2),
            "profit_factor": round(float(payload["profit_factor"]), 2),
            "max_drawdown": round(float(payload["max_drawdown_account"]) * 100.0, 2),
        }
        overall_rows.append(overall_row)

        for row in year_rows:
            yearly_rows.append(
                {
                    "strategy_name": strategy_name,
                    "year": row["year"],
                    "start_balance": round(row["start_balance"], 3),
                    "end_balance": round(row["end_balance"], 3),
                    "profit_abs": round(row["profit_abs"], 3),
                    "return_pct": round(row["return_pct"], 2),
                    "trades": row["trades"],
                    "winrate": round(row["winrate"], 2),
                    "profit_factor": None if math.isinf(row["profit_factor"]) else round(row["profit_factor"], 2),
                    "max_drawdown": round(row["max_drawdown"], 2),
                }
            )

        detail_lines = [
            f"### {strategy_name}",
            "",
            f"- 策略文件: `{meta['file']}`",
            f"- 定位: {meta['role']}",
            f"- 核心内容: {meta['desc']}",
            f"- 样本区间: {payload['backtest_start']} -> {payload['backtest_end']}",
            f"- 总收益率: {fmt_pct_num(overall_row['profit_pct'])}",
            f"- PF: {overall_row['profit_factor']:.2f}",
            f"- 最大回撤: {fmt_pct_num(overall_row['max_drawdown'])}",
            f"- 胜率: {fmt_pct_num(overall_row['winrate'])}",
            f"- 成交笔数: {overall_row['trades']}",
            "",
            "| 年份 | 收益率 | PF | 最大回撤 | 胜率 | 笔数 | 期初资金 | 期末资金 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in year_rows:
            pf_text = fmt_pf(row["profit_factor"])
            detail_lines.append(
                f"| {row['year']} | {row['return_pct']:.2f}% | {pf_text} | {row['max_drawdown']:.2f}% | "
                f"{row['winrate']:.2f}% | {row['trades']} | {row['start_balance']:.2f} | {row['end_balance']:.2f} |"
            )
        detail_lines.append("")
        detail_blocks.append("\n".join(detail_lines))

    overall_rows.sort(key=lambda x: x["profit_pct"], reverse=True)

    report_lines = [
        "# DualTrend 策略 5 年回测总览",
        "",
        "## 说明",
        "",
        "- 本次整理的是当前保留下来的主策略/对照策略类。",
        "- 实际有效样本并非自然整 5 年，而是因为 1h/5m 数据可用性与启动 K 线要求，统一生效区间为 `2022-11-11 16:00:00 -> 2026-06-18 00:00:00`。",
        "- 币池为当前 Positive13 配置，`max_open_trades = 3`，`timeframe = 1h`，`timeframe_detail = 5m`。",
        "- 2022 和 2026 都是部分年份，解读时要按部分年份看。",
        "",
        "## 总表",
        "",
        "| 策略文件 | 策略名 | 定位 | 总收益率 | PF | 最大回撤 | 胜率 | 成交笔数 |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in overall_rows:
        report_lines.append(
            f"| `{row['strategy_file']}` | `{row['strategy_name']}` | {row['role']} | "
            f"{row['profit_pct']:.2f}% | {row['profit_factor']:.2f} | {row['max_drawdown']:.2f}% | "
            f"{row['winrate']:.2f}% | {row['trades']} |"
        )

    report_lines.extend(
        [
            "",
            "## 核心差异",
            "",
            "- `DualTrendRawStrategy`: 原始双顺主逻辑，不加保本，不加 guard。",
            "- `DualTrendRawBreakevenStrategy`: 在 Raw 上只加 +2% 保本。",
            "- `DualTrendRawBreakevenGuardStrategy`: 在 Raw + 保本上再加 compression flush guard。",
            "- `DualTrendBaselineStrategy`: 旧主线，+2% 保本后，在 +5% 位置区分强弱单；弱单平仓，强单继续吃到 ROI 10%。",
            "- `DualTrendGuardStrategy`: Baseline 再叠加 compression flush guard。",
            "- `DualTrendRawBreakevenGuardStrongRunnerStructureStrategy`: 当前主候选。保留 Raw + 保本 + guard 的基础，只在 `short_pullback_restart` 到 +5% 后，用结构条件挑出强趋势单继续拿。",
            "",
            "## 分策略逐年明细",
            "",
        ]
    )
    report_lines.extend(detail_blocks)

    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "row_type",
                "strategy_name",
                "strategy_file",
                "role",
                "sample_start",
                "sample_end",
                "trades",
                "profit_pct",
                "final_balance",
                "winrate",
                "profit_factor",
                "max_drawdown",
                "year",
                "start_balance",
                "end_balance",
                "profit_abs",
                "return_pct",
            ],
        )
        writer.writeheader()
        for row in overall_rows:
            writer.writerow({"row_type": "overall", **row})
        for row in yearly_rows:
            writer.writerow({"row_type": "year", **row})

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(report_path)
    print(csv_path)


if __name__ == "__main__":
    main()
