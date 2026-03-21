# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Linux/macOS Flasher')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-p', '--port', required=False, default=None)
    args, unknown = parser.parse_known_args()

    print("[Flasher] Uploading firmware to ESP8266 via idf.py...", file=sys.stderr)
    sys.stderr.flush()
    
    work_dir = os.path.join(args.build, "idfTemplate")
    
    env = os.environ.copy()
    env["IDF_PATH"] = args.idf
    xtensa_bin = os.path.join(args.xtensa, "bin")
    venv_bin = os.path.dirname(sys.executable) 
    env["PATH"] = xtensa_bin + os.pathsep + venv_bin + os.pathsep + env.get("PATH", "")
    
    idf_py = os.path.join(args.idf, "tools", "idf.py")
    cmd = [sys.executable, idf_py]
    
    if args.port:
        cmd.extend(["-p", args.port])
        
    cmd.append("flash")
    
    try:
        p = subprocess.Popen(cmd, env=env, cwd=work_dir, stdout=sys.stderr, stderr=sys.stderr)
        p.wait()
        if p.returncode != 0:
            print("\n[Flasher Error] Upload failed.", file=sys.stderr)
            sys.exit(p.returncode)
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()