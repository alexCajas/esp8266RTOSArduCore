# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess
import glob

def main():
    parser = argparse.ArgumentParser(description='Calculate size of compiled ESP-IDF project')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False, default="1048576")
    args, unknown = parser.parse_known_args()

    is_windows = os.name == 'nt' or sys.platform in ['win32', 'cygwin', 'msys']
    work_dir = os.path.join(args.build, "idfTemplate")

    if is_windows:
        # ==================== WINDOWS SIZE ====================
        print("[Size] Max Size from IDE: {} bytes".format(args.max_size), file=sys.stderr)
        
        build_folder = os.path.join(work_dir, "build")
        elf_files = glob.glob(os.path.join(build_folder, "*.elf"))
        elf_files = [f for f in elf_files if not f.endswith("bootloader.elf")]
        
        if not elf_files:
            print("[Size Error] No ELF file found.", file=sys.stderr)
            sys.exit(0)
            
        elf_path = elf_files[0]
        size_tool = os.path.join(args.xtensa, "bin", "xtensa-lx106-elf-size.exe")

        try:
            p_size = subprocess.Popen([size_tool, "-A", elf_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, _ = p_size.communicate()
            
            if hasattr(output, 'decode'):
                output = output.decode('utf-8', 'ignore')

            print("--- ELF SECTIONS FOUND ---", file=sys.stderr)
            
            total_size = 0
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    section = parts[0]
                    try:
                        size = int(parts[1])
                        # ESP8266 RTOS SDK Memory Sections que ocupan Flash/RAM estática
                        if "text" in section or "data" in section or "rodata" in section or "vectors" in section:
                            if "dram0.bss" not in section and "debug" not in section:
                                print("{} : {} bytes".format(section, size), file=sys.stderr)
                                total_size += size
                    except ValueError:
                        pass
                        
            print("--------------------------", file=sys.stderr)

            # Imprimimos al stdout estándar EXACTAMENTE lo que la Regex de Arduino espera
            # Arduino dividirá automáticamente este total_size entre el upload.maximum_size y pintará la barra
            print("Total image size: {} bytes".format(total_size))

        except Exception as e:
            print("[Size Error] " + str(e), file=sys.stderr)
            sys.exit(0)

    else:
        # ==================== LINUX SIZE (ORIGINAL) ====================
        env = os.environ.copy()
        env["IDF_PATH"] = args.idf
        xtensa_bin = os.path.join(args.xtensa, "bin")
        venv_bin = os.path.dirname(sys.executable)
        env["PATH"] = xtensa_bin + os.pathsep + venv_bin + os.pathsep + env.get("PATH", "")
        
        idf_py = os.path.join(args.idf, "tools", "idf.py")
        try:
            p_size = subprocess.Popen([sys.executable, idf_py, "size"], env=env, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, _ = p_size.communicate()
            if hasattr(output, 'decode'):
                output = output.decode('utf-8', 'ignore')
            
            # En Linux imprimimos la salida nativa de Espressif hacia Arduino
            print(output)
            
            if p_size.returncode != 0:
                sys.exit(p_size.returncode)
        except Exception as e:
            sys.exit(1)

if __name__ == "__main__":
    main()