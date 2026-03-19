#!/bin/bash

# Get the absolute path where the core is installed
CORE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$CORE_DIR"

echo "🔧 [Setup] Checking prerequisites for ESP8266 RTOS..."

# 1. Check if python3.10 is installed, install if missing
if ! command -v python3.10 &>/dev/null; then
    echo "⚠️ [Setup] Python 3.10 is not installed. Attempting to install via apt-get..."
    echo "🔑 You may be prompted for your sudo password."
    sudo apt-get update
    sudo apt-get install -y python3.10
else
    echo "✅ [Setup] Python 3.10 is already installed."
fi

# 2. Check if python3.10-venv module is available, install if missing
if ! python3.10 -c "import venv" &>/dev/null; then
    echo "⚠️ [Setup] python3.10-venv is missing. Attempting to install via apt-get..."
    echo "🔑 You may be prompted for your sudo password."
    sudo apt-get install -y python3.10-venv
else
    echo "✅ [Setup] python3.10-venv module is ready."
fi

# 3. Final verification to ensure both were successfully installed
if ! command -v python3.10 &>/dev/null || ! python3.10 -c "import venv" &>/dev/null; then
    echo "❌ [Error] Failed to install prerequisites automatically."
    echo "Please check your internet connection or install python3.10 and python3.10-venv manually."
    exit 1
fi

echo "🔧 [Setup] Prerequisites met. Creating virtual environment (venv)..."

# Create the virtual environment in the 'env' folder
python3.10 -m venv env

# Activate and install dependencies directly into the venv
echo "📦 [Setup] Installing dependencies, CMake (3.28.3), and Ninja (1.11.1) locally..."
./env/bin/python -m pip install --upgrade pip

# Pin exact versions of cmake and ninja to match the development environment
./env/bin/python -m pip install "setuptools<60" wheel cmake==3.28.3 ninja==1.11.1

# Install the rest of the core requirements
./env/bin/python -m pip install -r ./requirements.txt

echo "✅ [Setup] Linux environment configured successfully!"
echo "🚀 You can now compile your RTOS projects in the Arduino IDE."
exit 0