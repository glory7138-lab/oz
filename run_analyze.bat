@echo off
pip install openpyxl >nul 2>&1
python "%~dp0analyze_xlsx.py" > "%~dp0xlsx_result.txt" 2>&1
echo Done. Check xlsx_result.txt
pause
