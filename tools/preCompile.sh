#!/bin/bash

# Script: preCompile.sh
# Description: create an install files before to complie an IDF project.

# Function to display script usage
usage() {
    echo "Usage: $0 -b <build.path> "
}

# Use getopt to handle command-line arguments
OPTS=$(getopt b: "$@")
if [ $? -ne 0 ]; then
    usage
    exit 1
fi

eval set -- "$OPTS"

# Default values
build_dir=""



# Parse command-line options
while true; do
    case "$1" in
        -b) build_dir="$2"; shift 2 ;;
        --) shift; break ;;
        *) usage; exit 1 ;;
    esac
done

# Check if required options are provided
if [ -z "$build_dir" ]; then
    usage
    exit 1
fi

# Print command-line options
echo "-b: $build_dir" 1>&2

mkdir "$build_dir/preproc"
touch "$build_dir/preproc/ctags_target_for_gcc_minus_e.cpp"


