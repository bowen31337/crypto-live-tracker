#!/bin/bash

# Exit on error
set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Run the application
python main.py
