#!/bin/bash
# Run tests with coverage

set -e

# Change to project root
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Install dev dependencies if needed
pip install -r requirements-dev.txt -q

# Run tests
echo "Running tests..."
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo "Coverage report saved to htmlcov/index.html"
