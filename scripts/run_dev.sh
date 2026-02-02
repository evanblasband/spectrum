#!/bin/bash
# Run the development server locally

set -e

# Change to project root
cd "$(dirname "$0")/.."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Copy .env.example to .env and fill in your API keys"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo "Starting development server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
