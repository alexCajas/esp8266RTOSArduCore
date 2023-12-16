@echo off
setlocal

REM Script: windowsPathToUnixPath.bat
REM Description: format windows path to unix path.


REM Parse command-line options
set "windows_dir=%~1"

REM Print command-line options
REM echo %windows_dir% >&2

REM Convierte la ruta del directorio al formato de Unix /c/ficheros/build
set "unix_path=%windows_dir:\=/%"
set "unix_path=/%unix_path:~0,1%%unix_path:~2%"

REM Establece una variable de entorno con la ruta en formato Unix
echo %unix_path% 