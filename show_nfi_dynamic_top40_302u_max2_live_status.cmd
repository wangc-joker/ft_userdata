@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0show_nfi_dynamic_top40_302u_max2_live_status.ps1"
echo.
pause
