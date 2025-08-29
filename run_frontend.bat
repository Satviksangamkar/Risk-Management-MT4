@echo off
echo Starting MT4 Frontend Server...
echo.
echo This will start a local web server for the MT4 Frontend
echo Make sure your MT4 Backend is running on http://localhost:8000
echo.

cd mt4_frontend

echo Starting Python HTTP server on port 8080...
echo Open your browser and navigate to: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.

python -m http.server 8080
