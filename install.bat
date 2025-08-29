@echo off
echo Installing MT4 Risk Management Calculator...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8 or higher.
    echo Visit https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
cd mt4_fastapi_backend
pip install -r requirements.txt
cd ..

echo.
echo Installation complete!
echo.
echo To start the application:
echo 1. Run 'start.bat'
echo 2. Open your browser and go to http://localhost:5501
echo.
pause
