@echo off
echo MT4 Risk Management Calculator - Setup Test
echo =========================================
echo.

:: Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
) else (
    echo [PASS] Python is installed.
)

:: Check required directories
echo.
echo Checking required directories...
if not exist mt4_fastapi_backend (
    echo [FAIL] Backend directory not found.
    pause
    exit /b 1
) else (
    echo [PASS] Backend directory found.
)

if not exist mt4_frontend (
    echo [FAIL] Frontend directory not found.
    pause
    exit /b 1
) else (
    echo [PASS] Frontend directory found.
)

:: Check required files
echo.
echo Checking required files...
if not exist mt4_fastapi_backend\main.py (
    echo [FAIL] Backend main.py not found.
    pause
    exit /b 1
) else (
    echo [PASS] Backend main.py found.
)

if not exist mt4_frontend\index.html (
    echo [FAIL] Frontend index.html not found.
    pause
    exit /b 1
) else (
    echo [PASS] Frontend index.html found.
)

if not exist mt4_fastapi_backend\requirements.txt (
    echo [FAIL] Backend requirements.txt not found.
    pause
    exit /b 1
) else (
    echo [PASS] Backend requirements.txt found.
)

:: Check for Git
echo.
echo Checking Git installation...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Git not found. You will not be able to use the upload script.
) else (
    echo [PASS] Git is installed.
)

:: Summary
echo.
echo =========================================
echo Setup Test Complete!
echo.
echo Your system is ready to run the MT4 Risk Management Calculator.
echo.
echo Next steps:
echo 1. Run 'install.bat' to set up the virtual environment
echo 2. Run 'start.bat' to start the application
echo 3. Open your browser and go to http://localhost:5501
echo.
echo To upload to GitHub, run 'upload_to_github.bat'
echo.
pause
