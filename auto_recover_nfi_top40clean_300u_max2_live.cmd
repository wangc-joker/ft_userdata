@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto_recover_nfi_top40clean_300u_max2_live.ps1"
endlocal
