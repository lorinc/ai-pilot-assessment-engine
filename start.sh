#!/bin/bash
# Start script for AI Pilot Assessment Engine

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Start Streamlit app
streamlit run src/app.py
