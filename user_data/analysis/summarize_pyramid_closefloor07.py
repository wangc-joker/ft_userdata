import csv
import json
import zipfile
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path("user_data/analysis/pyramid_risk_budget_2026-07-10")

FILES = {
    "3y_baseline": "backtest-result-2026-07-10_04-34-12.zip",
    "3y_nopyramid": "backtest-result-2026-07-10_04-49-34.zip",
    "3y_closefloor07": "backtest-result-2026-07-10_05-02-00.zip",
    "1y_closefloor07": "backtest-result-2026-07-10_05-07-50.zip",
    "pressure_closefloor07": "backtest-result-2026-07-10_05-09-19.zip",
    "5y_compare": "backtest-result-2026-07-10_06-57-25.zip",
    "3y_closefloor07_fee_1p5x": "backtest-result-2026-07-10_07-08-00.zip",
    "3y_closefloor07_fee_2x": "backtest-result-2026-07-10_07-14-35.zip",
}


def load_zip_result(zip_name: str) -> dict:
    path = BASE_DIR / zip_name
    with zipfile.ZipFile(path) as zf:
        json_name = next(
            name for name in zf.namelist() if name.endswith(".json") and "_config" not in name
        )
        return json.loads(zf.read(json_name))


def pct(value: float) -> float:
    return round(value * 100.0, 2)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def trade_key(trade: dict) -> tuple:
    return (
        trade["pair"],
        trade["open_date"],
        trade.get("enter_tag", ""),
        bool(trade.get("is_short", False)),
    )


def main() -> None:
    loaded = {label: load_zip_result(name) for label, name in FILES.items()}

    summary_rows: list[dict] = []
    for label, data in loaded.items():
        for strategy_name, result in data["strategy"].items():
            summary_rows.append(
                {
                    "label": label,
                    "strategy": strategy_name,
                    "timerange": result["timerange"],
                    "trades": result["total_trades"],
                    "profit_pct": round(result["profit_total"] * 100.0, 2),
                    "profit_abs_usdt": round(result["profit_total_abs"], 3),
                    "profit_factor": round(result["profit_factor"], 3),
                    "winrate_pct": round(result["winrate"] * 100.0, 2),
                    "max_dd_account_pct": round(result["max_drawdown_account"] * 100.0, 2),
                    "max_dd_relative_pct": round(result["max_relative_drawdown"] * 100.0, 2),
                    "avg_holding": result["holding_avg"],
                    "rejected_signals": result["rejected_signals"],
                }
            )
    write_csv(
        BASE_DIR / "closefloor07_experiment_summary.csv",
        summary_rows,
        [
            "label",
            "strategy",
            "timerange",
            "trades",
            "profit_pct",
            "profit_abs_usdt",
            "profit_factor",
            "winrate_pct",
            "max_dd_account_pct",
            "max_dd_relative_pct",
            "avg_holding",
            "rejected_signals",
        ],
    )

    compare_5y = loaded["5y_compare"]["strategy"]
    yearly_rows: list[dict] = []
    for strategy_name, result in compare_5y.items():
        for item in result["periodic_breakdown"]["year"]:
            yearly_rows.append(
                {
                    "strategy": strategy_name,
                    "year_bucket_end": item["date"],
                    "trades": item["trades"],
                    "wins": item["wins"],
                    "losses": item["losses"],
                    "profit_abs_usdt": round(item["profit_abs"], 3),
                    "profit_factor": round(item["profit_factor"], 3),
                }
            )
    write_csv(
        BASE_DIR / "closefloor07_5y_yearly.csv",
        yearly_rows,
        ["strategy", "year_bucket_end", "trades", "wins", "losses", "profit_abs_usdt", "profit_factor"],
    )

    baseline_3y = next(iter(loaded["3y_baseline"]["strategy"].values()))
    winner_3y = next(iter(loaded["3y_closefloor07"]["strategy"].values()))
    baseline_trades = {trade_key(trade): trade for trade in baseline_3y["trades"]}
    winner_trades = {trade_key(trade): trade for trade in winner_3y["trades"]}
    common_keys = sorted(set(baseline_trades) & set(winner_trades))

    trade_delta_rows: list[dict] = []
    pair_buckets: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "matched_trades": 0,
            "baseline_profit_abs": 0.0,
            "winner_profit_abs": 0.0,
            "delta_abs": 0.0,
            "improved_count": 0,
            "worsened_count": 0,
            "same_count": 0,
        }
    )
    improved = 0
    worsened = 0
    unchanged = 0

    for key in common_keys:
        base_trade = baseline_trades[key]
        win_trade = winner_trades[key]
        base_abs = float(base_trade["profit_abs"])
        win_abs = float(win_trade["profit_abs"])
        delta_abs = win_abs - base_abs
        if delta_abs > 1e-9:
            direction = "improved"
            improved += 1
        elif delta_abs < -1e-9:
            direction = "worsened"
            worsened += 1
        else:
            direction = "same"
            unchanged += 1

        pair = base_trade["pair"]
        bucket = pair_buckets[pair]
        bucket["matched_trades"] += 1
        bucket["baseline_profit_abs"] += base_abs
        bucket["winner_profit_abs"] += win_abs
        bucket["delta_abs"] += delta_abs
        bucket[f"{direction}_count"] += 1

        trade_delta_rows.append(
            {
                "pair": pair,
                "open_date": base_trade["open_date"],
                "enter_tag": base_trade.get("enter_tag", ""),
                "baseline_profit_abs": round(base_abs, 3),
                "winner_profit_abs": round(win_abs, 3),
                "delta_abs": round(delta_abs, 3),
                "baseline_exit_reason": base_trade.get("exit_reason", ""),
                "winner_exit_reason": win_trade.get("exit_reason", ""),
                "direction": direction,
            }
        )

    write_csv(
        BASE_DIR / "closefloor07_3y_trade_delta.csv",
        trade_delta_rows,
        [
            "pair",
            "open_date",
            "enter_tag",
            "baseline_profit_abs",
            "winner_profit_abs",
            "delta_abs",
            "baseline_exit_reason",
            "winner_exit_reason",
            "direction",
        ],
    )

    pair_delta_rows: list[dict] = []
    for pair, bucket in sorted(pair_buckets.items(), key=lambda item: item[1]["delta_abs"], reverse=True):
        pair_delta_rows.append(
            {
                "pair": pair,
                "matched_trades": int(bucket["matched_trades"]),
                "baseline_profit_abs": round(bucket["baseline_profit_abs"], 3),
                "winner_profit_abs": round(bucket["winner_profit_abs"], 3),
                "delta_abs": round(bucket["delta_abs"], 3),
                "improved_count": int(bucket["improved_count"]),
                "worsened_count": int(bucket["worsened_count"]),
                "same_count": int(bucket["same_count"]),
            }
        )
    write_csv(
        BASE_DIR / "closefloor07_3y_pair_delta.csv",
        pair_delta_rows,
        [
            "pair",
            "matched_trades",
            "baseline_profit_abs",
            "winner_profit_abs",
            "delta_abs",
            "improved_count",
            "worsened_count",
            "same_count",
        ],
    )

    nopyramid_3y = next(iter(loaded["3y_nopyramid"]["strategy"].values()))
    candidate_5y = compare_5y["DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy"]
    winner_5y = compare_5y["DualTrendPyramidCloseFloor07V1Strategy"]
    fee_1p5 = next(iter(loaded["3y_closefloor07_fee_1p5x"]["strategy"].values()))
    fee_2x = next(iter(loaded["3y_closefloor07_fee_2x"]["strategy"].values()))

    report = f"""# CloseFloor07 加仓过滤实验总结

## 结论

- 当前有效增厚点只有一条：在原主候选的加仓逻辑上，增加 `close_position >= 0.07`，避免在极端收低的 flush K 上继续加仓。
- 这条过滤在近三年是正收益增强：`+193.31% / PF 2.66 / MaxDD(account) 4.83%`，优于原候选 `+191.75% / PF 2.60 / MaxDD(account) 5.03%`。
- 但拉到真实 5 年后，它不是全面更优：原候选 `+252.14%`，CloseFloor07 `+250.64%`。PF 更高一些，但总收益略低，说明它主要改善的是近三年，不是全周期无条件增强。
- 前面验证过的风险预算 / 结构化加仓退出分支都不如主线，已经从策略代码里清掉，只保留分析结果。

## 关键回测

### 3 年主对照

- 原候选 `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`
  - `20230618-20260618`
  - `313 trades`
  - `+191.75%`
  - `PF 2.60`
  - `Winrate 50.80%`
  - `MaxDD(account) 5.03%`
- 新候选 `DualTrendPyramidCloseFloor07V1Strategy`
  - `20230618-20260618`
  - `313 trades`
  - `+193.31%`
  - `PF 2.66`
  - `Winrate 51.12%`
  - `MaxDD(account) 4.83%`
- 无加仓对照 `DualTrendCompressionCloseQualityGuard028CompressionTightStopStrategy`
  - `20230618-20260618`
  - `317 trades`
  - `+171.09%`
  - `PF 2.51`
  - `Winrate 49.84%`
  - `MaxDD(account) 5.00%`

### 近 1 年与压力期

- CloseFloor07 `20250618-20260618`
  - `123 trades`
  - `+67.56%`
  - `PF 3.38`
  - `Winrate 56.10%`
  - `MaxDD(account) 4.75%`
- CloseFloor07 `20260301-20260531`
  - `15 trades`
  - `+4.82%`
  - `PF 2.96`
  - `Winrate 40.00%`
  - `MaxDD(account) 1.75%`

### 真实 5 年

- 原候选 `DualTrendCompressionCloseQualityGuard028PyramidWindow05To15LegBe015Strategy`
  - `20210618-20260618`
  - `477 trades`
  - `+252.14%`
  - `PF 2.35`
  - `Winrate 51.15%`
  - `MaxDD(account) 5.02%`
- CloseFloor07 `DualTrendPyramidCloseFloor07V1Strategy`
  - `20210618-20260618`
  - `477 trades`
  - `+250.64%`
  - `PF 2.38`
  - `Winrate 51.36%`
  - `MaxDD(account) 4.82%`

## 5 年按年观察

- 2021 年尾段和 2022 年，CloseFloor07 比原候选更弱。
- 2023 年以后，CloseFloor07 整体更稳，主要收益增强发生在 2024-2026 这段。
- 这说明它更像“近年市场结构适配增强”，还不能直接下结论为全周期主替换。

## 3 年逐笔差异

- 完全匹配交易数：`{len(common_keys)}`
- 改善笔数：`{improved}`
- 变差笔数：`{worsened}`
- 不变笔数：`{unchanged}`
- 3 年总增量：`{round(winner_3y["profit_total_abs"] - baseline_3y["profit_total_abs"], 3)} USDT`

按实验逻辑看，这条过滤不是大幅改造，而是少做了一些“已经收在极低位、继续向下挤压”的二次加仓。收益提升不大，但回撤也同步变浅，属于比较干净的小修正。

## 成本压力

- CloseFloor07 3 年，手续费 `1.5x`:
  - `+176.56%`
  - `PF 2.48`
  - `MaxDD(account) 6.09%`
- CloseFloor07 3 年，手续费 `2x`:
  - `+165.90%`
  - `PF 2.33`
  - `MaxDD(account) 6.26%`

成本升高后收益会下台阶，但没有塌，说明这条过滤不是纯靠摩擦很低才成立。

## 本轮判断

- 如果目标是“近三年主线更厚、更稳”，CloseFloor07 值得保留为当前加仓主候选。
- 如果目标是“全 5 年绝对收益最高”，它暂时还不能完全替掉原候选，因为 5 年总收益略低。
- 更准确的定位是：
  - 原候选：全周期收益上限略高。
  - CloseFloor07：近三年更稳、PF 更高、回撤更低。
- 下一步继续研究“盈利单再开第二笔”的话，建议基于 CloseFloor07 往前走，因为它的加仓位置质量已经比原版本更干净。

## 输出文件

- 汇总表：`user_data/analysis/pyramid_risk_budget_2026-07-10/closefloor07_experiment_summary.csv`
- 5 年按年：`user_data/analysis/pyramid_risk_budget_2026-07-10/closefloor07_5y_yearly.csv`
- 3 年按 pair 差异：`user_data/analysis/pyramid_risk_budget_2026-07-10/closefloor07_3y_pair_delta.csv`
- 3 年逐笔差异：`user_data/analysis/pyramid_risk_budget_2026-07-10/closefloor07_3y_trade_delta.csv`
"""

    report_path = Path("user_data/reports/dualtrend_closefloor07_加仓过滤实验总结_2026-07-10.md")
    report_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
