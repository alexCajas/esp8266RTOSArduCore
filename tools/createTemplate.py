import shutil
import os
import argparse
import glob
import subprocess
import sys

def move_files(source, destination, file_extension):
    files = glob.glob(os.path.join(source, f"*.{file_extension}"))
    for file in files:
        destination_file = os.path.join(destination, os.path.basename(file))
        if os.path.exists(destination_file):
            os.remove(destination_file)
        shutil.move(file, destination)


def copy_folder(source, destination):
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            if not os.path.exists(d):
                os.makedirs(d)
            copy_folder(s, d)
        else:
            shutil.copy2(s, d)



def main(build_path, idf_path, xtensa_path, libraries_path):
    print(f"Build Path: {build_path}",file=sys.stderr)
    print(f"IDF Path: {idf_path}",file=sys.stderr)
    print(f"Xtensa Path: {xtensa_path}",file=sys.stderr)
    print(f"Libraries Path: {libraries_path}",file=sys.stderr)

    # Copiar la carpeta '/tools/idfTemplate/' de 'idf_path' a 'build_path'
    source_path = os.path.join(idf_path, 'tools', 'idfTemplate')

    destination_path = os.path.join(build_path, os.path.basename(source_path))
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    copy_folder(source_path, destination_path) 

    # Mover todos los archivos '.ino.cpp' de 'build_path/sketch/' a 'build_path/idfTemplate/main/'
    source_path = os.path.join(build_path, 'sketch')
    destination_path = os.path.join(build_path, 'idfTemplate', 'main')
    move_files(source_path, destination_path, 'cpp')   

    # Almacenar la ruta absoluta del archivo '.ino.cpp' en una variable
    ino_cpp_file = glob.glob(os.path.join(destination_path, '*.ino.cpp'))[0]
    ino_cpp_file_abs_path = os.path.abspath(ino_cpp_file)
    
    # Llamar al script 'get_include_files.py'
    get_include_files_script = os.path.join(idf_path, 'tools', 'get_include_files.py')
    subprocess.run(['python', get_include_files_script, '-f', ino_cpp_file_abs_path, '-l', libraries_path])

    # Llamar al script 'createCMake.py'
    create_cmake_script = os.path.join(idf_path, 'tools', 'createCMake.py')
    includes_cache_file = os.path.join(build_path, 'includes.cache')
    subprocess.run(['python', create_cmake_script, '-i', includes_cache_file, '-m', destination_path])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script that accepts build path, IDF path, Xtensa path, and Libraries path as arguments.')
    parser.add_argument('-b', '--build', type=str, required=True, help='The build path.')
    parser.add_argument('-i', '--idf', type=str, required=True, help='The IDF path.')
    parser.add_argument('-x', '--xtensa', type=str, required=True, help='The Xtensa path.')
    parser.add_argument('-l', '--libraries', type=str, required=True, help='The Arduino Libraries path.')
    args = parser.parse_args()

    main(args.build, args.idf, args.xtensa, args.libraries)
