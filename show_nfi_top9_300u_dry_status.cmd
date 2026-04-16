@echo off
setlocal
cd /d "%~dp0"
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0show_nfi_top9_300u_dry_status.ps1"
endlocal
