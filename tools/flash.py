# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess
import glob

def main():
    parser = argparse.ArgumentParser(description='Wrapper to flash ESP-IDF project')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-p', '--port', required=False, default=None)
    args, unknown = parser.parse_known_args()

    print("[Flasher] Preparing to upload firmware...", file=sys.stderr)
    sys.stderr.flush()
    
    is_windows = os.name == 'nt' or sys.platform in ['win32', 'cygwin', 'msys']
    work_dir = os.path.join(args.build, "idfTemplate")

    if is_windows:
        # ==================== WINDOWS NATIVE FLASH ====================
        # En Windows, evitamos MSYS2 e idf.py por completo para evitar errores de TTY.
        # Llamamos directamente a esptool.py usando el python nativo de MINGW32.
        
        python_exe = r"C:\msys32\mingw32\bin\python.exe"
        esptool_path = os.path.join(args.idf, "components", "esptool_py", "esptool", "esptool.py")
        
        # 1. Rutas de los archivos binarios compilados
        build_folder = os.path.join(work_dir, "build")
        bootloader_bin = os.path.join(build_folder, "bootloader", "bootloader.bin")
        partition_bin = os.path.join(build_folder, "partition_table", "partition-table.bin")
        
        # Buscamos el sketch principal (.bin)
        app_bins = glob.glob(os.path.join(build_folder, "*.bin"))
        app_bins = [f for f in app_bins if not f.endswith("bootloader.bin") and not f.endswith("partition-table.bin")]
        
        if not app_bins:
            print("[Flasher Error] Compiled sketch binary not found in build folder.", file=sys.stderr)
            sys.exit(1)
            
        app_bin = app_bins[0]
        
        # 2. Argumentos base para esptool (Baud rate de flash por defecto: 460800)
        # Nota: ESP8266 default flash arguments
        cmd = [
            python_exe, esptool_path,
            "--chip", "esp8266"
        ]
        
        if args.port:
            cmd.extend(["--port", args.port])
            
        cmd.extend([
            "--baud", "460800",
            "--before", "default_reset",
            "--after", "hard_reset",
            "write_flash",
            "-z",
            "--flash_mode", "dio",
            "--flash_freq", "40m",
            "--flash_size", "detect",
            "0x0", bootloader_bin,
            "0x8000", partition_bin,
            "0x10000", app_bin
        ])

        print("[Flasher] Invoking native esptool.py...", file=sys.stderr)
        
        try:
            # Ejecutamos esptool nativamente en Windows. No crashea porque es python puro y duro.
            p = subprocess.Popen(cmd, stdout=sys.stderr, stderr=sys.stderr)
            p.wait()
            
            if p.returncode != 0:
                print("\n[Flasher Error] Native esptool failed with exit code " + str(p.returncode), file=sys.stderr)
                sys.exit(p.returncode)
                
        except Exception as e:
            print("Error executing native flasher process: " + str(e), file=sys.stderr)
            sys.exit(1)
            
    else:
        # ==================== LINUX / MAC FLASH (ORIGINAL) ====================
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
                sys.exit(p.returncode)
                
        except Exception as e:
            sys.exit(1)

if __name__ == "__main__":
    main()