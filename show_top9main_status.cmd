@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0user_data\show_top9main_live_status.ps1" %*

endlocal
