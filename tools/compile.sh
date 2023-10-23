#!/bin/bash

# Script: compile.sh
# Description: Build an IDF project with specified parameters.

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

# Build IDF project
cp -r "$idf_dir/tools/idfTemplate" "$build_dir" 1>&2
mv "$build_dir/sketch/"* "$build_dir/idfTemplate/main"

# Build main/CMakeLists.txt using a Python script
scketchFilePath=$(find "$build_dir/idfTemplate/main" -maxdepth 1 -type f -name '*.ino.cpp')
python "$idf_dir/tools/get_include_files.py" -r "$scketchFilePath"

# Execute the Python script with the absolute path to the include.cache file as an argument
python "$idf_dir/tools/createProject.py" -i "$build_dir/includes.cache" -m "$build_dir/idfTemplate/main/"

# Export environment variables
cd "$xtensa_dir"
cd ./bin
xtensaPath=$(pwd)
export IDF="$idf_dir"
export PATH="$PATH:$xtensaPath"



cd "$build_dir/idfTemplate/"

# Build the IDF project
$IDF/tools/idf.py build 1>&2
