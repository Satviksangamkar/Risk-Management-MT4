@echo off
echo MT4 Risk Management Calculator - Automatic GitHub Upload
echo ======================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8 or higher.
    echo Visit https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if the upload script exists
if not exist auto_upload_to_github.py (
    echo Upload script not found: auto_upload_to_github.py
    pause
    exit /b 1
)

:: Install required Python packages
echo Installing required packages...
pip install requests

:: Run the upload script
echo.
echo Starting automatic upload...
python auto_upload_to_github.py

echo.
echo Upload process completed.
pause
