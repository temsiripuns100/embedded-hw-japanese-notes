@echo off
title Smart Tourist Photo Kiosk
cd /d "%~dp0"
echo ========================================================
echo        Smart Tourist Photo Kiosk (PoC Prototype)
echo   Face Recognition & Instant Photo Printing Kiosk
echo ========================================================
echo.
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Error] An error occurred while launching the Kiosk app.
    pause
)
