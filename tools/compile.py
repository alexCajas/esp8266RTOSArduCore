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
    return f"/{drive}{tail}"

def run_unbuffered(cmd, env, cwd):
    """Executes a command forcing real-time output to the Arduino console"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        subprocess.run(cmd, env=env, cwd=cwd, check=True, stdout=sys.stderr, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def run_size_and_parse(cmd, env, cwd, max_size_str):
    """Executes the size command, captures the output, and calculates the Flash %"""
    env["PYTHONUNBUFFERED"] = "1"
    try:
        # Capture the output instead of printing it directly
        result = subprocess.run(cmd, env=env, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = result.stdout
        
        # Print the original Espressif table
        print(output, file=sys.stderr, end='')
        
        # Improved regex: \s*~?\s* ignores spaces and the "~" symbol if it exists
        match = re.search(r"Total image size:\s*~?\s*(\d+)\s+bytes", output)
        if match:
            used_size = int(match.group(1))
            
            # Bulletproof fallback in case Arduino sends the literal "{upload.maximum_size}"
            try:
                max_size = int(max_size_str)
            except ValueError:
                max_size = 1048576 # Default to 1MB
                
            percent = (used_size / max_size) * 100
            
            print(f"\n📦 [Flash Memory] Program: {used_size} bytes ({percent:.1f}%) | Max space: {max_size} bytes\n", file=sys.stderr, flush=True)
            
    except subprocess.CalledProcessError as e:
        if e.stdout:
            print(e.stdout, file=sys.stderr)
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser(description='Wrapper to compile with ESP-IDF and show size')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False, default="1048576")
    args = parser.parse_args()

    print("🔧 [Builder] Starting ESP8266 RTOS compilation...", file=sys.stderr, flush=True)
    
    is_windows = sys.platform == 'win32'
    work_dir = os.path.join(args.build, "idfTemplate")
    env = os.environ.copy()

    if is_windows:
        # ==========================================
        #           WINDOWS (MSYS2) MODE
        # ==========================================
        msys_bash = r"C:\msys32\usr\bin\bash.exe"
        username = os.environ.get('USERNAME', 'Default')
        env["HOME"] = rf"C:\msys32\home\{username}"

        idf_msys = to_msys_path(args.idf)
        xtensa_msys = to_msys_path(os.path.join(args.xtensa, "bin"))
        work_msys = to_msys_path(work_dir)

        # 1. Compile
        bash_build = f"export IDF_PATH={idf_msys} && export PATH=$PATH:{xtensa_msys} && cd {work_msys} && python {idf_msys}/tools/idf.py build"
        run_unbuffered([msys_bash, "-lc", bash_build], env, work_dir)

        # 2. Memory Analysis
        print("\n📊 [Builder] Calculating memory usage...", file=sys.stderr, flush=True)
        bash_size = f"export IDF_PATH={idf_msys} && export PATH=$PATH:{xtensa_msys} && cd {work_msys} && python {idf_msys}/tools/idf.py size"
        run_size_and_parse([msys_bash, "-lc", bash_size], env, work_dir, args.max_size)

    else:
        # ==========================================
        #           LINUX / MAC MODE
        # ==========================================
        env["IDF_PATH"] = args.idf
        
        # Directories to inject into PATH
        xtensa_bin = os.path.join(args.xtensa, "bin")
        venv_bin = os.path.dirname(sys.executable) # This dynamically grabs the 'env/bin' path
        
        # Inject both xtensa and our venv bin into the system PATH
        env["PATH"] = xtensa_bin + os.pathsep + venv_bin + os.pathsep + env.get("PATH", "")
        
        idf_py = os.path.join(args.idf, "tools", "idf.py")
        
        # 1. Compile
        run_unbuffered([sys.executable, idf_py, "build"], env, work_dir)
        
        # 2. Memory Analysis
        print("\n📊 [Builder] Calculating memory usage...", file=sys.stderr, flush=True)
        run_size_and_parse([sys.executable, idf_py, "size"], env, work_dir, args.max_size)

if __name__ == "__main__":
    main()