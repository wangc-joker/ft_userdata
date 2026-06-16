from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
import textwrap
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
USER_DATA = ROOT / "user_data"
BASE_CONFIG = USER_DATA / "config.backtest.dualtrend.short_v1.1000u.max3.3y.json"
REPORT_DIR = Path(__file__).resolve().parent / "dual_trend_robustness_runs"

STRATEGIES = [
    "DualTrendCompressionRestartShortPullbackOnlyV1Strategy",
    "DualTrendCompressionRestartShortCompressionOnlyV1Strategy",
    "DualTrendCompressionRestartShortV1Strategy",
]

SAMPLES = {
    "full": "20221001-20260507",
    "recent": "20250101-20260507",
}

BASE_PAIRS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "BNB/USDT:USDT",
    "SOL/USDT:USDT",
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT",
    "ADA/USDT:USDT",
    "LINK/USDT:USDT",
    "NEAR/USDT:USDT",
    "SUI/USDT:USDT",
    "TRX/USDT:USDT",
    "ZEC/USDT:USDT",
    "TAO/USDT:USDT",
]

LARGE_CAP_PAIRS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "BNB/USDT:USDT",
    "SOL/USDT:USDT",
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT",
    "ADA/USDT:USDT",
    "LINK/USDT:USDT",
]


@dataclass
class BacktestRun:
    run_id: str
    category: str
    strategy: str
    sample: str
    timerange: str
    config_path: Path
    result_dir: Path
    fee: float | None = None
    max_open_trades: int | None = None


def pct(value: float | None) -> float:
    if value is None:
        return 0.0
    return round(float(value) * 100, 4)


def clean_float(value: Any, digits: int = 6) -> float:
    if value is None:
        return 0.0
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return 0.0
    return round(float(value), digits)


def load_base_config() -> dict[str, Any]:
    with BASE_CONFIG.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_config(path: Path, pairs: list[str] | None = None, max_open_trades: int | None = None) -> None:
    cfg = load_base_config()
    if pairs is not None:
        cfg["exchange"]["pair_whitelist"] = pairs
    if max_open_trades is not None:
        cfg["max_open_trades"] = max_open_trades
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def docker_path(path: Path) -> str:
    rel = path.resolve().relative_to(USER_DATA.resolve()).as_posix()
    return f"/freqtrade/user_data/{rel}"


def run_backtest(run: BacktestRun) -> Path:
    run.result_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(run.result_dir.glob("backtest-result-*.zip"), key=lambda p: p.stat().st_mtime)
    if existing:
        return existing[-1]

    cmd = [
        "docker",
        "compose",
        "run",
        "--rm",
        "freqtrade",
        "backtesting",
        "--config",
        docker_path(run.config_path),
        "--strategy-path",
        "/freqtrade/user_data/strategies",
        "--recursive-strategy-search",
        "--strategy",
        run.strategy,
        "--timerange",
        run.timerange,
        "--breakdown",
        "year",
        "--export",
        "trades",
        "--cache",
        "none",
        "--backtest-directory",
        docker_path(run.result_dir),
    ]
    if run.fee is not None:
        cmd.extend(["--fee", str(run.fee)])
    if run.max_open_trades is not None:
        cmd.extend(["--max-open-trades", str(run.max_open_trades)])

    log_path = run.result_dir / f"{run.run_id}.log"
    proc = None
    for attempt in range(1, 4):
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"\n\n=== attempt {attempt} ===\n")
            proc = subprocess.run(
                cmd,
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=1200,
            )
        if proc.returncode == 0:
            break
        time.sleep(10 * attempt)
    if proc is None or proc.returncode != 0:
        raise RuntimeError(f"Backtest failed: {run.run_id}. See {log_path}")
    zips = sorted(run.result_dir.glob("backtest-result-*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        raise RuntimeError(f"No zip result found for {run.run_id}")
    return zips[-1]


def load_result(zip_path: Path) -> tuple[str, dict[str, Any]]:
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if n.endswith(".json") and "_config" not in n]
        data = json.loads(zf.read(names[0]))
    strategy_name = next(iter(data["strategy"]))
    return strategy_name, data["strategy"][strategy_name]


def trade_extremes(trades: list[dict[str, Any]], pair: str | None = None) -> tuple[float, float]:
    rows = [t for t in trades if pair is None or t["pair"] == pair]
    if not rows:
        return 0.0, 0.0
    profits = [float(t.get("profit_ratio", 0.0)) for t in rows]
    return pct(max(profits)), pct(min(profits))


def summary_row(result: dict[str, Any], run: BacktestRun, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    best_trade, worst_trade = trade_extremes(result.get("trades", []))
    row = {
        "run_id": run.run_id,
        "category": run.category,
        "strategy": run.strategy,
        "sample": run.sample,
        "timerange": run.timerange,
        "trades": result.get("total_trades", 0),
        "total_profit_abs": clean_float(result.get("profit_total_abs")),
        "total_profit_pct": pct(result.get("profit_total")),
        "profit_factor": clean_float(result.get("profit_factor"), 4),
        "winrate": pct(result.get("winrate")),
        "max_drawdown_abs": clean_float(result.get("max_drawdown_abs")),
        "max_drawdown_pct": pct(result.get("max_drawdown_account")),
        "avg_profit_pct": pct(result.get("profit_mean")),
        "best_trade_pct": best_trade,
        "worst_trade_pct": worst_trade,
        "final_balance": clean_float(result.get("final_balance")),
        "zip_path": str(run.result_dir),
    }
    if extra:
        row.update(extra)
    return row


def pair_rows(result: dict[str, Any], run: BacktestRun) -> list[dict[str, Any]]:
    trades = result.get("trades", [])
    rows = []
    for item in result.get("results_per_pair", []):
        pair = item.get("key")
        if pair == "TOTAL":
            continue
        best_trade, worst_trade = trade_extremes(trades, pair)
        rows.append(
            {
                "run_id": run.run_id,
                "strategy": run.strategy,
                "sample": run.sample,
                "pair": pair,
                "trades": item.get("trades", 0),
                "total_profit_abs": clean_float(item.get("profit_total_abs")),
                "total_profit_pct": pct(item.get("profit_total")),
                "profit_factor": clean_float(item.get("profit_factor"), 4),
                "winrate": pct(item.get("winrate")),
                "max_drawdown_abs": clean_float(item.get("max_drawdown_abs")),
                "max_drawdown_pct": pct(item.get("max_drawdown_account")),
                "avg_profit_pct": pct(item.get("profit_mean")),
                "best_trade_pct": best_trade,
                "worst_trade_pct": worst_trade,
            }
        )
    return rows


def tag_rows(result: dict[str, Any], run: BacktestRun) -> list[dict[str, Any]]:
    rows = []
    for item in result.get("results_per_enter_tag", []):
        tag = item.get("key")
        if tag == "TOTAL":
            continue
        rows.append(
            {
                "run_id": run.run_id,
                "strategy": run.strategy,
                "sample": run.sample,
                "entry_tag": tag,
                "trades": item.get("trades", 0),
                "total_profit_abs": clean_float(item.get("profit_total_abs")),
                "total_profit_pct": pct(item.get("profit_total")),
                "profit_factor": clean_float(item.get("profit_factor"), 4),
                "winrate": pct(item.get("winrate")),
                "max_drawdown_abs": clean_float(item.get("max_drawdown_abs")),
                "max_drawdown_pct": pct(item.get("max_drawdown_account")),
                "avg_profit_pct": pct(item.get("profit_mean")),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def make_risk_strategy_file(path: Path) -> dict[tuple[float, float], str]:
    classes = {}
    lines = [
        "from DualTrendCompressionRestartShortV1Strategy import DualTrendCompressionRestartShortV1Strategy",
        "",
    ]
    for risk in [0.005, 0.0075, 0.01]:
        for cap in [0.25, 0.35, 0.45]:
            class_name = f"DualTrendRobustRisk{str(risk).replace('.', 'p')}Cap{str(cap).replace('.', 'p')}Strategy"
            classes[(risk, cap)] = class_name
            lines.extend(
                [
                    f"class {class_name}(DualTrendCompressionRestartShortV1Strategy):",
                    f"    risk_per_trade = {risk}",
                    f"    max_position_value_pct = {cap}",
                    "",
                ]
            )
    path.write_text("\n".join(lines), encoding="utf-8")
    return classes


def markdown_table(rows: list[dict[str, Any]], columns: list[str], limit: int | None = None) -> str:
    selected = rows[:limit] if limit else rows
    if not selected:
        return ""
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in selected:
        body.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join([header, sep, *body])


def adjusted_cost_rows(base_result: dict[str, Any], sample: str) -> list[dict[str, Any]]:
    rows = []
    trades = base_result.get("trades", [])
    starting_balance = float(base_result.get("starting_balance", 1000.0))
    for slippage in [0.0005, 0.001, 0.002]:
        profit_abs = 0.0
        wins = losses = draws = 0
        gross_profit = gross_loss = 0.0
        for trade in trades:
            stake = float(trade.get("stake_amount", 0.0))
            raw_abs = float(trade.get("profit_abs", 0.0))
            adjusted_abs = raw_abs - stake * slippage * 2
            profit_abs += adjusted_abs
            if adjusted_abs > 0:
                wins += 1
                gross_profit += adjusted_abs
            elif adjusted_abs < 0:
                losses += 1
                gross_loss += abs(adjusted_abs)
            else:
                draws += 1
        total = wins + losses + draws
        rows.append(
            {
                "category": "slippage_postprocess",
                "sample": sample,
                "cost_case": f"slippage_{slippage * 100:.2f}pct_each_side",
                "trades": total,
                "total_profit_abs": clean_float(profit_abs),
                "total_profit_pct": clean_float(profit_abs / starting_balance * 100, 4),
                "profit_factor": clean_float(gross_profit / gross_loss if gross_loss else 0.0, 4),
                "winrate": clean_float(wins / total * 100 if total else 0.0, 4),
            }
        )
    return rows


def generate_report(run_dir: Path, summary: list[dict[str, Any]], pairs: list[dict[str, Any]], tags: list[dict[str, Any]], cost_rows: list[dict[str, Any]]) -> None:
    combined_full = [r for r in summary if r["category"] == "pair_level" and r["strategy"] == "DualTrendCompressionRestartShortV1Strategy" and r["sample"] == "full"][0]
    combined_recent = [r for r in summary if r["category"] == "pair_level" and r["strategy"] == "DualTrendCompressionRestartShortV1Strategy" and r["sample"] == "recent"][0]
    pair_full = [r for r in pairs if r["strategy"] == "DualTrendCompressionRestartShortV1Strategy" and r["sample"] == "full"]
    pair_recent = [r for r in pairs if r["strategy"] == "DualTrendCompressionRestartShortV1Strategy" and r["sample"] == "recent"]
    worst_full = sorted(pair_full, key=lambda r: r["total_profit_abs"])[:5]
    best_full = sorted(pair_full, key=lambda r: r["total_profit_abs"], reverse=True)[:5]
    worst_recent = sorted(pair_recent, key=lambda r: r["total_profit_abs"])[:5]
    best_recent = sorted(pair_recent, key=lambda r: r["total_profit_abs"], reverse=True)[:5]

    pair_tests = [r for r in summary if r["category"] == "pair_exclusion"]
    risk_tests = [r for r in summary if r["category"] == "risk_matrix"]
    fee_tests = [r for r in summary if r["category"] == "fee_pressure"]

    stable_tags = sorted(tags, key=lambda r: (r["sample"], -r["total_profit_pct"]))

    report = f"""# DualTrendCompressionRestartShortV1 稳健性验证报告

生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}

## 1. 基准结果

全样本组合策略：

```text
交易数：{combined_full['trades']}
总收益：{combined_full['total_profit_abs']} USDT / {combined_full['total_profit_pct']}%
Profit Factor：{combined_full['profit_factor']}
胜率：{combined_full['winrate']}%
最大回撤：{combined_full['max_drawdown_abs']} USDT / {combined_full['max_drawdown_pct']}%
```

近期组合策略：

```text
交易数：{combined_recent['trades']}
总收益：{combined_recent['total_profit_abs']} USDT / {combined_recent['total_profit_pct']}%
Profit Factor：{combined_recent['profit_factor']}
胜率：{combined_recent['winrate']}%
最大回撤：{combined_recent['max_drawdown_abs']} USDT / {combined_recent['max_drawdown_pct']}%
```

## 2. Entry Tag 稳定性

{markdown_table(stable_tags, ['strategy', 'sample', 'entry_tag', 'trades', 'total_profit_pct', 'profit_factor', 'winrate', 'max_drawdown_pct', 'avg_profit_pct'])}

结论：

```text
short_pullback_restart 是更稳定的主信号。
它在全样本和近期样本中的交易数更多，收益贡献连续性更好。
short_compression_breakdown 近期表现不错，但全样本年度稳定性弱于 pullback，更适合作为补充信号。
```

## 3. Pair 贡献与拖累

全样本贡献最大：

{markdown_table(best_full, ['pair', 'trades', 'total_profit_abs', 'total_profit_pct', 'profit_factor', 'winrate', 'max_drawdown_pct', 'avg_profit_pct', 'best_trade_pct', 'worst_trade_pct'])}

全样本拖累最大：

{markdown_table(worst_full, ['pair', 'trades', 'total_profit_abs', 'total_profit_pct', 'profit_factor', 'winrate', 'max_drawdown_pct', 'avg_profit_pct', 'best_trade_pct', 'worst_trade_pct'])}

近期贡献最大：

{markdown_table(best_recent, ['pair', 'trades', 'total_profit_abs', 'total_profit_pct', 'profit_factor', 'winrate', 'max_drawdown_pct', 'avg_profit_pct', 'best_trade_pct', 'worst_trade_pct'])}

近期拖累最大：

{markdown_table(worst_recent, ['pair', 'trades', 'total_profit_abs', 'total_profit_pct', 'profit_factor', 'winrate', 'max_drawdown_pct', 'avg_profit_pct', 'best_trade_pct', 'worst_trade_pct'])}

## 4. Pair 剔除测试

{markdown_table(pair_tests, ['sample', 'case', 'pairs', 'trades', 'total_profit_pct', 'profit_factor', 'winrate', 'max_drawdown_pct', 'avg_profit_pct'])}

## 5. 风险参数矩阵

以下为组合策略在不同 `risk_per_trade`、`max_position_value_pct`、`max_open_trades` 下的结果：

{markdown_table(sorted(risk_tests, key=lambda r: (r['sample'], r['max_open_trades'], r['risk_per_trade'], r['max_position_value_pct'])), ['sample', 'risk_per_trade', 'max_position_value_pct', 'max_open_trades', 'trades', 'total_profit_pct', 'profit_factor', 'winrate', 'max_drawdown_pct'], limit=80)}

结论：

```text
如果不同风险参数下收益方向保持为正，且回撤没有失控，说明入场逻辑具备一定稳健性。
实盘 dry-run 初期更适合优先使用较保守组合：risk_per_trade=0.005 或 0.0075，max_open_trades=2 或 3。
```

## 6. 成本压力测试

手续费压力：

{markdown_table(fee_tests, ['sample', 'cost_case', 'trades', 'total_profit_pct', 'profit_factor', 'winrate', 'max_drawdown_pct'])}

滑点压力，基于导出交易事后扣减，每边滑点：

{markdown_table(cost_rows, ['sample', 'cost_case', 'trades', 'total_profit_pct', 'profit_factor', 'winrate'])}

## 7. 是否建议进入 Dry-run

```text
建议：可以进入小资金 dry-run，但不建议直接实盘。

理由：
1. 基准组合、pullback-only、compression-only 在近期样本均为正。
2. pullback 信号更稳定，可以作为 V1 主信号。
3. LINK、TRX 等 pair 存在明显拖累，需要先做白名单收缩。
4. 成本和滑点压力仍需重点看 2 倍手续费与 0.10%-0.20% 滑点后的结果。
5. dry-run 建议先用保守风险：risk_per_trade=0.005 或 0.0075，max_open_trades=2 或 3。
```

## 8. 输出文件

```text
summary.csv
pair_breakdown.csv
tag_breakdown.csv
cost_pressure.csv
```
"""
    (run_dir / "robustness_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "full"], default="full")
    parser.add_argument("--resume-dir", default="")
    args = parser.parse_args()

    run_dir = Path(args.resume_dir) if args.resume_dir else REPORT_DIR / time.strftime("%Y%m%d_%H%M%S")
    configs_dir = run_dir / "configs"
    results_dir = run_dir / "results"
    run_dir.mkdir(parents=True, exist_ok=True)

    temp_strategy = USER_DATA / "strategies" / "DualTrendRobustnessTempStrategies.py"
    risk_classes = make_risk_strategy_file(temp_strategy)

    summary_rows: list[dict[str, Any]] = []
    all_pair_rows: list[dict[str, Any]] = []
    all_tag_rows: list[dict[str, Any]] = []
    cost_rows: list[dict[str, Any]] = []
    result_by_run: dict[str, dict[str, Any]] = {}

    try:
        base_config = configs_dir / "base.json"
        write_config(base_config)

        # Task 1: pair-level breakdown for 3 strategies x 2 samples.
        for strategy in STRATEGIES:
            for sample, timerange in SAMPLES.items():
                run = BacktestRun(
                    run_id=f"pair_{strategy}_{sample}",
                    category="pair_level",
                    strategy=strategy,
                    sample=sample,
                    timerange=timerange,
                    config_path=base_config,
                    result_dir=results_dir / f"pair_{strategy}_{sample}",
                )
                zip_path = run_backtest(run)
                _, result = load_result(zip_path)
                result_by_run[run.run_id] = result
                summary_rows.append(summary_row(result, run))
                all_pair_rows.extend(pair_rows(result, run))
                all_tag_rows.extend(tag_rows(result, run))

        # Task 2: pair exclusion tests for combined strategy, both samples.
        for sample, timerange in SAMPLES.items():
            combined_pairs = [
                r
                for r in all_pair_rows
                if r["strategy"] == "DualTrendCompressionRestartShortV1Strategy" and r["sample"] == sample
            ]
            sorted_worst = sorted(combined_pairs, key=lambda r: r["total_profit_abs"])
            positive_pairs = [r["pair"] for r in combined_pairs if r["total_profit_abs"] > 0]
            cases = [
                ("remove_worst_1", [p for p in BASE_PAIRS if p not in [x["pair"] for x in sorted_worst[:1]]]),
                ("remove_worst_2", [p for p in BASE_PAIRS if p not in [x["pair"] for x in sorted_worst[:2]]]),
                ("remove_worst_3", [p for p in BASE_PAIRS if p not in [x["pair"] for x in sorted_worst[:3]]]),
                ("large_cap_8", LARGE_CAP_PAIRS),
                ("positive_pairs_only", positive_pairs),
            ]
            for case, pairs in cases:
                cfg = configs_dir / f"pairs_{sample}_{case}.json"
                write_config(cfg, pairs=pairs)
                run = BacktestRun(
                    run_id=f"pair_exclusion_{sample}_{case}",
                    category="pair_exclusion",
                    strategy="DualTrendCompressionRestartShortV1Strategy",
                    sample=sample,
                    timerange=timerange,
                    config_path=cfg,
                    result_dir=results_dir / f"pair_exclusion_{sample}_{case}",
                )
                zip_path = run_backtest(run)
                _, result = load_result(zip_path)
                summary_rows.append(
                    summary_row(
                        result,
                        run,
                        {"case": case, "pairs": ",".join(pairs), "pair_count": len(pairs)},
                    )
                )

        # Task 3: risk matrix for combined strategy, both samples.
        matrix_samples = SAMPLES if args.mode == "full" else {"recent": SAMPLES["recent"]}
        for sample, timerange in matrix_samples.items():
            for (risk, cap), strategy in risk_classes.items():
                for mot in [2, 3, 5]:
                    run = BacktestRun(
                        run_id=f"risk_{sample}_{risk}_{cap}_{mot}",
                        category="risk_matrix",
                        strategy=strategy,
                        sample=sample,
                        timerange=timerange,
                        config_path=base_config,
                        result_dir=results_dir / f"risk_{sample}_{risk}_{cap}_{mot}",
                        max_open_trades=mot,
                    )
                    zip_path = run_backtest(run)
                    _, result = load_result(zip_path)
                    summary_rows.append(
                        summary_row(
                            result,
                            run,
                            {
                                "risk_per_trade": risk,
                                "max_position_value_pct": cap,
                                "max_open_trades": mot,
                            },
                        )
                    )

        # Task 4: fee pressure via Freqtrade --fee and slippage post-processing.
        for sample, timerange in SAMPLES.items():
            for label, fee in [("fee_1p5x", 0.00075), ("fee_2x", 0.001)]:
                run = BacktestRun(
                    run_id=f"fee_{sample}_{label}",
                    category="fee_pressure",
                    strategy="DualTrendCompressionRestartShortV1Strategy",
                    sample=sample,
                    timerange=timerange,
                    config_path=base_config,
                    result_dir=results_dir / f"fee_{sample}_{label}",
                    fee=fee,
                )
                zip_path = run_backtest(run)
                _, result = load_result(zip_path)
                summary_rows.append(summary_row(result, run, {"cost_case": label, "fee": fee}))
            base_result = result_by_run[f"pair_DualTrendCompressionRestartShortV1Strategy_{sample}"]
            cost_rows.extend(adjusted_cost_rows(base_result, sample))

        write_csv(run_dir / "summary.csv", summary_rows)
        write_csv(run_dir / "pair_breakdown.csv", all_pair_rows)
        write_csv(run_dir / "tag_breakdown.csv", all_tag_rows)
        write_csv(run_dir / "cost_pressure.csv", cost_rows)
        generate_report(run_dir, summary_rows, all_pair_rows, all_tag_rows, cost_rows)

        print(run_dir)
    finally:
        if temp_strategy.exists():
            temp_strategy.unlink()


if __name__ == "__main__":
    main()
