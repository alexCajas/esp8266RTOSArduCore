# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Linux/macOS Compiler Wrapper')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False)
    parser.add_argument('-f', '--flash_size', required=False)
    args, unknown = parser.parse_known_args()

    work_dir = os.path.join(args.build, "idfTemplate")
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    print("[Builder] Starting native compilation...", file=sys.stderr)
    sys.stderr.flush()

    env = os.environ.copy()
    env["IDF_PATH"] = args.idf
    xtensa_bin = os.path.join(args.xtensa, "bin")
    venv_bin = os.path.dirname(sys.executable)
    env["PATH"] = xtensa_bin + os.pathsep + venv_bin + os.pathsep + env.get("PATH", "")
    
    idf_py = os.path.join(args.idf, "tools", "idf.py")
    
    try:
        p = subprocess.Popen([sys.executable, idf_py, "build"], env=env, cwd=work_dir)
        p.wait()
        if p.returncode != 0:
            print("\n[Builder Error] Compilation failed.", file=sys.stderr)
            sys.exit(p.returncode)
    except Exception as e:
        print("Error executing build process: " + str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()