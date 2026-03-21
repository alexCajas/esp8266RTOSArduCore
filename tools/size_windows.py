# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse
import subprocess
import glob

def main():
    parser = argparse.ArgumentParser(description='Windows Size Calculator')
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-m', '--max_size', required=False, default="1048576")
    parser.add_argument('-f', '--flash_size', required=False, default="Unknown")
    args, unknown = parser.parse_known_args()

    work_dir = os.path.join(args.build, "idfTemplate")

    print("[Size] Physical Flash Size Selected: {}".format(args.flash_size), file=sys.stderr)
    print("[Size] Maximum App Partition Size: {} bytes".format(args.max_size), file=sys.stderr)
    
    build_folder = os.path.join(work_dir, "build")
    elf_files = glob.glob(os.path.join(build_folder, "*.elf"))
    elf_files = [f for f in elf_files if not f.endswith("bootloader.elf")]
    
    if not elf_files:
        print("[Size Error] No ELF application file found in build directory.", file=sys.stderr)
        sys.exit(0)
        
    elf_path = elf_files[0]
    size_tool = os.path.join(args.xtensa, "bin", "xtensa-lx106-elf-size.exe")

    try:
        p_size = subprocess.Popen([size_tool, "-A", elf_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = p_size.communicate()
        
        if hasattr(output, 'decode'):
            output = output.decode('utf-8', 'ignore')

        print("--- MEMORY SECTIONS USED ---", file=sys.stderr)
        
        total_size = 0
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                section = parts[0]
                try:
                    size = int(parts[1])
                    if "text" in section or "data" in section or "rodata" in section or "vectors" in section:
                        if "dram0.bss" not in section and "debug" not in section:
                            print("{} : {} bytes".format(section, size), file=sys.stderr)
                            total_size += size
                except ValueError:
                    pass
                    
        print("----------------------------", file=sys.stderr)
        
        # Output exactly what Arduino expects on stdout for the Regex
        print("Total image size: {} bytes".format(total_size))

    except Exception as e:
        print("[Size Error] Exception occurred: " + str(e), file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()