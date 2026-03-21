# -*- coding: utf-8 -*-
import os
import sys
import argparse
import subprocess

def run_unbuffered(cmd, env, cwd):
    """Executes a command forcing all output through the error channel for Arduino to print"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        # Explicitly redirect stdout to stderr for Arduino IDE parsing
        subprocess.run(cmd, env=env, cwd=cwd, check=True, stdout=sys.stderr, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser(description='Linux Native Flasher')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-p', '--port', required=False, default=None)
    args, unknown = parser.parse_known_args()

    print("⚡ [Flasher] Uploading firmware to ESP8266...", file=sys.stderr, flush=True)
    
    work_dir = os.path.join(args.build, "idfTemplate")
    
    env = os.environ.copy()
    env["IDF_PATH"] = args.idf
    
    xtensa_bin = os.path.join(args.xtensa, "bin")
    # Added venv_bin here just in case python dependencies are needed during flash
    venv_bin = os.path.dirname(sys.executable) 
    env["PATH"] = f"{xtensa_bin}{os.pathsep}{venv_bin}{os.pathsep}{env.get('PATH', '')}"
    
    idf_py = os.path.join(args.idf, "tools", "idf.py")
    cmd = [sys.executable, idf_py]
    
    if args.port:
        cmd.extend(["-p", args.port])
        
    cmd.append("flash")
    
    run_unbuffered(cmd, env, work_dir)

if __name__ == "__main__":
    main()