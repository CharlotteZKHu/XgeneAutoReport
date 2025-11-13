@echo off
REM --- Automated Report Generation Runner (Ultra-Simplified) ---
REM This script assumes you have a Python environment (like conda or system)
REM already activated and all dependencies (pandas, openpyxl) installed.
REM
REM It will only ask for file paths and run the main script.

REM --- Configuration ---
SET "MAIN_SCRIPT=main.py"

REM --- Main Logic ---
echo ==========================================
echo       Starting Report Generator
echo ==========================================

REM --- Interactive Input ---
echo.
echo Please provide the paths to your data files.
echo You can drag and drop the file onto this window to get its full path.
echo.

REM Prompt for the demographics file path
set /p demographics_path=" > Enter path to DEMOGRAPHICS file: "

REM Prompt for the lab results file path
set /p results_path=" > Enter path to LAB RESULTS file: "

REM Check if inputs are empty
IF "%demographics_path%"=="" (
    echo.
    echo  > ERROR: Demographics file path is required. Exiting.
    pause
    exit /b
)
IF "%results_path%"=="" (
    echo.
    echo  > ERROR: Lab results file path is required. Exiting.
    pause
    exit /b
)

REM --- End of input section ---

REM --- Run the main Python script ---
echo.
echo  > Paths received. Starting the report generator...
echo.
REM Pass the collected paths as arguments. Quotes are important!
python %MAIN_SCRIPT% --demographics "%demographics_path%" --results "%results_path%"

REM --- Finish ---
echo.
echo  > Process finished.
echo ==========================================
echo.
echo Press any key to exit...
pause >nul