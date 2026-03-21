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

def main():
    parser = argparse.ArgumentParser(description='Wrapper to compile with ESP-IDF in Windows')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False) # Ignored in compile
    parser.add_argument('-f', '--flash_size', required=False, default="Unknown") # Añadido para el platform.txt
    args, unknown = parser.parse_known_args()

    work_dir = os.path.join(args.build, "idfTemplate")

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    # ==================== WINDOWS BUILD (PURE TTY + SMART PAUSE + COLORS) ====================
    msys_bash = r"C:\msys32\usr\bin\bash.exe"
    idf_msys = to_msys_path(args.idf)
    xtensa_msys = to_msys_path(os.path.join(args.xtensa, "bin"))
    work_msys = to_msys_path(work_dir)

    build_sh_path = os.path.join(work_dir, "run_build.sh")
    win_env = os.environ.copy()
    win_env["MSYSTEM"] = "MINGW32"

    with open(build_sh_path, "w") as f:
        f.write("#!/bin/bash\n")
        
        # --- DEFINICIÓN DE COLORES Y FORMATOS ANSI AVANZADOS ---
        f.write("RED='\\033[1;31m'\n")
        f.write("GREEN='\\033[1;32m'\n")
        f.write("YELLOW='\\033[1;33m'\n")
        f.write("CYAN='\\033[1;36m'\n")
        f.write("ALERT_BOX='\\033[1;37;41m'\n") 
        f.write("NC='\\033[0m' # No Color\n")
        
        f.write("export PATH=\"/mingw32/bin:/usr/bin:{}:$PATH\"\n".format(xtensa_msys))
        f.write("export IDF_PATH=\"{}\"\n".format(idf_msys))
        f.write("cd \"{}\"\n".format(work_msys))
        
        f.write("echo -e \"${CYAN}========================================${NC}\"\n")
        f.write("echo -e \"${CYAN}   ESP8266 RTOS SDK Build in MSYS2      ${NC}\"\n")
        f.write("echo -e \"${CYAN}========================================${NC}\"\n")
        f.write("echo -e \"\\n[Builder] Target Physical Flash: {}\"\n".format(args.flash_size))
        f.write("echo -e \"\\n[Builder] Starting compilation...\"\n")
        
        # Compilamos Pura (Sin 'tee')
        f.write("/mingw32/bin/python.exe \"{}/tools/idf.py\" build\n".format(idf_msys))
        f.write("BUILD_RET=$?\n")
        
        # --- MANEJO DE ERROR (ROJO) ---
        f.write("if [ $BUILD_RET -ne 0 ]; then\n")
        f.write("  echo -e \"\\n${RED}[ERROR] Compilation failed with code $BUILD_RET!${NC}\"\n")
        f.write("  echo -e \"${RED}Please review the red errors above.\\n${NC}\"\n")
        f.write("  read -p \"Press Enter to close this window and cancel upload...\" dummy\n")
        f.write("  exit $BUILD_RET\n")
        f.write("fi\n")
        
        # --- MANEJO DE ÉXITO Y ALERTA VISUAL EXTREMA ---
        f.write("if [ -f build/compile_commands.json ]; then\n")
        f.write("  echo -e \"\\n${GREEN}[SUCCESS] Build finished successfully!${NC}\"\n")
        
        # Dibujamos un bloque gigante y colorido para llamar la atención sí o sí
        f.write("  echo -e \"\\n${ALERT_BOX}                                                         ${NC}\"\n")
        f.write("  echo -e \"${ALERT_BOX}   WARNINGS MAY EXIST IN THE LOG ABOVE!                  ${NC}\"\n")
        f.write("  echo -e \"${ALERT_BOX}   PRESS ANY KEY NOW TO PAUSE AND REVIEW THEM            ${NC}\"\n")
        f.write("  echo -e \"${ALERT_BOX}                                                         ${NC}\\n\"\n")
        
        # Pausa de 3 segundos. Si pulsa, se detiene indefinidamente.
        f.write("  read -t 3 -n 1 -p \"Closing automatically in 3 seconds...\" dummy\n")
        f.write("  if [ $? -eq 0 ]; then\n")
        f.write("    echo -e \"\\n\\n${YELLOW}=== PAUSED ===${NC}\"\n")
        f.write("    echo -e \"${YELLOW}Scroll up to read compiler warnings.${NC}\"\n")
        f.write("    echo -e \"${YELLOW}Press Enter to exit and continue with upload.${NC}\"\n")
        f.write("    read dummy\n")
        f.write("  fi\n")
        f.write("fi\n")
        
        f.write("exit 0\n")

    print("[Builder] Opening MSYS2 Terminal for compilation...", file=sys.stderr)
    sys.stderr.flush()

    # Flag OBLIGATORIO para emulación TTY
    CREATE_NEW_CONSOLE = 0x00000010

    try:
        p = subprocess.Popen([msys_bash, "--login", "-c", to_msys_path(build_sh_path)],
                             creationflags=CREATE_NEW_CONSOLE, env=win_env)
        p.wait()
        
        if p.returncode != 0:
            print("\n[Builder Error] MSYS2 Compilation aborted by user or failed.", file=sys.stderr)
            sys.exit(p.returncode)
            
    except Exception as e:
        print("Error executing MSYS2 process: " + str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()