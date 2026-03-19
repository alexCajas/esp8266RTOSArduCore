import os
import sys
import argparse
import subprocess
import re

def to_msys_path(win_path):
    """Convierte C:\\ruta a /c/ruta para MSYS2"""
    drive, tail = os.path.splitdrive(win_path)
    drive = drive.replace(':', '').lower()
    tail = tail.replace('\\', '/')
    return f"/{drive}{tail}"

def run_unbuffered(cmd, env, cwd):
    """Ejecuta compilación forzando salida en tiempo real"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        subprocess.run(cmd, env=env, cwd=cwd, check=True, stdout=sys.stderr, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def run_size_and_parse(cmd, env, cwd, max_size_str):
    """Ejecuta el size, captura la salida, la imprime y calcula el % de Flash"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        # Capturamos la salida en lugar de imprimirla directamente
        result = subprocess.run(cmd, env=env, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = result.stdout
        
        # Imprimimos la tabla original de Espressif
        print(output, file=sys.stderr, end='')
        
        # Expresión regular mejorada: \s*~?\s* ignora espacios y el símbolo "~" si existe
        match = re.search(r"Total image size:\s*~?\s*(\d+)\s+bytes", output)
        if match:
            used_size = int(match.group(1))
            # Si Arduino no pasa el tamaño, asumimos 1MB (1048576 bytes) por defecto
            max_size = int(max_size_str) if max_size_str.strip() else 1048576 
            percent = (used_size / max_size) * 100
            
            print(f"\n📦 [Memoria Flash] Programa: {used_size} bytes ({percent:.1f}%) | Espacio máximo: {max_size} bytes\n", file=sys.stderr, flush=True)
            
    except subprocess.CalledProcessError as e:
        if e.stdout:
            print(e.stdout, file=sys.stderr)
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser(description='Wrapper para compilar con ESP-IDF y mostrar tamaño')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False, default="1048576") # Argumento nuevo
    args = parser.parse_args()

    print("🔧 [Builder] Iniciando compilación ESP8266 RTOS...", file=sys.stderr, flush=True)
    
    is_windows = sys.platform == 'win32'
    work_dir = os.path.join(args.build, "idfTemplate")
    env = os.environ.copy()

    if is_windows:
        msys_bash = r"C:\msys32\usr\bin\bash.exe"
        username = os.environ.get('USERNAME', 'Default')
        env["HOME"] = rf"C:\msys32\home\{username}"

        idf_msys = to_msys_path(args.idf)
        xtensa_msys = to_msys_path(os.path.join(args.xtensa, "bin"))
        work_msys = to_msys_path(work_dir)

        # 1. Compilación
        bash_build = f"export IDF_PATH={idf_msys} && export PATH=$PATH:{xtensa_msys} && cd {work_msys} && python {idf_msys}/tools/idf.py build"
        run_unbuffered([msys_bash, "-lc", bash_build], env, work_dir)

        # 2. Análisis de Memoria
        print("\n📊 [Builder] Calculando uso de memoria...", file=sys.stderr, flush=True)
        bash_size = f"export IDF_PATH={idf_msys} && export PATH=$PATH:{xtensa_msys} && cd {work_msys} && python {idf_msys}/tools/idf.py size"
        run_size_and_parse([msys_bash, "-lc", bash_size], env, work_dir, args.max_size)

    else:
        env["IDF_PATH"] = args.idf
        xtensa_bin = os.path.join(args.xtensa, "bin")
        env["PATH"] = xtensa_bin + os.pathsep + env.get("PATH", "")
        idf_py = os.path.join(args.idf, "tools", "idf.py")
        
        # 1. Compilación
        run_unbuffered([sys.executable, idf_py, "build"], env, work_dir)
        
        # 2. Análisis de Memoria
        print("\n📊 [Builder] Calculando uso de memoria...", file=sys.stderr, flush=True)
        run_size_and_parse([sys.executable, idf_py, "size"], env, work_dir, args.max_size)

if __name__ == "__main__":
    main()