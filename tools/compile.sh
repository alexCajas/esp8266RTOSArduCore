#!/bin/bash

# Script: compile.sh
# Description: Build an IDF project with specified parameters.

# =========================
# Python VENV CONFIG
# =========================

# Detect venv python relative to platform
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_VENV="$SCRIPT_DIR/../env/bin/python"

# Fallback if venv does not exist
if [ ! -f "$PYTHON_VENV" ]; then
    echo "[WARN] VENV python not found, using system python" 1>&2
    PYTHON_VENV="python"
fi

# Optional: prepend venv to PATH (safe for most cases)
export PATH="$(dirname "$PYTHON_VENV"):$PATH"
export PATH="/usr/bin:$PATH"
# =========================

# Function to display script usage
usage() {
    echo "Usage: $0 -b <build.path> -i <idf.path> -x <xtensa.path>"
}

# Use getopt to handle command-line arguments
OPTS=$(getopt b:i:x: "$@")
if [ $? -ne 0 ]; then
    usage
    exit 1
fi

eval set -- "$OPTS"

# Default values
build_dir=""
idf_dir=""
xtensa_dir=""

# Parse command-line options
while true; do
    case "$1" in
        -b) build_dir="$2"; shift 2 ;;
        -i) idf_dir="$2"; shift 2 ;;
        -x) xtensa_dir="$2"; shift 2 ;;
        --) shift; break ;;
        *) usage; exit 1 ;;
    esac
done

# Check if required options are provided
if [ -z "$build_dir" ] || [ -z "$idf_dir" ] || [ -z "$xtensa_dir" ]; then
    usage
    exit 1
fi

# Print command-line options
echo "-b: $build_dir" 1>&2
echo "-i: $idf_dir" 1>&2
echo "-x: $xtensa_dir" 1>&2

# =========================
# TOOLCHAIN SETUP
# =========================

cd "$xtensa_dir"
cd ./bin
xtensaPath=$(pwd)

export IDF_PATH="$idf_dir"
export PATH="$PATH:$xtensaPath"

# =========================
# BUILD
# =========================

cd "$build_dir/idfTemplate/"

# Force IDF to use the venv Python
"$PYTHON_VENV" "$IDF_PATH/tools/idf.py" build 1>&2