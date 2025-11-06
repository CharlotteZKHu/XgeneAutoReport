#!/bin/bash

# --- Automated Report Generation Runner ---
# This script automates the setup and execution of the patient report generator.
# It handles virtual environment creation, dependency installation, and running the main script.

# --- Configuration ---
# # Name of the virtual environment directory
# VENV_DIR="venv"
# The main Python script to execute
MAIN_SCRIPT="main.py"

# --- Main Logic ---
echo "=========================================="
echo " Starting Report Generator Setup Check... "
echo "=========================================="

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo " > ERROR: python3 is not installed or not in PATH."
    exit 1
fi

# # 2. Check for virtual environment directory
# if [ ! -d "$VENV_DIR" ]; then
#     echo " > Virtual environment not found. Creating '$VENV_DIR'..."
#     python3 -m venv $VENV_DIR
#     if [ $? -ne 0 ]; then
#         echo " > ERROR: Failed to create virtual environment."
#         exit 1
#     fi
# fi

# # 3. Activate virtual environment and install dependencies
# source "$VENV_DIR/bin/activate"
# echo " > Checking/installing dependencies from requirements.txt..."
# pip install -r requirements.txt --quiet
# if [ $? -ne 0 ]; then
#     echo " > ERROR: Failed to install dependencies."
#     deactivate
#     exit 1
# fi

# --- NEW: Interactive Input ---
echo ""
echo "Please provide the paths to your data files."
echo "You can drag and drop the file onto the terminal to get its full path."
echo ""

# Prompt for the demographics file path
read -p " > Enter path to DEMOGRAPHICS file: " demographics_path

# Prompt for the lab results file path
read -p " > Enter path to LAB RESULTS file: " results_path

# Check if inputs are empty
if [ -z "$demographics_path" ] || [ -z "$results_path" ]; then
    echo ""
    echo " > ERROR: Both file paths are required. Exiting."
    deactivate
    exit 1
fi
# --- End of new input section ---


# 4. Run the main Python script
echo ""
echo " > All checks passed. Starting the report generator..."
echo ""
# Pass the collected paths as arguments to the main script
python3 $MAIN_SCRIPT --demographics "$demographics_path" --results "$results_path"

# 5. Deactivate the virtual environment upon completion
echo ""
echo " > Process finished. Deactivating virtual environment."
deactivate
echo "=========================================="