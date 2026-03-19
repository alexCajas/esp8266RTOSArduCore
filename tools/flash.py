import os
import sys
import argparse
import subprocess

def to_msys_path(win_path):
    drive, tail = os.path.splitdrive(win_path)
    drive = drive.replace(':', '').lower()
    tail = tail.replace('\\', '/')
    return f"/{drive}{tail}"

def run_unbuffered(cmd, env, cwd):
    """Ejecuta un comando forzando toda la salida por el canal de errores para que Arduino lo imprima"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        # Redirigimos explícitamente stdout hacia stderr
        subprocess.run(cmd, env=env, cwd=cwd, check=True, stdout=sys.stderr, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-p', '--port', required=False, default=None)
    args = parser.parse_args()

    print("⚡ [Flasher] Subiendo firmware al ESP8266...", file=sys.stdout, flush=True)
    
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

        port_arg = f"-p {args.port}" if args.port else ""
        bash_command = f"export IDF_PATH={idf_msys} && export PATH=$PATH:{xtensa_msys} && cd {work_msys} && python {idf_msys}/tools/idf.py {port_arg} flash"
        
        cmd = [msys_bash, "-lc", bash_command]
        run_unbuffered(cmd, env, work_dir)
        
    else:
        env["IDF_PATH"] = args.idf
        xtensa_bin = os.path.join(args.xtensa, "bin")
        env["PATH"] = xtensa_bin + os.pathsep + env.get("PATH", "")
        
        idf_py = os.path.join(args.idf, "tools", "idf.py")
        cmd = [sys.executable, idf_py]
        if args.port:
            cmd.extend(["-p", args.port])
        cmd.append("flash")
        
        run_unbuffered(cmd, env, work_dir)

if __name__ == "__main__":
    main()