@echo off
echo 🚀 MT4 CALCULATOR - MAIN APPLICATION RUN
echo ========================================
echo.

cd "D:\D Drive\ULTIMATE CALCULATOR\mt4_refactored"

echo 📄 Checking for 10.htm file...
if exist "..\10.htm" (
    echo ✅ Found 10.htm file
    for %%A in ("..\10.htm") do echo 📏 File size: %%~zA bytes
) else (
    echo ❌ ERROR: 10.htm file not found!
    pause
    exit /b 1
)

echo.
echo 🔄 Running MT4 Calculator main application...
echo ========================================

python run_main_final.py

echo.
echo ========================================
echo ✅ MT4 Calculator main application completed!
echo 🎯 R-Multiple calculations use CLOSED TRADES ONLY
echo.

pause
