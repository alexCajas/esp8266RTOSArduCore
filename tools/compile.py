import os
import sys
import argparse
import subprocess

def to_msys_path(win_path):
    """Convierte C:\\ruta a /c/ruta para MSYS2"""
    drive, tail = os.path.splitdrive(win_path)
    drive = drive.replace(':', '').lower()
    tail = tail.replace('\\', '/')
    return f"/{drive}{tail}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    args = parser.parse_args()

    print("🔧 [Builder] Iniciando compilación ESP8266 RTOS...", file=sys.stderr)
    
    is_windows = sys.platform == 'win32'
    work_dir = os.path.join(args.build, "idfTemplate")

    # Copiamos el entorno actual para no modificar el del sistema globalmente
    env = os.environ.copy()

    if is_windows:
        # ----- MODO WINDOWS (MSYS2) -----
        msys_bash = r"C:\msys32\usr\bin\bash.exe"
        if not os.path.exists(msys_bash):
            print("❌ [Error] MSYS2 no encontrado en C:\\msys32.", file=sys.stderr)
            sys.exit(1)

        # ¡EL SECRETO DEL .BAT! Reparar la variable HOME que Arduino corrompe
        username = os.environ.get('USERNAME', 'Default')
        env["HOME"] = rf"C:\msys32\home\{username}"

        # Convertir rutas a formato POSIX para MSYS
        idf_msys = to_msys_path(args.idf)
        xtensa_msys = to_msys_path(os.path.join(args.xtensa, "bin"))
        work_msys = to_msys_path(work_dir)

        # Comando bash que configura el PATH y compila SIN abrir ventana nueva (-lc)
        bash_command = f"export IDF_PATH={idf_msys} && export PATH=$PATH:{xtensa_msys} && cd {work_msys} && python {idf_msys}/tools/idf.py build"
        
        cmd = [msys_bash, "-lc", bash_command]
        
        try:
            # ¡Importante pasarle el env modificado!
            subprocess.run(cmd, env=env, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)

    else:
        # ----- MODO LINUX / MAC -----
        env["IDF_PATH"] = args.idf
        xtensa_bin = os.path.join(args.xtensa, "bin")
        env["PATH"] = xtensa_bin + os.pathsep + env.get("PATH", "")
        
        idf_py = os.path.join(args.idf, "tools", "idf.py")
        cmd = [sys.executable, idf_py, "build"]
        
        try:
            subprocess.run(cmd, env=env, cwd=work_dir, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)

if __name__ == "__main__":
    main()