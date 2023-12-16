@echo off
setlocal

REM Comprobar si se recibieron los tres parametros
if "%~4"=="" (
    echo Usage: script.bat -b ^<build.path^> -i ^<idf.path^> -x ^<xtensa.path^>
    exit /b
)



set "build_dir=%~2"
set "idf_dir=%~4"


echo Build path: %build_dir% >&2
echo IDF path: %idf_dir% >&2



REM Llama al script que convierte la ruta del directorio al formato de Unix y captura su salida
for /f "delims=" %%i in ('call %idf_dir%\tools\windowsPathToUnixPath.bat  %build_dir%') do set "build_dir_unix=%%i"
echo build_dir_unix: %build_dir_unix% >&2

for /f "delims=" %%i in ('call %idf_dir%\tools\windowsPathToUnixPath.bat  %idf_dir%') do set "idf_dir_unix=%%i"
echo idf_dir_unix: %idf_dir_unix% >&2


REM delete space in idf_dir_unix
set "idf_dir_unix=%idf_dir_unix: =%"
set "xtensa=/../../../tools/xtensa-lx106-elf/8_4_0-esp-2020r3"
set "xtensa_dir_unix=%idf_dir_unix%%xtensa%"

REM for /f "delims=" %%i in ('call %idf_dir%\tools\windowsPathToUnixPath.bat  %xtensa_dir%') do set "xtensa_dir_unix=%%i"
echo xtensa_dir_unix: %xtensa_dir_unix% >&2

REM call to flash.sh
REM arduino arduino replace home enviroment variable, so it is nedded to fix it with the corret HOME enviroment variable
set HOME=C:\msys32\home\%username%
C:\msys32\msys2.exe %idf_dir%\tools\flashWindows.sh -b %build_dir_unix% -i %idf_dir_unix% -x %xtensa_dir_unix%
endlocal
