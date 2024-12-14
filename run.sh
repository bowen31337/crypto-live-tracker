#!/bin/bash

# Exit on error
set -e

# Enable verbose output
set -x

# Print system information
echo "System information:"
uname -a

# Detect if running on Raspberry Pi
IS_RASPBERRY_PI=false
if [ -f /etc/rpi-issue ] || grep -q "Raspberry Pi" /proc/cpuinfo; then
    IS_RASPBERRY_PI=true
    echo "Detected Raspberry Pi environment"
fi

# Print debugging information
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"

# Remove previous virtual environment and build artifacts
echo "Cleaning up previous installations..."
rm -rf venv build dist __pycache__ *.pyc

# Create fresh virtual environment
echo "Creating fresh virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Print Python paths for debugging
echo "Python executable: $(which python)"
echo "Python path: $PYTHONPATH"
echo "Pip location: $(which pip)"

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install wheel first
echo "Installing wheel..."
pip install wheel

if [ "$IS_RASPBERRY_PI" = true ]; then
    echo "Installing dependencies for Raspberry Pi..."
    # Install packages one by one
    for package in requests pandas numpy matplotlib ta; do
        echo "Installing $package..."
        pip install "$package" || echo "Failed to install $package"
    done
else
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

# Clear any Python cache
echo "Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# Set PYTHONPATH to current directory
export PYTHONPATH="${PWD}"
echo "Set PYTHONPATH to: $PYTHONPATH"

# List installed packages
echo "Installed Python packages:"
pip list

# Run the application
echo "Running the application..."
python main.py
