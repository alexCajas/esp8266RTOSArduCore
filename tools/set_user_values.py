# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Inject Arduino IDE hardware settings into ESP-IDF sdkconfig and CMake')
    parser.add_argument('-b',  '--build', required=True, help='Build directory path')
    parser.add_argument('-c',  '--cpu_freq', required=True, help='CPU Frequency (e.g., 80000000L)')
    parser.add_argument('-fm', '--flash_mode', required=True, help='Flash Mode (e.g., qio, dio)')
    parser.add_argument('-ff', '--flash_freq', required=True, help='Flash Frequency (e.g., 40, 80)')
    parser.add_argument('-fs', '--flash_size', required=True, help='Physical Flash Size (e.g., 4MB)')
    parser.add_argument('-l',  '--log_level', required=True, help='Arduino HAL Log Level (0-5)')
    
    # [NEW] Capture build.extra_flags from Arduino IDE or VSCode arduino.json
    parser.add_argument('-e',  '--extra_flags', nargs=argparse.REMAINDER, default=[], help='Custom C/C++ Compiler Flags')
    args, unknown = parser.parse_known_args()

    idf_template_dir = os.path.join(args.build, "idfTemplate")
    sdkconfig_path = os.path.join(idf_template_dir, "sdkconfig")
    cmakelists_path = os.path.join(idf_template_dir, "CMakeLists.txt")
    
    if not os.path.exists(sdkconfig_path):
        print("[Config Injector] Error: sdkconfig not found at {}".format(sdkconfig_path), file=sys.stderr)
        sys.exit(1)

    print("[Config Injector] Translating Arduino IDE settings to ESP-IDF Kconfig...", file=sys.stderr)

    # =========================================================================
    # FASE 1: INYECTAR KCONFIG EN SDKCONFIG (Hardware Menus)
    # =========================================================================
    
    config_updates = {
        "CONFIG_ARDUHAL_LOG_DEFAULT_LEVEL": args.log_level
    }

    # --- CPU Frequency ---
    if "160" in args.cpu_freq:
        config_updates["CONFIG_ESP8266_DEFAULT_CPU_FREQ_160"] = "y"
        config_updates["CONFIG_ESP8266_DEFAULT_CPU_FREQ_80"] = None
    else:
        config_updates["CONFIG_ESP8266_DEFAULT_CPU_FREQ_80"] = "y"
        config_updates["CONFIG_ESP8266_DEFAULT_CPU_FREQ_160"] = None

    # --- Flash Size ---
    sizes = ["1MB", "2MB", "4MB", "8MB", "16MB"]
    for s in sizes:
        key = "CONFIG_ESPTOOLPY_FLASHSIZE_{}".format(s)
        if s == args.flash_size:
            config_updates[key] = "y"
        else:
            config_updates[key] = None

    # --- Flash Mode ---
    modes = {"qio": "QIO", "qout": "QOUT", "dio": "DIO", "dout": "DOUT"}
    for m_key, m_val in modes.items():
        key = "CONFIG_ESPTOOLPY_FLASHMODE_{}".format(m_val)
        if m_key == args.flash_mode.lower():
            config_updates[key] = "y"
        else:
            config_updates[key] = None

    # --- Flash Frequency ---
    freqs = {"40": "40M", "80": "80M"}
    for f_key, f_val in freqs.items():
        key = "CONFIG_ESPTOOLPY_FLASHFREQ_{}".format(f_val)
        if f_key in args.flash_freq:
            config_updates[key] = "y"
        else:
            config_updates[key] = None

    # Read and strip out old configurations
    with open(sdkconfig_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    keys_to_modify = list(config_updates.keys())
    
    for line in lines:
        stripped_line = line.strip()
        keep_line = True
        
        for key in keys_to_modify:
            if stripped_line.startswith(key + "=") or stripped_line == "# {} is not set".format(key):
                keep_line = False
                break
                
        if keep_line:
            new_lines.append(line)

    # Append new Kconfig variables
    new_lines.append("\n# --- Arduino IDE Injected Configurations ---\n")
    for key, value in config_updates.items():
        if value is not None:
            new_lines.append("{}={}\n".format(key, value))

    with open(sdkconfig_path, "w") as f:
        f.writelines(new_lines)


    # =========================================================================
    # FASE 2: INYECTAR EXTRA FLAGS EN CMAKELISTS.TXT (Bypass para VSCode)
    # =========================================================================
    
    extra_flags_clean = " ".join(args.extra_flags).strip()
    
    if extra_flags_clean == '""' or extra_flags_clean == "''":
        extra_flags_clean = ""
    
    if extra_flags_clean and os.path.exists(cmakelists_path):
        print("[Config Injector] Custom build.extra_flags detected! Forcing into CMake...", file=sys.stderr)
        
        with open(cmakelists_path, "r") as f:
            cmake_lines = f.readlines()

        injection = [
            "\n# --- Arduino IDE / VSCode Custom build.extra_flags ---\n",
            "set(CMAKE_C_FLAGS \"${CMAKE_C_FLAGS} %s\")\n" % extra_flags_clean,
            "set(CMAKE_CXX_FLAGS \"${CMAKE_CXX_FLAGS} %s\")\n" % extra_flags_clean,
            "# -----------------------------------------------------\n\n"
        ]
        
        cmake_lines = injection + cmake_lines

        with open(cmakelists_path, "w") as f:
            f.writelines(cmake_lines)

    print("[Config Injector] Success! Configuration bridge fully synced.", file=sys.stderr)

if __name__ == "__main__":
    main()