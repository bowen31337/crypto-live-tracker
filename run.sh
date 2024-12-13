#!/bin/bash

# Exit on error
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo to install system dependencies"
    echo "Usage: sudo ./run.sh"
    exit 1
fi

# Detect if running on Raspberry Pi
IS_RASPBERRY_PI=false
if [ -f /etc/rpi-issue ] || grep -q "Raspberry Pi" /proc/cpuinfo; then
    IS_RASPBERRY_PI=true
    echo "Detected Raspberry Pi environment"
fi

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-wheel \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libatlas-base-dev \  # Required for numpy on RPi
    python3-numpy \      # System numpy for RPi
    python3-pandas \     # System pandas for RPi
    python3-matplotlib   # System matplotlib for RPi

# Print debugging information
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"

# Remove previous virtual environment and build artifacts
echo "Cleaning up previous installations..."
rm -rf venv build dist __pycache__ *.pyc

# Create fresh virtual environment
echo "Creating new virtual environment..."
python3 -m venv venv --system-site-packages  # Allow access to system packages

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Print Python paths for debugging
echo "Python executable: $(which python)"
echo "Python path: $PYTHONPATH"

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install wheel first
echo "Installing wheel..."
pip install wheel

if [ "$IS_RASPBERRY_PI" = true ]; then
    echo "Installing dependencies for Raspberry Pi..."
    # Install remaining packages without dependencies to avoid conflicts
    pip install -v requests ta python-dateutil --no-deps
else
    echo "Installing dependencies for standard environment..."
    pip install -v -r requirements.txt
fi

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
