#!/bin/bash
# Double-click runner script for macOS

# Change directory to script folder location
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==============================================="
echo "  GPO Sett's Arena Infamy Macro Launcher  "
echo "==============================================="
echo ""
echo "Installing/checking Python dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "Launching Macro GUI..."
python3 gui_app.py
