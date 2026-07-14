import csv
import json
import zipfile
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path("user_data/analysis/pyramid_second_add_2026-07-13")
REPORT_PATH = Path("user_data/reports/dualtrend_second_add15_盈利单二次加仓实验_2026-07-13.md")

FILES = {
    "3y": "backtest-result-2026-07-13_04-46-06.zip",
    "1y": "backtest-result-2026-07-13_06-49-38.zip",
    "pressure": "backtest-result-2026-07-13_07-01-10.zip",
    "5y": "backtest-result-2026-07-13_07-35-27.zip",
}

BASELINE = "DualTrendPyramidCloseFloor07V1Strategy"
WINNER = "DualTrendPyramidSecondAdd15V1Strategy"


def load_result(zip_name: str) -> dict:
    with zipfile.ZipFile(BASE_DIR / zip_name) as zf:
        json_name = next(
            name for name in zf.namelist() if name.endswith(".json") and "_config" not in name
        )
        return json.loads(zf.read(json_name))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def row(label: str, strategy: str, result: dict) -> dict:
    entry_orders = 0
    trades_with_second_add = 0
    second_add_orders = 0
    for trade in result["trades"]:
        entries = [o for o in trade.get("orders", []) if o.get("ft_is_entry")]
        entry_orders += len(entries)
        if len(entries) >= 3:
            trades_with_second_add += 1
            second_add_orders += len(entries) - 2

    pullback = next(
        (item for item in result.get("results_per_enter_tag", []) if item.get("key") == "short_pullback_restart"),
        {},
    )
    return {
        "sample": label,
        "strategy": strategy,
        "timerange": result["timerange"],
        "trades": result["total_trades"],
        "profit_pct": round(result["profit_total"] * 100.0, 2),
        "profit_abs_usdt": round(result["profit_total_abs"], 3),
        "profit_factor": round(result["profit_factor"], 3),
        "winrate_pct": round(result["winrate"] * 100.0, 2),
        "max_dd_account_pct": round(result["max_drawdown_account"] * 100.0, 2),
        "max_dd_relative_pct": round(result["max_relative_drawdown"] * 100.0, 2),
        "pullback_profit_pct": round(float(pullback.get("profit_total", 0.0)) * 100.0, 2),
        "pullback_profit_abs_usdt": round(float(pullback.get("profit_total_abs", 0.0)), 3),
        "pullback_pf": round(float(pullback.get("profit_factor", 0.0)), 3),
        "entry_orders": entry_orders,
        "trades_with_second_add": trades_with_second_add,
        "second_add_orders": second_add_orders,
    }


def trade_key(trade: dict) -> tuple:
    return (
        trade["pair"],
        trade["open_date"],
        trade.get("enter_tag", ""),
        bool(trade.get("is_short", False)),
    )


def main() -> None:
    loaded = {label: load_result(filename) for label, filename in FILES.items()}

    summary_rows: list[dict] = []
    for label, data in loaded.items():
        for strategy, result in data["strategy"].items():
            if strategy in {BASELINE, WINNER}:
                summary_rows.append(row(label, strategy, result))

    summary_fields = [
        "sample",
        "strategy",
        "timerange",
        "trades",
        "profit_pct",
        "profit_abs_usdt",
        "profit_factor",
        "winrate_pct",
        "max_dd_account_pct",
        "max_dd_relative_pct",
        "pullback_profit_pct",
        "pullback_profit_abs_usdt",
        "pullback_pf",
        "entry_orders",
        "trades_with_second_add",
        "second_add_orders",
    ]
    write_csv(BASE_DIR / "second_add15_summary.csv", summary_rows, summary_fields)

    delta_rows: list[dict] = []
    pair_buckets: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "matched_trades": 0,
            "baseline_profit_abs": 0.0,
            "winner_profit_abs": 0.0,
            "delta_abs": 0.0,
            "improved": 0,
            "worsened": 0,
            "same": 0,
        }
    )

    for label in ("3y", "5y"):
        baseline = loaded[label]["strategy"][BASELINE]
        winner = loaded[label]["strategy"][WINNER]
        base_trades = {trade_key(t): t for t in baseline["trades"]}
        win_trades = {trade_key(t): t for t in winner["trades"]}
        for key in sorted(set(base_trades) & set(win_trades)):
            base_trade = base_trades[key]
            win_trade = win_trades[key]
            base_abs = float(base_trade["profit_abs"])
            win_abs = float(win_trade["profit_abs"])
            delta = win_abs - base_abs
            direction = "same"
            if delta > 1e-9:
                direction = "improved"
            elif delta < -1e-9:
                direction = "worsened"
            pair = base_trade["pair"]
            pair_key = f"{label}:{pair}"
            bucket = pair_buckets[pair_key]
            bucket["matched_trades"] += 1
            bucket["baseline_profit_abs"] += base_abs
            bucket["winner_profit_abs"] += win_abs
            bucket["delta_abs"] += delta
            bucket[direction] += 1
            delta_rows.append(
                {
                    "sample": label,
                    "pair": pair,
                    "open_date": base_trade["open_date"],
                    "enter_tag": base_trade.get("enter_tag", ""),
                    "baseline_profit_abs": round(base_abs, 3),
                    "winner_profit_abs": round(win_abs, 3),
                    "delta_abs": round(delta, 3),
                    "baseline_exit_reason": base_trade.get("exit_reason", ""),
                    "winner_exit_reason": win_trade.get("exit_reason", ""),
                    "direction": direction,
                    "winner_entry_order_count": len(
                        [o for o in win_trade.get("orders", []) if o.get("ft_is_entry")]
                    ),
                }
            )

    write_csv(
        BASE_DIR / "second_add15_trade_delta.csv",
        delta_rows,
        [
            "sample",
            "pair",
            "open_date",
            "enter_tag",
            "baseline_profit_abs",
            "winner_profit_abs",
            "delta_abs",
            "baseline_exit_reason",
            "winner_exit_reason",
            "direction",
            "winner_entry_order_count",
        ],
    )

    pair_rows = []
    for key, bucket in pair_buckets.items():
        sample, pair = key.split(":", 1)
        pair_rows.append(
            {
                "sample": sample,
                "pair": pair,
                "matched_trades": int(bucket["matched_trades"]),
                "baseline_profit_abs": round(bucket["baseline_profit_abs"], 3),
                "winner_profit_abs": round(bucket["winner_profit_abs"], 3),
                "delta_abs": round(bucket["delta_abs"], 3),
                "improved": int(bucket["improved"]),
                "worsened": int(bucket["worsened"]),
                "same": int(bucket["same"]),
            }
        )
    pair_rows.sort(key=lambda r: (r["sample"], -r["delta_abs"]))
    write_csv(
        BASE_DIR / "second_add15_pair_delta.csv",
        pair_rows,
        [
            "sample",
            "pair",
            "matched_trades",
            "baseline_profit_abs",
            "winner_profit_abs",
            "delta_abs",
            "improved",
            "worsened",
            "same",
        ],
    )

    by_sample = {
        (row["sample"], row["strategy"]): row
        for row in summary_rows
    }

    def fmt(sample: str, strategy: str) -> str:
        r = by_sample[(sample, strategy)]
        return (
            f"`{r['profit_pct']}% / PF {r['profit_factor']} / "
            f"MaxDD(account) {r['max_dd_account_pct']}% / Win {r['winrate_pct']}% / "
            f"{r['trades']} trades`"
        )

    winner_3y = by_sample[("3y", WINNER)]
    base_3y = by_sample[("3y", BASELINE)]
    winner_5y = by_sample[("5y", WINNER)]
    base_5y = by_sample[("5y", BASELINE)]

    report = f"""# SecondAdd15 盈利单二次加仓实验

## 结论

本轮有效候选是 `DualTrendPyramidSecondAdd15V1Strategy`。

它在 `DualTrendPyramidCloseFloor07V1Strategy` 的基础上，只做一件事：允许 `short_pullback_restart` 盈利单在已有第一腿加仓后，再出现同方向信号时做第二腿加仓。第一腿仍是初始仓位 `25%`，第二腿降为初始仓位 `15%`，第二腿触发窗口提高到 `1.8% - 3.5%` 浮盈。

这个版本没有修改入场逻辑、没有改币池、没有改 `max_open_trades`、没有改止损或止盈主逻辑。

## 回测对照

### 3 年 `20230618-20260618`

- CloseFloor07: {fmt('3y', BASELINE)}
- SecondAdd15: {fmt('3y', WINNER)}
- 增量：`+{round(winner_3y['profit_pct'] - base_3y['profit_pct'], 2)}%`，PF 小幅提升，账户回撤不变。

### 近 1 年 `20250618-20260618`

- CloseFloor07: {fmt('1y', BASELINE)}
- SecondAdd15: {fmt('1y', WINNER)}

### 压力期 `20260301-20260531`

- CloseFloor07: {fmt('pressure', BASELINE)}
- SecondAdd15: {fmt('pressure', WINNER)}

### 真实 5 年 `20210618-20260618`

- CloseFloor07: {fmt('5y', BASELINE)}
- SecondAdd15: {fmt('5y', WINNER)}
- 增量：`+{round(winner_5y['profit_pct'] - base_5y['profit_pct'], 2)}%`。

## 加仓行为

- 3 年 SecondAdd15 的二次加仓交易数：`{winner_3y['trades_with_second_add']}`。
- 5 年 SecondAdd15 的二次加仓交易数：`{winner_5y['trades_with_second_add']}`。
- 3 年 `short_pullback_restart` 收益从 `{base_3y['pullback_profit_pct']}%` 提到 `{winner_3y['pullback_profit_pct']}%`。
- 5 年 `short_pullback_restart` 收益从 `{base_5y['pullback_profit_pct']}%` 提到 `{winner_5y['pullback_profit_pct']}%`。

## 判断

- 第二腿加仓是有效的，但属于“小幅增强”，不是收益结构的大改造。
- 它没有放大压力期回撤，5 年也略微跑赢 CloseFloor07，因此可以保留为当前加仓主候选。
- `SecondAdd12` 和 `SecondAdd12Confirm` 没有提供额外优势，已从策略代码中删除。
- 这条线下一步更值得研究的是“第二腿触发后的坏加仓识别”，而不是继续提高第二腿仓位。

## 输出文件

- 汇总：`user_data/analysis/pyramid_second_add_2026-07-13/second_add15_summary.csv`
- 逐笔差异：`user_data/analysis/pyramid_second_add_2026-07-13/second_add15_trade_delta.csv`
- pair 差异：`user_data/analysis/pyramid_second_add_2026-07-13/second_add15_pair_delta.csv`
"""

    REPORT_PATH.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
