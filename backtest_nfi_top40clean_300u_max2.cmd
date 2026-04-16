@echo off
setlocal
cd /d "%~dp0"

docker compose run --rm freqtrade backtesting --config /freqtrade/user_data/config.backtest.nfi.top40clean.300u.max2.json --strategy NostalgiaForInfinityX7 --timerange 20251016-20260416 --export none

echo.
pause
