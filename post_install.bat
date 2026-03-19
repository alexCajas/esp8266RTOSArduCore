@echo off
setlocal

set "CORE_DIR=%~dp0"
set "MSYS_BASH=C:\msys32\usr\bin\bash.exe"

echo [Setup] Configuring ESP8266 RTOS environment for Windows...

if exist "%MSYS_BASH%" (
    echo [Setup] MSYS2 detected. Installing Python dependencies in MSYS2...
    
    REM Convert the Windows path to MSYS format so bash can understand it
    for /f "delims=" %%i in ('"%MSYS_BASH%" -lc "cygpath -u '%CORE_DIR%'"') do set "CORE_DIR_UNIX=%%i"
    
    REM Run pip install within the MSYS2 environment
    "%MSYS_BASH%" -lc "cd '%CORE_DIR_UNIX%'; pip install setuptools wheel; pip install -r tools/requirements.txt"
    
    echo [Setup] Windows environment configured successfully.
) else (
    echo [WARNING] MSYS2 was not found at C:\msys32.
    echo Please download and install MSYS2 according to the core instructions.
    echo Once installed, open the MSYS2 terminal and run: pip install -r requirements.txt
)

endlocal
exit /b 0