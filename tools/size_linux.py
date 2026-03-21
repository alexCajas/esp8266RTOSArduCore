# -*- coding: utf-8 -*-
import os
import sys
import argparse
import subprocess
import re

def run_size_and_parse(cmd, env, cwd, max_size_str):
    """Executes the size command, captures the output, and calculates the Flash %"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        # Capture the output instead of printing it directly
        result = subprocess.run(cmd, env=env, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = result.stdout
        
        # [CRITICAL FIX FOR NEW ARCHITECTURE]: Print to stdout so Arduino IDE Regex catches it
        print(output, file=sys.stdout, end='')
        sys.stdout.flush()
        
        # Improved regex: \s*~?\s* ignores spaces and the "~" symbol if it exists
        match = re.search(r"Total image size:\s*~?\s*(\d+)\s+bytes", output)
        if match:
            used_size = int(match.group(1))
            
            # Bulletproof fallback in case Arduino sends the literal "{upload.maximum_size}"
            try:
                max_size = int(max_size_str)
            except ValueError:
                max_size = 1048576 # Default to 1MB
                
            percent = (used_size / max_size) * 100
            
            # Print your custom UI bar to stderr so the user sees it in the console
            print(f"\n📦 [Flash Memory] Program: {used_size} bytes ({percent:.1f}%) | Max space: {max_size} bytes\n", file=sys.stderr, flush=True)
            
    except subprocess.CalledProcessError as e:
        if e.stdout:
            print(e.stdout, file=sys.stderr)
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser(description='Linux Native Size Calculator')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False, default="1048576")
    parser.add_argument('-f', '--flash_size', required=False)
    args, unknown = parser.parse_known_args()

    work_dir = os.path.join(args.build, "idfTemplate")
    
    print("\n📊 [Builder] Calculating memory usage...", file=sys.stderr, flush=True)
    
    env = os.environ.copy()
    env["IDF_PATH"] = args.idf
    
    xtensa_bin = os.path.join(args.xtensa, "bin")
    venv_bin = os.path.dirname(sys.executable)
    env["PATH"] = f"{xtensa_bin}{os.pathsep}{venv_bin}{os.pathsep}{env.get('PATH', '')}"
    
    idf_py = os.path.join(args.idf, "tools", "idf.py")
    
    # Run the size analysis
    run_size_and_parse([sys.executable, idf_py, "size"], env, work_dir, args.max_size)

if __name__ == "__main__":
    main()