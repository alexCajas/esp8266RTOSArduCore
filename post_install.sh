#!/bin/bash

# Get the absolute path where the core is installed
CORE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$CORE_DIR"

echo "🔧 [Setup] Checking prerequisites for ESP8266 RTOS..."

# 1. Check if python3.10 is installed
if ! command -v python3.10 &>/dev/null; then
    echo "❌ [Error] Python 3.10 is not installed on this system."
    echo "This core requires Python 3.10. Please open a terminal and run:"
    echo "sudo apt-get update && sudo apt-get install -y python3.10"
    exit 1
fi

# 2. Check if python3.10-venv module is available
if ! python3.10 -c "import venv" &>/dev/null; then
    echo "❌ [Error] The python3.10-venv package is missing."
    echo "Virtual environments are required. Please open a terminal and run:"
    echo "sudo apt-get install -y python3.10-venv"
    exit 1
fi

echo "🔧 [Setup] Prerequisites met. Creating virtual environment (venv)..."

# Create the virtual environment in the 'env' folder
python3.10 -m venv env

# Activate and install dependencies directly into the venv
echo "📦 [Setup] Installing dependencies, CMake, and Ninja locally..."
./env/bin/python -m pip install --upgrade pip

# Install cmake and ninja here to avoid dependency on system's package manager
./env/bin/python -m pip install "setuptools<60" wheel cmake==3.28.3 ninja==1.11.1
./env/bin/python -m pip install -r ./requirements.txt

echo "✅ [Setup] Linux environment configured successfully."
exit 0