#!/bin/bash
# Setup virtual environment and run tests
# This script can be executed by Cascade in a single command

set -e  # Exit on error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "================================================"
echo "AI Pilot Assessment Engine - Setup & Test"
echo "================================================"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo ""
    echo "1. Creating virtual environment..."
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo ""
    echo "1. Virtual environment already exists"
fi

# Activate venv and install dependencies
echo ""
echo "2. Installing dependencies..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1

# Install only the minimal dependencies needed for Story 1.1
pip install pydantic networkx pytest > /dev/null 2>&1
echo "   ✓ Dependencies installed (pydantic, networkx, pytest)"

# Run the test script
echo ""
echo "3. Running graph construction tests..."
echo ""
python3 scripts/test_graph_construction.py

# Store exit code
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "================================================"
    echo "✓ Setup and tests completed successfully!"
    echo "================================================"
else
    echo "================================================"
    echo "✗ Tests failed with exit code $TEST_EXIT_CODE"
    echo "================================================"
fi

exit $TEST_EXIT_CODE
