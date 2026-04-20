@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto_recover_nfi_dynamic_top40_302u_max2_live.ps1"
endlocal
