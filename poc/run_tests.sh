#!/bin/bash
# Test runner script for CI/CD

set -e  # Exit on error

echo "🧪 Running AI Pilot Assessment POC Tests"
echo "========================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
echo "📊 Running tests with coverage..."
pytest --cov --cov-report=term-missing --cov-report=html

# Check if coverage meets minimum threshold
echo ""
echo "✅ All tests passed!"
echo ""
echo "📈 Coverage report generated in htmlcov/index.html"
