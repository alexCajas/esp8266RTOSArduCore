"""
This Python script reads a file, searches for lines containing the #include directive,
and then searches for the file specified in the #include directive and .c, .cpp, .h, and .hpp files
in the same directory as the included file. The absolute paths of the .c and .cpp files are stored in a variable named LIBRARY_SRCS,
and the highest level directories of the .h and .hpp files are stored in a variable named includedirs.
The results are saved in a JSON file named 'results.json'.
"""

import sys
import os
import re
import json
import argparse

def find_file_in_directory(file_name, directory):
    for root, dirs, files in os.walk(directory):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def find_c_cpp_h_hpp_files(directory):
    c_cpp_files = []
    h_hpp_dirs = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if (file.endswith('.c') or file.endswith('.cpp')) and ('src' in root or root == directory):
                c_cpp_files.append(os.path.join(root, file))
            elif file.endswith('.h') or file.endswith('.hpp'):
                h_hpp_dirs.add(root)
    return c_cpp_files, list(h_hpp_dirs)

def find_include(file_name, libraries_path):
    directory = os.path.expanduser(libraries_path)
    LIBRARY_SRCS = []
    includedirs = set()
    with open(file_name, 'r') as file:
        for line in file:
            match = re.search(r'#include ["<](.*)[">]', line)
            if match and match.group(1) not in ["Arduino.h"]:
                included_file = match.group(1)
                path = find_file_in_directory(included_file, directory)
                if path is not None:
                    same_dir = os.path.dirname(path)
                    c_cpp_files, h_hpp_dirs = find_c_cpp_h_hpp_files(same_dir)
                    LIBRARY_SRCS.extend(c_cpp_files)
                    # Only add the highest level directory for each .h or .hpp file
                    for h_hpp_dir in h_hpp_dirs:
                        highest_level_dir = os.path.commonpath([same_dir, h_hpp_dir])
                        includedirs.add(highest_level_dir)
    return {"LIBRARY_SRCS": LIBRARY_SRCS, "includedirs": list(includedirs)}

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Script that looking for the path of include files in .ino sketch.')
    parser.add_argument('-f', '--file', type=str, required=True, help='The .ino sketch.')
    parser.add_argument('-l', '--libraries', type=str, required=True, help='The Arduino Libraries path.')
    args = parser.parse_args()
    
    results = find_include(args.file, args.libraries)
    results_path = os.path.dirname(args.file)+"/includes.json"
    with open(results_path, 'w') as f:
        json.dump(results, f)
