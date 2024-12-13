#!/bin/bash

# Exit on error
set -e

# Enable verbose output
set -x

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

# Print system information
echo "System information:"
uname -a
cat /etc/os-release
dpkg --print-architecture

# Update package lists and show available updates
echo "Updating package lists..."
apt-get update -y
apt-get upgrade --dry-run

# Check if required repositories are enabled
echo "Checking repositories..."
grep -r "^deb" /etc/apt/sources.list /etc/apt/sources.list.d/

# Try to install each package individually with error handling
install_package() {
    local package=$1
    echo "Attempting to install $package..."
    if apt-cache show "$package" >/dev/null 2>&1; then
        apt-get install -y "$package" || echo "Failed to install $package"
    else
        echo "Package $package not found in repositories"
    fi
}

# Basic development packages
echo "Installing basic development packages..."
BASIC_PACKAGES="
    python3
    python3-dev
    python3-pip
    python3-venv
    build-essential
"

for package in $BASIC_PACKAGES; do
    install_package "$package"
done

# Graphics and image processing packages
echo "Installing graphics packages..."
GRAPHICS_PACKAGES="
    libjpeg-dev
    zlib1g-dev
    libfreetype6-dev
    liblcms2-dev
    libwebp-dev
    libopenjp2-7-dev
    tk-dev
    python3-tk
    libatlas-base-dev
"

for package in $GRAPHICS_PACKAGES; do
    install_package "$package"
done

# Try to install Python packages from system repository first
echo "Installing Python packages from system repository..."
PYTHON_PACKAGES="
    python3-numpy
    python3-pandas
    python3-matplotlib
    python3-pip
"

for package in $PYTHON_PACKAGES; do
    install_package "$package"
done

# Print debugging information
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"

# Remove previous virtual environment and build artifacts
echo "Cleaning up previous installations..."
rm -rf venv build dist __pycache__ *.pyc

# Create fresh virtual environment
echo "Creating fresh virtual environment..."
python3 -m venv venv --system-site-packages

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Print Python paths for debugging
echo "Python executable: $(which python)"
echo "Python path: $PYTHONPATH"
echo "Pip location: $(which pip)"

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip -v

# Install wheel first
echo "Installing wheel..."
pip install wheel -v

if [ "$IS_RASPBERRY_PI" = true ]; then
    echo "Installing dependencies for Raspberry Pi..."
    # Try to install packages one by one with verbose output
    for package in requests ta python-dateutil; do
        echo "Installing $package..."
        pip install "$package" -v --no-deps || echo "Failed to install $package"
    done
else
    echo "Installing dependencies for standard environment..."
    while read -r package; do
        # Skip empty lines and comments
        [[ -z "$package" || "$package" =~ ^#.*$ ]] && continue
        echo "Installing $package..."
        pip install "$package" -v || echo "Failed to install $package"
    done < requirements.txt
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
