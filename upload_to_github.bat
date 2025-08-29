@echo off
echo MT4 Risk Management Calculator - GitHub Upload Script
echo =================================================
echo.

:: Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git not found. Please install Git.
    echo Visit https://git-scm.com/downloads
    pause
    exit /b 1
)

:: Configure Git if needed
set /p username="Enter your GitHub username: "
git config user.name "%username%"

set /p email="Enter your GitHub email: "
git config user.email "%email%"

:: Initialize Git repository if not already done
if not exist .git (
    echo Initializing Git repository...
    git init
)

:: Add all files
echo Adding files to Git...
git add .

:: Commit changes
set /p message="Enter commit message (or press Enter for default): "
if "%message%"=="" set message="Initial commit of MT4 Risk Management Calculator"
git commit -m "%message%"

:: Add remote repository
echo.
echo Adding remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/Satviksangamkar/Risk-Management-MT4.git

:: Push to GitHub
echo.
echo Pushing to GitHub...
git push -u origin master

echo.
echo Upload complete! Check your repository at:
echo https://github.com/Satviksangamkar/Risk-Management-MT4
echo.
pause
