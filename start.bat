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

if not defined COLD_WALLETS_PYTHON (
    echo [ERROR] Set COLD_WALLETS_PYTHON to an explicitly reviewed virtualenv python.exe.
    exit /b 1
)
set "PYTHON=%COLD_WALLETS_PYTHON%"
if not defined COLD_WALLETS_PORT set "COLD_WALLETS_PORT=8888"

if not exist "%PYTHON%" (
    echo [ERROR] The configured Python executable does not exist.
    exit /b 1
)
"%PYTHON%" -c "import sys; raise SystemExit(0 if sys.prefix != sys.base_prefix else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] COLD_WALLETS_PYTHON must reference an active isolated virtualenv.
    exit /b 1
)

echo Dashboard: http://127.0.0.1:%COLD_WALLETS_PORT%
echo Press Ctrl+C to stop the foreground process.
"%PYTHON%" -B dashboard\server.py
exit /b %errorlevel%
