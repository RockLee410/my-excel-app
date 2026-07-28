@echo off
setlocal
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
)

.
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel >nul 2>&1
.
.venv\Scripts\python.exe -m pip install -r requirements.txt >nul 2>&1
.
.venv\Scripts\python.exe -m streamlit run excel_gen.py
