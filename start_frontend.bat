@echo off
echo Starting MT4 Frontend Server...
cd /d "D:\D Drive\ULTIMATE CALCULATOR\mt4_frontend"
call "D:\D Drive\ULTIMATE CALCULATOR\ult_trz\Scripts\activate.bat"
python -m http.server 8080
pause
