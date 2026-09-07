@echo off
setlocal
cd /d "%~dp0"

title Cold Wallets - Online Watch-Only Coordinator
echo Cold Wallets online watch-only coordinator
echo.
echo This launcher does not elevate privileges, install packages, start Tor,
echo manipulate network adapters, access keys, or start signing tools.
echo Real broadcast remains disabled pending controlled validation.
echo.

set "PYTHON=C:\Python314\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"

"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found. Install a reviewed supported version manually.
    exit /b 1
)

echo Dashboard: http://127.0.0.1:8888
echo Press Ctrl+C to stop the foreground process.
"%PYTHON%" -B dashboard\server.py
exit /b %errorlevel%
