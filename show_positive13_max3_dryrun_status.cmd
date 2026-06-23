@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0show_positive13_max3_dryrun_status.ps1"
echo.
pause
