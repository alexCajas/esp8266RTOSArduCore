# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess
import re

def main():
    parser = argparse.ArgumentParser(description='Linux/macOS Size Calculator')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False, default="1048576")
    parser.add_argument('-f', '--flash_size', required=False, default="Unknown")
    args, unknown = parser.parse_known_args()

    work_dir = os.path.join(args.build, "idfTemplate")

    print("[Size] Physical Flash Size Selected: {}".format(args.flash_size), file=sys.stderr)
    print("[Size] Maximum App Partition Size: {} bytes".format(args.max_size), file=sys.stderr)
    
    env = os.environ.copy()
    env["IDF_PATH"] = args.idf
    xtensa_bin = os.path.join(args.xtensa, "bin")
    venv_bin = os.path.dirname(sys.executable)
    env["PATH"] = xtensa_bin + os.pathsep + venv_bin + os.pathsep + env.get("PATH", "")
    
    idf_py = os.path.join(args.idf, "tools", "idf.py")
    
    try:
        p_size = subprocess.Popen([sys.executable, idf_py, "size"], env=env, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = p_size.communicate()
        
        if hasattr(output, 'decode'):
            output = output.decode('utf-8', 'ignore')
        
        # Original logic: Print the Espressif table
        print(output, file=sys.stderr, end='')
        
        match = re.search(r"Total image size:\s*~?\s*(\d+)\s+bytes", output)
        if match:
            used_size = int(match.group(1))
            try: 
                max_size = int(args.max_size)
            except ValueError: 
                max_size = 1048576 
                
            percent = (float(used_size) / float(max_size)) * 100.0
            # Original logic: Print the custom memory bar to stderr
            print("\n[Flash Memory] Program: {} bytes ({:.1f}%) | Max space: {} bytes\n".format(used_size, percent, max_size), file=sys.stderr)
            sys.stderr.flush()
            
            # Print standard output for Arduino native Regex
            print("Total image size: {} bytes".format(used_size))
            
        if p_size.returncode != 0:
            sys.exit(p_size.returncode)
            
    except Exception as e:
        print("[Size Error] " + str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()