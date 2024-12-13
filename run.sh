#!/bin/bash

# Exit on error
set -e

# Print debugging information
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"

# Remove previous virtual environment and build artifacts
echo "Cleaning up previous installations..."
rm -rf venv build dist __pycache__ *.pyc

# Create fresh virtual environment
echo "Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Print Python paths for debugging
echo "Python executable: $(which python)"
echo "Python path: $PYTHONPATH"

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements with verbose output
echo "Installing requirements..."
pip install -v -r requirements.txt

# Clear any Python cache
echo "Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Set PYTHONPATH to current directory
export PYTHONPATH="${PWD}"
echo "Set PYTHONPATH to: $PYTHONPATH"

# Run the application
echo "Running the application..."
python main.py
