@echo off
chcp 65001 >nul
title 🎬 Simple Netflux

echo.
echo ============================================================
echo 🎬 SIMPLE NETFLUX - Netflix Clone
echo ============================================================
echo.

REM Check Flask installation
echo 📦 Checking Flask...
py -c "import flask" 2>nul
if errorlevel 1 (
    echo ❌ Flask not installed!
    echo 📥 Installing Flask...
    py -m pip install flask
    if errorlevel 1 (
        echo ❌ Failed to install Flask!
        echo Please run: py -m pip install flask
        pause
        exit /b 1
    )
    echo ✅ Flask installed successfully!
)

echo ✅ Flask is ready!
echo.
echo 🚀 Starting Simple Netflux...
echo.
echo 📋 Server will show network addresses for other devices
echo 💡 Share the network address with other devices on same WiFi
echo.
echo ============================================================

py simple_netflux.py

pause