@echo off
echo Starting MT4 Risk Management Calculator...
echo.

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Start the server
cd mt4_fastapi_backend
python main.py

:: Deactivate virtual environment when server stops
call deactivate
