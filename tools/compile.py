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
    parser = argparse.ArgumentParser(description='Wrapper to compile with ESP-IDF')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False) # Ignorado en compile
    args, unknown = parser.parse_known_args()

    is_windows = os.name == 'nt' or sys.platform in ['win32', 'cygwin', 'msys']
    work_dir = os.path.join(args.build, "idfTemplate")

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    if is_windows:
        # ==================== WINDOWS BUILD (CON VENTANA PARA EVADIR TTY) ====================
        msys_bash = r"C:\msys32\usr\bin\bash.exe"
        idf_msys = to_msys_path(args.idf)
        xtensa_msys = to_msys_path(os.path.join(args.xtensa, "bin"))
        work_msys = to_msys_path(work_dir)

        build_sh_path = os.path.join(work_dir, "run_build.sh")
        win_env = os.environ.copy()
        win_env["MSYSTEM"] = "MINGW32"

        with open(build_sh_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("export PATH=\"/mingw32/bin:/usr/bin:{}:$PATH\"\n".format(xtensa_msys))
            f.write("export IDF_PATH=\"{}\"\n".format(idf_msys))
            f.write("cd \"{}\"\n".format(work_msys))
            
            f.write("echo '========================================'\n")
            f.write("echo '   ESP8266 RTOS SDK Build in MSYS2      '\n")
            f.write("echo '========================================'\n")
            f.write("echo -e '\\n[Builder] Starting compilation...'\n")
            
            # Compilamos
            f.write("/mingw32/bin/python.exe \"{}/tools/idf.py\" build\n".format(idf_msys))
            f.write("BUILD_RET=$?\n")
            
            # Notificamos el resultado
            f.write("if [ $BUILD_RET -ne 0 ]; then\n")
            f.write("  echo -e '\\n[ERROR] Compilation failed with code '$BUILD_RET'!'\n")
            f.write("else\n")
            f.write("  echo -e '\\n[SUCCESS] Build finished successfully!'\n")
            f.write("fi\n")
            
            # [FIX UX]: Pausamos SIEMPRE la ventana para que el usuario pueda leer logs y warnings
            f.write("echo ''\n")
            f.write("read -p 'Press Enter to close this window and continue...' dummy\n")
            
            # Salimos devolviendo el código original de la compilación
            f.write("exit $BUILD_RET\n")

        print("[Builder] Opening MSYS2 Terminal for compilation...", file=sys.stderr)
        sys.stderr.flush()

        # Este flag es obligatorio para que idf.py/winpty no crasheen con el error TTY
        CREATE_NEW_CONSOLE = 0x00000010

        try:
            # Arduino se queda congelado en esta línea esperando a que la ventana negra se cierre
            p = subprocess.Popen([msys_bash, "--login", "-c", to_msys_path(build_sh_path)],
                                 creationflags=CREATE_NEW_CONSOLE, env=win_env)
            p.wait()
            
            if p.returncode != 0:
                print("\n[Builder Error] MSYS2 Compilation aborted by user or failed.", file=sys.stderr)
                sys.exit(p.returncode)
                
        except Exception as e:
            print("Error executing MSYS2 process: " + str(e), file=sys.stderr)
            sys.exit(1)

    else:
        # ==================== LINUX BUILD (ORIGINAL, SILENCIOSO) ====================
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

if __name__ == "__main__":
    main()