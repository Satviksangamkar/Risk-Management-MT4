@echo off
echo Starting MT4 Calculator...
echo Working Directory: %CD%
echo Python Path: %PYTHONPATH%

cd "D:\D Drive\ULTIMATE CALCULATOR"

echo.
echo Testing Python version...
python --version

echo.
echo Running MT4 Calculator package...
python -m mt4_refactored

echo.
echo MT4 Calculator completed.
pause
