@echo off
setlocal
cd /d "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0show_nfi_top40clean_300u_max2_live_status.ps1"
endlocal
