# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess
import re

def to_msys_path(win_path):
    """Converts C:\\path to /c/path for MSYS2 compatibility"""
    drive, tail = os.path.splitdrive(win_path)
    drive = drive.replace(':', '').lower()
    tail = tail.replace('\\', '/')
    return "/{}{}".format(drive, tail)

def main():
    parser = argparse.ArgumentParser(description='Wrapper to compile with ESP-IDF and show size')
    # [FIX ARDUINO]: Hacemos los argumentos opcionales para que no crashee cuando Arduino 
    # llama a "compiler.size.cmd" sin parámetros al final del proceso.
    parser.add_argument('-b', '--build', required=False)
    parser.add_argument('-i', '--idf', required=False)
    parser.add_argument('-x', '--xtensa', required=False)
    parser.add_argument('-m', '--max_size', required=False, default="1048576")
    args = parser.parse_args()

    # Si falta algún argumento, salimos silenciosamente con éxito (Evita el error de Arduino)
    if not args.build or not args.idf or not args.xtensa:
        sys.exit(0)

    # Detectamos Windows, incluso si Python está corriendo bajo MSYS2/Cygwin
    is_windows = os.name == 'nt' or sys.platform in ['win32', 'cygwin', 'msys']
    work_dir = os.path.join(args.build, "idfTemplate")

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    if is_windows:
        # ==========================================
        #           WINDOWS (MSYS2) MODE
        # ==========================================
        msys_bash = r"C:\msys32\usr\bin\bash.exe"
        idf_msys = to_msys_path(args.idf)
        xtensa_msys = to_msys_path(os.path.join(args.xtensa, "bin"))
        work_msys = to_msys_path(work_dir)

        build_sh_path = os.path.join(work_dir, "run_build.sh")

        win_env = os.environ.copy()
        win_env["MSYSTEM"] = "MINGW32"

        # 1. El script maestro AHORA SOLO COMPILA en la ventana visible
        with open(build_sh_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("export PATH=\"/mingw32/bin:/usr/bin:{}:$PATH\"\n".format(xtensa_msys))
            f.write("export IDF_PATH=\"{}\"\n".format(idf_msys))
            f.write("cd \"{}\"\n".format(work_msys))
            
            f.write("echo '========================================'\n")
            f.write("echo '   ESP8266 RTOS SDK Build in MSYS2      '\n")
            f.write("echo '========================================'\n")
            
            f.write("echo -e '\\n[Builder] Starting compilation...'\n")
            f.write("/mingw32/bin/python.exe \"{}/tools/idf.py\" build\n".format(idf_msys))
            f.write("BUILD_RET=$?\n")
            
            f.write("if [ $BUILD_RET -ne 0 ]; then\n")
            f.write("  echo -e '\\n[ERROR] Compilation failed with code '$BUILD_RET'!'\n")
            f.write("  read -p 'Press Enter to close this window and cancel upload...' dummy\n")
            f.write("  exit $BUILD_RET\n")
            f.write("fi\n")

            f.write("echo -e '\\n[SUCCESS] Build finished successfully!'\n")
            f.write("sleep 1.5\n")

        print("[Builder] Opening MSYS2 Terminal for compilation...", file=sys.stderr)
        sys.stderr.flush()

        CREATE_NEW_CONSOLE = 0x00000010

        try:
            p = subprocess.Popen([msys_bash, "--login", "-c", to_msys_path(build_sh_path)],
                                 creationflags=CREATE_NEW_CONSOLE, env=win_env)
            p.wait()

            if p.returncode != 0:
                print("\n[Builder Error] MSYS2 compilation aborted.", file=sys.stderr)
                sys.exit(p.returncode)

            # 2. [FIX SIZE]: Calculamos el tamaño ejecutando Python NATIVO de Windows, sin Bash
            print("\n[Builder] Calculating memory usage...", file=sys.stderr)
            sys.stderr.flush()

            mingw_python = r"C:\msys32\mingw32\bin\python.exe"
            idf_py_path = os.path.join(args.idf, "tools", "idf.py")

            # Configuramos el entorno para que Python encuentre idf.py nativamente
            size_env = os.environ.copy()
            size_env["IDF_PATH"] = args.idf # Pasamos la ruta en formato Windows nativo
            
            # Ejecución limpia directa (Sin TTY de bash)
            p_size = subprocess.Popen([mingw_python, idf_py_path, "size"],
                                      env=size_env, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
            output, _ = p_size.communicate()

            if hasattr(output, 'decode'):
                output = output.decode('utf-8', 'ignore')

            # Imprimimos el log en la consola de Arduino
            print(output, file=sys.stderr, end='')

            match = re.search(r"Total image size:\s*~?\s*(\d+)\s+bytes", output)
            if match:
                used_size = int(match.group(1))
                try:
                    max_size = int(args.max_size)
                except ValueError:
                    max_size = 1048576 
                    
                percent = (float(used_size) / float(max_size)) * 100.0
                print("\n[Flash Memory] Program: {} bytes ({:.1f}%) | Max space: {} bytes\n".format(used_size, percent, max_size), file=sys.stderr)
                sys.stderr.flush()
            else:
                print("\n[Warning] Could not parse size output. Firmware is ready.", file=sys.stderr)

        except Exception as e:
            print("Error executing MSYS2 process: " + str(e), file=sys.stderr)
            sys.exit(1)

    else:
        # ==========================================
        #           LINUX / MAC MODE (Intacto)
        # ==========================================
        env = os.environ.copy()
        env["IDF_PATH"] = args.idf
        
        xtensa_bin = os.path.join(args.xtensa, "bin")
        venv_bin = os.path.dirname(sys.executable)
        
        env["PATH"] = xtensa_bin + os.pathsep + venv_bin + os.pathsep + env.get("PATH", "")
        
        idf_py = os.path.join(args.idf, "tools", "idf.py")
        
        p = subprocess.Popen([sys.executable, idf_py, "build"], env=env, cwd=work_dir)
        p.wait()
        
        if p.returncode != 0:
            sys.exit(p.returncode)
        
        print("\n[Builder] Calculating memory usage...", file=sys.stderr)
        sys.stderr.flush()
        
        try:
            p_size = subprocess.Popen([sys.executable, idf_py, "size"], env=env, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, _ = p_size.communicate()
            
            if hasattr(output, 'decode'):
                output = output.decode('utf-8', 'ignore')
            
            print(output, file=sys.stderr, end='')
            
            match = re.search(r"Total image size:\s*~?\s*(\d+)\s+bytes", output)
            if match:
                used_size = int(match.group(1))
                try: 
                    max_size = int(args.max_size)
                except ValueError: 
                    max_size = 1048576 
                percent = (float(used_size) / float(max_size)) * 100.0
                print("\n[Flash Memory] Program: {} bytes ({:.1f}%) | Max space: {} bytes\n".format(used_size, percent, max_size), file=sys.stderr)
                sys.stderr.flush()
                
            if p_size.returncode != 0: 
                sys.exit(p_size.returncode)
                
        except Exception as e:
            sys.exit(1)

if __name__ == "__main__":
    main()