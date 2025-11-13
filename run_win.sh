#!/bin/bash
# run_win.sh - accepts two args (or will ask interactively if none provided)
MAIN_SCRIPT="main.py"

echo "=========================================="
echo " Starting Report Generator Setup Check..."
echo "=========================================="
echo ""

# # Check for Python
# if ! command -v python >/dev/null 2>&1; then
#     echo " > ERROR: Python is not installed or not in PATH."
#     exit 1
# fi

# If two args supplied, use them; otherwise prompt (useful when run from Git Bash interactively)
if [ "$#" -ge 2 ]; then
    demographics_path="$1"
    results_path="$2"
else
    echo "Please provide the paths to your data files."
    echo "You can drag and drop the file onto the terminal."
    echo ""
    read -p " > Enter path to DEMOGRAPHICS file: " demographics_path
    read -p " > Enter path to LAB RESULTS file: " results_path
fi

# sanitize: strip surrounding quotes if any
demographics_path="${demographics_path%\"}"
demographics_path="${demographics_path#\"}"
results_path="${results_path%\"}"
results_path="${results_path#\"}"

# For Windows paths, Python expects either:
# 1. Forward slashes: C:/Users/...
# 2. Raw strings with backslashes
# Since we're passing via command line, convert backslashes to forward slashes
# But we need to be careful to preserve the structure

# Use tr instead of sed for more reliable conversion
demographics_path=$(echo "$demographics_path" | tr '\\' '/')
results_path=$(echo "$results_path" | tr '\\' '/')

echo ""
echo " > Running with:"
echo "   demographics: $demographics_path"
echo "   results:      $results_path"
echo ""

python "$MAIN_SCRIPT" --demographics "$demographics_path" --results "$results_path"

echo ""
echo " > Process finished."
echo "=========================================="