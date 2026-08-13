@echo off
title PLA0501_R26 파일 생성
echo.
echo ===================================================
echo   PLA0501_R26.ozr / .odi  파일을 생성합니다
echo ===================================================
echo.
python "d:\antigra\oz\create_r26_final.py"
echo.
if %errorlevel% neq 0 (
    echo [오류] Python 실행에 실패했습니다.
    echo Python이 설치되어 있는지 확인해 주세요.
    pause
) else (
    pause
)
