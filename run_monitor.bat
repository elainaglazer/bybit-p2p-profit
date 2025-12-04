@echo off
title Bybit P2P Monitor

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing required library 'requests'...
    pip install requests
)

echo Starting Monitor...
python bybit_p2p_monitor.py
pause