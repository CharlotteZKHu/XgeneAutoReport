#!/bin/bash
cd "$(dirname "$0")"

echo "Starting Patient Report Generator..."

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed."
    exit 1
fi

# Install dependencies
pip3 install -r requirements.txt --quiet

# Run the GUI
python3 gui_app.py