import argparse
import os
import sys


def main(build_path):
    print(f"preCompile Build Path: {build_path}", file=sys.stderr)
    
    # Crear la carpeta 'preproc' y el archivo 'ctags_target_for_gcc_minus_e.cpp' en 'build_path'
    preproc_path = os.path.join(build_path, 'preproc')
    os.makedirs(preproc_path, exist_ok=True)

    file_path = os.path.join(preproc_path, 'ctags_target_for_gcc_minus_e.cpp')
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script that accepts build path as arguments.')
    parser.add_argument('-b', '--build', type=str, required=True, help='The build path.')
    args = parser.parse_args()

    main(args.build)
