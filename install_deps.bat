@echo off
title OZ Report Generator - Install Dependencies

echo ================================================
echo   Installing Dependencies...
echo ================================================
echo.

cd /d "%~dp0frontend"
echo [1/2] Installing Frontend npm packages...
call npm install
echo.

echo [2/2] Installing Backend Python packages...
pip install -r "%~dp0backend\requirements.txt"
echo.

echo ================================================
echo   All dependencies installed successfully!
echo ================================================
pause
