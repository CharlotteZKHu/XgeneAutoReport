#!/bin/bash

# --- Automated Report Generation Runner (Simplified) ---
# This script assumes you have a Python environment (like conda or system)
# with the required packages installed.

# --- Configuration ---
MAIN_SCRIPT="main.py"

# --- Main Logic ---
echo "=========================================="
echo "  Starting Report Generator "
echo "=========================================="

# # 1. Check for Python 3
# if ! command -v python3 &> /dev/null; then
#     echo " > ERROR: python3 is not installed or not in PATH."
#     exit 1
# fi

# # 2. Install/Check dependencies in the current environment
# echo " > Checking/installing dependencies from requirements.txt..."
# pip3 install -r requirements.txt --quiet
# if [ $? -ne 0 ]; then
#     echo " > ERROR: Failed to install dependencies. Please check your pip3."
#     exit 1
# fi

# --- Interactive Input ---
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
    exit 1
fi
# --- End of new input section ---


# 3. Run the main Python script
echo ""
echo " > All checks passed. Starting the report generator..."
echo ""
# Pass the collected paths as arguments to the main script
python3 $MAIN_SCRIPT --demographics "$demographics_path" --results "$results_path"

# --- UPDATED: Optional Copy Step ---
echo ""
echo " > Report generation process finished."
echo ""
read -p " > (Optional) Enter a destination path to COPY the PDFs to (or press Enter to skip): " copy_path

if [ -n "$copy_path" ]; then
    echo " > Copying all *.pdf files from 'output' to '$copy_path'..."
    # We use rsync to copy *only* .pdf files, while recreating the directory structure.
    # -a: archive mode (recursive, preserves metadata)
    # -m: prune empty directories
    # --include='*/': ensures all directories are created
    # --include='*.pdf': includes all .pdf files
    # --exclude='*': excludes all other files
    # 'output/': source (trailing slash is important)
    # "$copy_path": destination (CHANGED: removed /output)
    rsync -am --include='*/' --include='*.pdf' --exclude='*' output/ "$copy_path"
    if [ $? -eq 0 ]; then
        echo " > Successfully copied PDF files."
    else
        echo " > ERROR: Failed to copy files. Make sure 'rsync' is installed."
    fi
else
    echo " > Skipping copy step."
fi
# --- End of updated copy step ---

# 4. Finish
echo ""
echo " > Process finished."
echo "=========================================="