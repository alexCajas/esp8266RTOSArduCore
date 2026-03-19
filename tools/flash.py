import os
import sys
import argparse
import subprocess

def to_msys_path(win_path):
    """Convierte C:\\ruta a /c/ruta para que MSYS2 (Bash) lo entienda."""
    drive, tail = os.path.splitdrive(win_path)
    drive = drive.replace(':', '').lower()
    tail = tail.replace('\\', '/')
    return f"/{drive}{tail}"

def main():
    parser = argparse.ArgumentParser(description='Wrapper multiplataforma para flashear con ESP-IDF')
    parser.add_argument('-b', '--build', required=True, help='Directorio de compilación')
    parser.add_argument('-i', '--idf', required=True, help='Directorio del ESP-IDF')
    parser.add_argument('-x', '--xtensa', required=True, help='Directorio del toolchain Xtensa')
    # Añadimos el argumento del puerto serial (Arduino lo inyecta dinámicamente)
    parser.add_argument('-p', '--port', required=False, default=None, help='Puerto Serial (Ej. COM3 o /dev/ttyUSB0)')
    args = parser.parse_args()

    print("⚡ [Flasher] Iniciando subida de firmware al ESP8266...", file=sys.stderr)

    is_windows = sys.platform == 'win32'
    work_dir = os.path.join(args.build, "idfTemplate")
    
    # Copiamos el entorno actual para no modificar el del sistema globalmente
    env = os.environ.copy()

    if is_windows:
        # ==========================================
        #           MODO WINDOWS (MSYS2)
        # ==========================================
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

        # Formatear el argumento del puerto si existe
        port_arg = f"-p {args.port}" if args.port else ""
        
        # Comando bash que configura el PATH y flashea SIN abrir ventana nueva (-lc)
        bash_command = f"export IDF_PATH={idf_msys} && export PATH=$PATH:{xtensa_msys} && cd {work_msys} && python {idf_msys}/tools/idf.py {port_arg} flash"
        
        cmd = [msys_bash, "-lc", bash_command]
        
        try:
            # Ejecutamos pasando el entorno modificado
            subprocess.run(cmd, env=env, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ [Flasher] Error durante la subida en Windows. Código: {e.returncode}", file=sys.stderr)
            sys.exit(e.returncode)

    else:
        # ==========================================
        #           MODO LINUX / MAC
        # ==========================================
        env["IDF_PATH"] = args.idf
        xtensa_bin = os.path.join(args.xtensa, "bin")
        env["PATH"] = xtensa_bin + os.pathsep + env.get("PATH", "")
        
        idf_py = os.path.join(args.idf, "tools", "idf.py")
        cmd = [sys.executable, idf_py]
        
        # Añadir el puerto a la lista de argumentos si se proporcionó
        if args.port:
            cmd.extend(["-p", args.port])
        cmd.append("flash")
        
        try:
            subprocess.run(cmd, env=env, cwd=work_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ [Flasher] Error durante la subida en Linux/Mac. Código: {e.returncode}", file=sys.stderr)
            sys.exit(e.returncode)

if __name__ == "__main__":
    main()