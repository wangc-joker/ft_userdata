@echo off
set "SECRETS_PATH=%~1"
if "%SECRETS_PATH%"=="" set "SECRETS_PATH=D:\secure\secret_bin.json"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_top9main_test_live.ps1" "%SECRETS_PATH%"
