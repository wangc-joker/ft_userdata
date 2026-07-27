@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0show_positive13_longmicro_observation_status.ps1"
echo.
pause
