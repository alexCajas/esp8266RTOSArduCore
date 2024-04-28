"""
This Python script reads a file, searches for lines containing the #include directive,
and then searches for the file specified in the #include directive and .c, .cpp, .h, and .hpp files
in the same directory as the included file. The absolute paths of the .c and .cpp files are stored in a variable named LIBRARY_SRCS,
and the highest level directories of the .h and .hpp files are stored in a variable named includedirs.
The results are saved in a JSON file named 'results.json'.
"""

import argparse
import os
import re
import queue
import json
from collections import defaultdict
import sys

libreriasExternas = set()
libreriasInternas = set()
includes_to_proccess = queue.Queue()
includes_proccessed = set()
files_to_proccess = queue.Queue()
files_proccessed = set()

files_h_hpp = set()
files_c_cpp = set()

def parse_file(file, internal_path, external_path):


    with open(file, 'r') as f:
        for line in f:
            # Buscar líneas de inclusión
            match = re.search(r'#include\s+"([^"]+)"|#include\s+<([^>]+)>', line)
            if match:
                if match.group(1):
                    path = find_absolute_paths(external_path, match.group(1))
                    if (path is not None) and ("build" not in path) and ("extras" not in path) and ("example" not in path) and ("examples" not in path) and ("tests" not in path) and ("test" not in path):

                        print(f"math1: {path} {external_path}",file=sys.stderr)
                        #print(f'match {match.group(1)}, en fichero {file}') 
                        if path is not None:
                            if path not in libreriasExternas:
                                libreriasExternas.add(path)
                                includes_to_proccess.put(path)
                                #parse_file(path,externPath)
                        else:
                            path = find_absolute_paths(internal_path,match.group(1))
                            if path is not None and path not in libreriasInternas:
                                libreriasInternas.add(path)
                                includes_to_proccess.put(path)
                elif match.group(2):
                    path = find_absolute_paths(internal_path, match.group(2))
                    print(f"math1: {match.group(2)}",file=sys.stderr)
                    #print(f'match: {match.group(2)}, en fichero {file}')
                    if path is not None and path not in libreriasInternas:
                        libreriasInternas.add(path)
                        includes_to_proccess.put(path)
                        #parse_file(path,externPath,internalPath)
    
    files_proccessed.add(file)

    if file.endswith(('.c', '.cpp')):
        files_c_cpp.add(file)
    elif file.endswith(('.h', '.hpp')):
        files_h_hpp.add(file)    

def looking_for_files(path, extensiones):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(tuple(extensiones)):
                absolute_path = os.path.abspath(os.path.join(root, file))
                files_to_proccess.put(absolute_path)






def find_absolute_paths(path, lib):
    for root, _, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            if lib in filepath:
                return os.path.abspath(filepath)





def get_include_dirs(paths):
    # Agrupa las rutas por proyecto
    rutas_por_proyecto = defaultdict(list)
    dirs = set()
    for ruta in paths:
        proyecto = obtener_nombre_proyecto(ruta)
        rutas_por_proyecto[proyecto].append(ruta)

    # Para cada proyecto, encuentra la ruta común más corta
    for proyecto, rutas in rutas_por_proyecto.items():
        ruta_comun = obtener_ruta_comun(rutas)
        dirs.add(ruta_comun)

    return dirs



def obtener_nombre_proyecto(ruta):
    # Divide la ruta en componentes
    partes = ruta.split(os.sep)
    # Encuentra el índice de 'libraries' en la ruta
    indice = partes.index('libraries')
    # Devuelve el nombre del proyecto, que debería ser el siguiente componente
    return partes[indice + 1]

def obtener_ruta_comun(rutas):
    # Divide cada ruta en componentes
    rutas_divididas = [ruta.split(os.sep) for ruta in rutas]
    # Encuentra la ruta común más corta
    ruta_comun = os.sep.join(x[0] for x in zip(*rutas_divididas) if len(set(x)) == 1)
    # Si solo hay una ruta, devuelve la ruta al directorio que contiene el fichero
    if len(rutas) == 1:
        ruta_comun = os.path.dirname(ruta_comun)
    return ruta_comun


def main():
    parser = argparse.ArgumentParser(description='Script that looking for the path of include files in .ino sketch.')
    parser.add_argument('-f', '--file', type=str, required=True, help='The .ino sketch.')
    parser.add_argument('-l', '--external_libraries', type=str, required=True, help='The Arduino Libraries path.')
    parser.add_argument('-i','--internal_libraries', type=str, required=True,help='The internal Arduino libraries path')
    args = parser.parse_args()


    print(f"-f: {args.file}",file=sys.stderr)
    print(f"-l: {args.external_libraries}",file=sys.stderr)
    print(f"-i: {args.internal_libraries}",file=sys.stderr)

    files_to_proccess.put(os.path.abspath(args.file))

    while not files_to_proccess.empty():
        file = files_to_proccess.get()
        if file not in files_proccessed:
            parse_file(file,args.internal_libraries, args.external_libraries)
        else:
            continue
        while not includes_to_proccess.empty():
            include = includes_to_proccess.get()
            files_to_proccess.put(include)
            ruta_absoluta = os.path.dirname(include)
            looking_for_files(ruta_absoluta, ('.c', '.cpp'))   
            includes_proccessed.add(include)


    # Uso de la función
    includedirs = get_include_dirs(files_h_hpp) 
    print(f"includedirs: {includedirs}",file=sys.stderr)
    #print(includedirs)


    results_path = os.path.dirname(args.file) + "/includes.json"
    with open(results_path, 'w') as f:
        json.dump({"LIBRARY_SRCS": list(set(files_c_cpp)), "includedirs": list(set(includedirs))}, f)    


if __name__ == '__main__':
    main()
