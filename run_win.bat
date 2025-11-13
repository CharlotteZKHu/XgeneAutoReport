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

REM --- UPDATED: Optional Copy Step ---
echo.
echo  > Report generation process finished.
echo.
set /p copy_path=" > (Optional) Enter a destination path to COPY the 'output' folder to (or press Enter to skip): "

REM Check if the user provided a path
IF NOT "%copy_path%"=="" (
    echo  > Copying all *.pdf files from 'output' to "%copy_path%"...
    REM Use robocopy to copy *only* .pdf files, replicating the folder structure
    REM "output" = source
    REM "%copy_path%\output" = destination
    REM *.pdf = file(s) to copy
    REM /S = copy subdirectories (but not empty ones)
    robocopy output "%copy_path%\output" *.pdf /S
    IF %errorlevel% leq 1 (
        REM robocopy returns 0 for no files copied, 1 for files copied successfully
        echo  > Successfully copied PDF files.
    ) ELSE (
        echo  > ERROR: Failed to copy files.
    )
) ELSE (
    echo  > Skipping copy step.
)
REM --- End of updated copy step ---

REM --- Finish ---
echo.
echo  > Process finished.
echo ==========================================
echo.
echo Press any key to exit...
pause >nul