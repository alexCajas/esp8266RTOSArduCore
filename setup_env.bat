@echo off
setlocal

set "CORE_DIR=%~dp0"
set "MSYS_BASH=C:\msys32\usr\bin\bash.exe"

REM Native batch trick: Replace all backslashes (\) with forward slashes (/)
set "CORE_DIR_UNIX=%CORE_DIR:\=/%"
set "REQ_FILE_UNIX=%CORE_DIR_UNIX%requirements.txt"

echo [Setup] Configuring ESP8266 RTOS environment for Windows...

if exist "%MSYS_BASH%" (
    echo [Setup] MSYS2 detected. Installing Python dependencies in MSYS2...
    echo [Setup] Reading requirements from: %REQ_FILE_UNIX%
    
    REM [FIX CRÍTICO]: Forzamos el entorno MinGW32 y la no conversión de rutas
    set "MSYSTEM=MINGW32"
    set "CHERE_INVOKING=1"
    
    REM Ejecutamos usando explícitamente el Python de mingw32 para instalar las librerías 
    REM de forma global (--user) donde el ESP8266_RTOS_SDK de Espressif las buscará después.
    "%MSYS_BASH%" -lc "/mingw32/bin/python.exe -m pip install setuptools wheel && /mingw32/bin/python.exe -m pip install --user -r '%REQ_FILE_UNIX%'"
    
    echo [Setup] Windows environment configured successfully!
) else (
    echo [WARNING] MSYS2 was not found at C:\msys32.
    echo Please download and install MSYS2 according to the core instructions.
    echo Once installed, open the MSYS2 MinGW32 terminal and run:
    echo /mingw32/bin/python.exe -m pip install -r "%REQ_FILE_UNIX%"
)

echo.
echo Press any key to close this window...
pause >nul

endlocal
exit /b 0