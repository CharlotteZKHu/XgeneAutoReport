@echo off
REM Windows Launcher for the Report Generator GUI
echo Starting Patient Report Generator...
echo.
echo Please wait while the application loads...

REM Ensure python is found
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in your PATH.
    pause
    exit /b
)

REM Install dependencies quietly if needed
pip install -r requirements.txt --quiet

REM Launch the GUI
REM pythonw.exe runs without keeping a black console window open in the background
start "" pythonw gui_app.py