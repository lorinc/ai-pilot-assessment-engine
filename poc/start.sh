#!/bin/bash
# Start script for AI Pilot Assessment POC

set -e  # Exit on error

echo "🚀 Starting AI Pilot Assessment POC"
echo "===================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found in venv!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start Streamlit app
echo "🌐 Starting Streamlit app..."
echo ""
streamlit run app.py
