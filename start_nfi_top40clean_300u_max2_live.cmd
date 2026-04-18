@echo off
setlocal
cd /d "%~dp0"
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_nfi_top40clean_300u_max2_live.ps1"
pause
