@echo off
echo ==============================================
echo   MT4 Calculator - Integrated App Launcher
echo ==============================================
echo.
echo Starting MT4 Calculator on port 5501...
echo Frontend and API will be available at:
echo   http://localhost:5501
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "D:\D Drive\ULTIMATE CALCULATOR\mt4_fastapi_backend"
call "D:\D Drive\ULTIMATE CALCULATOR\ult_trz\Scripts\activate.bat"

echo Backend starting with integrated frontend...
python main.py

pause
