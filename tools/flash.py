# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess

def to_msys_path(win_path):
    """Converts C:\\path to /c/path for MSYS2 compatibility"""
    drive, tail = os.path.splitdrive(win_path)
    drive = drive.replace(':', '').lower()
    tail = tail.replace('\\', '/')
    return "/{}{}".format(drive, tail)

def run_unbuffered(cmd, env, cwd):
    """Executes a command forcing all output through the error channel for Arduino to print"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        p = subprocess.Popen(cmd, env=env, cwd=cwd, stdin=subprocess.PIPE, stdout=sys.stderr, stderr=sys.stderr)
        p.communicate(b"")
        if p.returncode != 0:
            sys.exit(p.returncode)
    except Exception as e:
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-p', '--port', required=False, default=None)
    args = parser.parse_args()

    print("[Flasher] Uploading firmware to ESP8266...", file=sys.stdout)
    sys.stdout.flush()
    
    is_windows = sys.platform == 'win32'
    work_dir = os.path.join(args.build, "idfTemplate")
    env = os.environ.copy()

    if is_windows:
        msys_bash = r"C:\msys32\usr\bin\bash.exe"
        username = os.environ.get('USERNAME', 'Default')
        env["HOME"] = "C:\\msys32\\home\\{}".format(username)

        # --- MAGIC MSYS2 VARIABLES ---
        env["MSYSTEM"] = "MINGW32"
        env["CHERE_INVOKING"] = "1"

        idf_msys = to_msys_path(args.idf)
        xtensa_msys = to_msys_path(os.path.join(args.xtensa, "bin"))
        work_msys = to_msys_path(work_dir)

        port_arg = "-p {}".format(args.port) if args.port else ""
        
        bash_command = 'export PATH="{}:$PATH" && export IDF_PATH="{}" && cd "{}" && python "{}/tools/idf.py" {} flash'.format(xtensa_msys, idf_msys, work_msys, idf_msys, port_arg)
        
        cmd = [msys_bash, "-lc", bash_command]
        run_unbuffered(cmd, env, work_dir)
        
    else:
        env["IDF_PATH"] = args.idf
        
        xtensa_bin = os.path.join(args.xtensa, "bin")
        venv_bin = os.path.dirname(sys.executable) 
        
        env["PATH"] = xtensa_bin + os.pathsep + venv_bin + os.pathsep + env.get("PATH", "")
        
        idf_py = os.path.join(args.idf, "tools", "idf.py")
        cmd = [sys.executable, idf_py]
        if args.port:
            cmd.extend(["-p", args.port])
        cmd.append("flash")
        
        run_unbuffered(cmd, env, work_dir)

if __name__ == "__main__":
    main()