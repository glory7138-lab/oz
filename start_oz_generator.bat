@echo off
title OZ Report Generator

echo ================================================
echo   OZ Report Generator - Starting...
echo ================================================
echo.

echo [1/2] Starting Backend Server (port 8088)...
start "OZ-Backend" cmd /k "cd /d %~dp0backend && python main.py"

echo [2/2] Starting Frontend Server (port 3088)...
start "OZ-Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ================================================
echo   Opening http://localhost:3088 in browser...
echo ================================================
echo.

ping 127.0.0.1 -n 5 >nul
start http://localhost:3088

