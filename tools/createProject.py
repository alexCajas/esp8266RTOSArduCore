import json
import os
import sys
import argparse

parser = argparse.ArgumentParser(description='create CMakelist.txt of .ino scketch')
parser.add_argument('-i', metavar='path', type=str,
                    help='include.cache_path')
parser.add_argument('-m', metavar='path', type=str,
                    help='main_project_path')
args = parser.parse_args()


file_path = args.i
cmake_dir = args.m


cmakeTemplate = """
set(LIBRARY_SRCS
    externalFiles
  )


set(includedirs
    externalDirs
  )


idf_component_register(SRCS ${LIBRARY_SRCS} INCLUDE_DIRS ${includedirs} )
"""

# Ruta del archivo JSON
json_path = cmake_dir+"/includes.json"  # Reemplaza con la ruta real de tu archivo

# Leer el archivo JSON
with open(json_path, 'r') as archivo_json:
    includes_json = json.load(archivo_json)

# Abrir el archivo include.cache en modo lectura
with open(file_path, "r") as f:
    # Leer el contenido del archivo
    content = f.read()

    # Cargar el contenido del archivo en formato JSON
    data = json.loads(content)

    # Obtener la lista de archivos de origen del objeto JSON, ignorando aquellos que contengan "null" y extrayendo solo el nombre de archivo
    srcs = [os.path.basename(entry["Sourcefile"]) for entry in data if entry.get("Sourcefile")]

    # Verificar que la lista de archivos de origen no esté vacía
    if not srcs:
        print("No se encontraron archivos de origen válidos en el archivo {}.".format(file_path))
        sys.exit(1)

    includes_json["LIBRARY_SRCS"].append('" "'.join(srcs))


cmake_content = cmakeTemplate.replace("externalFiles", '\n    '.join(includes_json['LIBRARY_SRCS']))
cmake_content = cmake_content.replace("externalDirs", '\n    '.join(includes_json['includedirs']))


# Crear el archivo CMakeLists.txt en el directorio especificado
cmake_path = os.path.join(cmake_dir, "CMakeLists.txt")
with open(cmake_path, "w") as cmake_file:
    cmake_file.write(cmake_content)


# Imprimir la ubicación del archivo CMakeLists.txt creado
print("Se ha creado el archivo {}.".format(cmake_path))
