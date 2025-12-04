@echo off
REM Windows Launcher for the Report Generator GUI
REM This script launches the GUI and immediately closes this console window.

REM 1. Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in your PATH.
    pause
    exit /b
)

REM 2. Install dependencies (quietly)
REM We use 'call' to ensure pip finishes before we continue
call pip install -r requirements.txt --quiet >nul 2>&1

REM 3. Launch the GUI
REM 'start ""' starts a new process.
REM 'pythonw' runs Python without a console window.
start "" pythonw gui_app.py

REM 4. Exit this batch script immediately
exit