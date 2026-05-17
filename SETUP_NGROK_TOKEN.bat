@echo off
chcp 65001 >nul
title 🔑 Setup ngrok Token

echo.
echo ============================================================
echo 🔑 NGROK TOKEN SETUP
echo ============================================================
echo.
echo To use ngrok, you need a free account and authtoken.
echo.
echo 📋 Steps:
echo 1. Go to: https://dashboard.ngrok.com/signup
echo 2. Sign up for a FREE account
echo 3. Copy your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
echo 4. Paste it below
echo.
echo ============================================================
echo.

set /p TOKEN="Enter your ngrok authtoken: "

if "%TOKEN%"=="" (
    echo.
    echo ❌ No token entered!
    pause
    exit /b 1
)

echo.
echo Setting up authtoken...
ngrok config add-authtoken %TOKEN%

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo ✅ SUCCESS! Token configured successfully!
    echo ============================================================
    echo.
    echo Now you can run: NGROK_SIMPLE.bat
    echo.
) else (
    echo.
    echo ❌ Failed to configure token
    echo.
)

pause
