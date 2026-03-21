# -*- coding: utf-8 -*-
import os
import sys
import argparse
import subprocess

def run_unbuffered(cmd, env, cwd):
    """Executes a command forcing real-time output to the Arduino console"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        subprocess.run(cmd, env=env, cwd=cwd, check=True, stdout=sys.stderr, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser(description='Linux Native Compiler Wrapper')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False) # Ignored during compile
    parser.add_argument('-f', '--flash_size', required=False) # Ignored during compile
    args, unknown = parser.parse_known_args()

    work_dir = os.path.join(args.build, "idfTemplate")
    
    print("🔧 [Builder] Starting ESP8266 RTOS compilation...", file=sys.stderr, flush=True)
    
    env = os.environ.copy()
    env["IDF_PATH"] = args.idf
    
    # Directories to inject into PATH
    xtensa_bin = os.path.join(args.xtensa, "bin")
    venv_bin = os.path.dirname(sys.executable) # This dynamically grabs the 'env/bin' path
    
    # Inject both xtensa and our venv bin into the system PATH
    env["PATH"] = f"{xtensa_bin}{os.pathsep}{venv_bin}{os.pathsep}{env.get('PATH', '')}"
    
    idf_py = os.path.join(args.idf, "tools", "idf.py")
    
    # Compile natively
    run_unbuffered([sys.executable, idf_py, "build"], env, work_dir)

if __name__ == "__main__":
    main()