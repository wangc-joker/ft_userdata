@echo off
setlocal
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0update_nfi_dynamic_top40_302u.ps1"
echo.
pause
