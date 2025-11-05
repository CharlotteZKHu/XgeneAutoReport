#!/bin/bash

# --- Automated Report Generation Runner ---
# This script automates the setup and execution of the patient report generator.
# It handles virtual environment creation, dependency installation, and running the main script.

# --- Configuration ---
# Name of the virtual environment directory
VENV_DIR="venv"
# The main Python script to execute
MAIN_SCRIPT="main.py"

# --- Main Logic ---
echo "=========================================="
echo "Initializing Report Generation System..."
echo "=========================================="

# 1. Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo " > Virtual environment not found. Creating one at './$VENV_DIR/'..."
    # Check if python3 is available
    if ! command -v python3 &> /dev/null
    then
        echo " > ERROR: python3 could not be found. Please install Python 3 to continue."
        exit 1
    fi
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo " > ERROR: Failed to create virtual environment."
        exit 1
    fi
    echo " > Virtual environment created successfully."
fi

# 2. Activate the virtual environment
# The source command executes the script in the current shell
echo " > Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. Install/update dependencies from requirements.txt
echo " > Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo " > ERROR: Failed to install dependencies."
    # Deactivate on failure
    deactivate
    exit 1
fi
echo " > Dependencies are up to date."

# 4. Run the main Python script
echo ""
echo " > All checks passed. Starting the report generator..."
echo ""
python3 $MAIN_SCRIPT

# 5. Deactivate the virtual environment upon completion
deactivate
echo ""
echo "=========================================="
echo "Script finished."
echo "=========================================="
