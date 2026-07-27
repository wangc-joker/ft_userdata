@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_positive13_longmicro_observation_report.ps1" -Mode full
echo.
pause
