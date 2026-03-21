# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess
import glob

def main():
    parser = argparse.ArgumentParser(description='Windows Native Flasher')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-p', '--port', required=False, default=None)
    args, unknown = parser.parse_known_args()

    print("[Flasher] Preparing to upload firmware (Native Windows)...", file=sys.stderr)
    sys.stderr.flush()
    
    work_dir = os.path.join(args.build, "idfTemplate")
    python_exe = r"C:\msys32\mingw32\bin\python.exe"
    esptool_path = os.path.join(args.idf, "components", "esptool_py", "esptool", "esptool.py")
    
    build_folder = os.path.join(work_dir, "build")
    bootloader_bin = os.path.join(build_folder, "bootloader", "bootloader.bin")
    partition_bin = os.path.join(build_folder, "partition_table", "partition-table.bin")
    
    app_bins = glob.glob(os.path.join(build_folder, "*.bin"))
    app_bins = [f for f in app_bins if not f.endswith("bootloader.bin") and not f.endswith("partition-table.bin")]
    
    if not app_bins:
        print("[Flasher Error] Compiled sketch binary not found in build folder.", file=sys.stderr)
        sys.exit(1)
        
    app_bin = app_bins[0]
    
    cmd = [python_exe, esptool_path, "--chip", "esp8266"]
    if args.port:
        cmd.extend(["--port", args.port])
        
    cmd.extend([
        "--baud", "460800",
        "--before", "default_reset",
        "--after", "hard_reset",
        "write_flash", "-z",
        "--flash_mode", "dio",
        "--flash_freq", "40m",
        "--flash_size", "detect",
        "0x0", bootloader_bin,
        "0x8000", partition_bin,
        "0x10000", app_bin
    ])

    print("[Flasher] Invoking esptool.py...", file=sys.stderr)
    
    try:
        p = subprocess.Popen(cmd, stdout=sys.stderr, stderr=sys.stderr)
        p.wait()
        if p.returncode != 0:
            print("\n[Flasher Error] Upload failed with exit code " + str(p.returncode), file=sys.stderr)
            sys.exit(p.returncode)
    except Exception as e:
        print("Error executing native flasher process: " + str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()