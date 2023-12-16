#!/bin/bash

# Script: flash.sh
# Description: Flash an IDF project with specified parameters.

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

# Export environment variables
cd "$xtensa_dir"
cd ./bin
xtensaPath=$(pwd)
export IDF_PATH="$idf_dir"
export PATH="$PATH:$xtensaPath"

# Flash the IDF project
cd "$build_dir/idfTemplate/"
$IDF_PATH/tools/idf.py flash

echo "Press any key to continue"
read key
