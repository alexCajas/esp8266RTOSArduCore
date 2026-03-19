import os
import sys
import argparse
import shutil
import glob
import re

def copy_folder(source, destination):
    if not os.path.exists(destination):
        os.makedirs(destination)
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            copy_folder(s, d)
        else:
            shutil.copy2(s, d)

def move_sketch_files(source, destination):
    for ext in ['cpp', 'c', 'S', 'h', 'hpp']:
        files = glob.glob(os.path.join(source, f"*.{ext}"))
        for file in files:
            dest_file = os.path.join(destination, os.path.basename(file))
            if os.path.exists(dest_file):
                os.remove(dest_file)
            shutil.move(file, destination)

def find_library(header_path, search_paths):
    root_header = header_path.split('/')[0] if '/' in header_path else header_path

    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue
        for lib_name in os.listdir(base_path):
            lib_full_path = os.path.join(base_path, lib_name)
            if not os.path.isdir(lib_full_path):
                continue
            
            src_path = os.path.join(lib_full_path, 'src')
            if os.path.exists(src_path):
                if os.path.exists(os.path.join(src_path, header_path)) or os.path.exists(os.path.join(src_path, root_header)):
                    return lib_full_path, src_path
            
            if os.path.exists(os.path.join(lib_full_path, header_path)) or os.path.exists(os.path.join(lib_full_path, root_header)):
                return lib_full_path, lib_full_path

    return None, None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', required=True)
    parser.add_argument('-i', '--idf', required=True)
    parser.add_argument('-x', '--xtensa', required=True)
    parser.add_argument('-l', '--libraries', required=True)
    parser.add_argument('-s', '--sketch', required=True) # <-- Nueva variable
    args = parser.parse_args()

    external_libs_path = os.path.expanduser(args.libraries)
    internal_libs_path = os.path.join(args.idf, "libraries")
    search_paths = [external_libs_path, internal_libs_path]

    source_template = os.path.join(args.idf, 'tools', 'idfTemplate')
    dest_template = os.path.join(args.build, 'idfTemplate')
    copy_folder(source_template, dest_template)

    sketch_source = os.path.join(args.build, 'sketch')
    main_component_dir = os.path.join(dest_template, 'main')
    move_sketch_files(sketch_source, main_component_dir)

    include_dirs = set()
    sources = set()
    processed_files = set()
    files_to_parse = []
    processed_libs = set()

    # Añadimos el directorio original del sketch a los includes para que gcc encuentre las rutas relativas
    include_dirs.add(os.path.abspath(args.sketch))

    for ext in ['cpp', 'c', 'S', 'h', 'hpp']:
        for f in glob.glob(os.path.join(main_component_dir, f"*.{ext}")):
            abs_f = os.path.abspath(f)
            files_to_parse.append(abs_f)
            if ext in ['cpp', 'c', 'S']:
                sources.add(abs_f)

    while files_to_parse:
        current_file = files_to_parse.pop(0)
        if current_file in processed_files:
            continue
        
        processed_files.add(current_file)

        # Determinar el directorio base para resolver rutas relativas
        # Si es el sketch copiado, su base real es args.sketch. Si no, es su propia carpeta.
        if current_file.endswith('.ino.cpp') and main_component_dir in current_file:
            current_base_dir = args.sketch
        else:
            current_base_dir = os.path.dirname(current_file)

        try:
            with open(current_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match = re.search(r'#include\s*[<"]([^>"]+)[>"]', line)
                    if match:
                        header_name = match.group(1)
                        
                        # -- MAGIA 1: Resolución de Rutas Relativas/Locales --
                        # Comprobamos si el archivo está físicamente junto a quien lo llama o en la ruta relativa
                        local_path = os.path.abspath(os.path.join(current_base_dir, header_name))
                        if os.path.exists(local_path):
                            include_dirs.add(os.path.dirname(local_path))
                            if local_path not in processed_files and local_path not in files_to_parse:
                                files_to_parse.append(local_path)
                            continue # Ya resuelto localmente, no buscar en librerías
                        
                        # -- MAGIA 2: Búsqueda en Librerías Globales --
                        root_header = header_name.split('/')[0] if '/' in header_name else header_name
                        if root_header in processed_libs:
                            continue

                        lib_base, lib_inc_dir = find_library(header_name, search_paths)
                        if lib_base:
                            processed_libs.add(root_header)
                            include_dirs.add(lib_inc_dir)
                            
                            for root, dirs, files in os.walk(lib_inc_dir):
                                dirs[:] = [d for d in dirs if d.lower() not in ['examples', 'extras', 'test', 'tests', 'docs']]
                                for file in files:
                                    abs_file = os.path.abspath(os.path.join(root, file))
                                    if file.endswith(('.c', '.cpp', '.S')):
                                        sources.add(abs_file)
                                        files_to_parse.append(abs_file)
                                    elif file.endswith(('.h', '.hpp')):
                                        files_to_parse.append(abs_file)
        except Exception as e:
            pass

    formatted_srcs = '\n    '.join([f'"{s.replace(chr(92), "/")}"' for s in sources])
    formatted_dirs = '\n    '.join([f'"{d.replace(chr(92), "/")}"' for d in include_dirs])

    cmake_content = f"""
set(LIBRARY_SRCS
    {formatted_srcs}
)

set(includedirs
    {formatted_dirs}
)

idf_component_register(SRCS "${{LIBRARY_SRCS}}" INCLUDE_DIRS "${{includedirs}}")
"""
    cmake_path = os.path.join(main_component_dir, "CMakeLists.txt")
    with open(cmake_path, "w", encoding="utf-8") as f:
        f.write(cmake_content)

if __name__ == "__main__":
    main()