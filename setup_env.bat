@echo off
:: ==============================================================================
:: ESP8266 RTOS SDK - Automated Environment Setup for Windows (cURL + 7-Zip)
:: ==============================================================================

set "CORE_DIR=%~dp0"
set "MSYS_DIR=C:\msys32"
set "MSYS_BASH=%MSYS_DIR%\usr\bin\bash.exe"

:: ------------------------------------------------------------------------------
:: CONFIGURATION: REPLACE THESE URLS WITH YOUR ACTUAL GITHUB DIRECT LINKS
:: ------------------------------------------------------------------------------
:: URL to your hosted 7za.exe (Standalone 7-Zip extractor, ~700KB)
set "EXTRACTOR_URL=https://github.com/alexCajas/esp8266RTOSArduCore/releases/download/v1.0.3/7za.exe"

:: URL to your heavily compressed MSYS2 environment (msys32_rtos_patched.7z)
set "MSYS_7Z_URL=https://github.com/alexCajas/esp8266RTOSArduCore/releases/download/v1.0.3/msys32_rtos_patched.7z"

:: Temporary file paths
set "TEMP_7ZA=%TEMP%\7za_arduino_temp.exe"
set "TEMP_7Z=%TEMP%\msys32_rtos_patched.7z"

:: Path conversion for MSYS2 bash environment
set "CORE_DIR_UNIX=%CORE_DIR:\=/%"
set "REQ_FILE_UNIX=%CORE_DIR_UNIX%requirements.txt"

echo =======================================================
echo   ESP8266 RTOS Arduino Core - Windows Setup
echo =======================================================
echo.

:: Check if MSYS2 is already installed
if exist "%MSYS_BASH%" goto HAS_MSYS

:NO_MSYS
echo [Setup] MSYS2 not found at C:\msys32.
echo [Setup] Starting automated high-speed download and installation...
echo.

:: 1. Download the lightweight 7-Zip standalone extractor using native cURL
echo [1/4] Downloading portable extractor (7za.exe)...
curl.exe -L "%EXTRACTOR_URL%" -o "%TEMP_7ZA%"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] cURL failed to download the extractor. Please check your internet connection.
    goto END_ERROR
)
if not exist "%TEMP_7ZA%" (
    echo [ERROR] File was not saved. Check permissions in %TEMP%.
    goto END_ERROR
)

:: 2. Download the highly compressed MSYS2 environment (198MB) at maximum speed
echo.
echo [2/4] Downloading MSYS2 environment (198MB)...
curl.exe -L "%MSYS_7Z_URL%" -o "%TEMP_7Z%"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] cURL failed to download the MSYS2 environment.
    goto END_ERROR
)
if not exist "%TEMP_7Z%" (
    echo [ERROR] File was not saved.
    goto END_ERROR
)

:: 3. Extract using 7za.exe (Extremely fast, multi-threaded extraction)
echo.
echo [3/4] Extracting MSYS2 to C:\ (Lightning fast via 7-Zip)...
:: The 'x' command extracts with full paths. '-o' sets destination. '-y' assumes yes to all prompts.
"%TEMP_7ZA%" x "%TEMP_7Z%" -o"C:\" -y

:: Check if extraction was successful
if not exist "%MSYS_BASH%" (
    echo.
    echo [ERROR] Extraction failed. C:\msys32 was not created properly.
    echo Ensure you are running this script as Administrator if C:\ requires privileges.
    goto END_ERROR
)

:: 4. Clean up temporary files
echo.
echo [Setup] Cleaning up temporary files...
del "%TEMP_7ZA%"
del "%TEMP_7Z%"

echo [SUCCESS] MSYS2 installed successfully!
echo.
goto INSTALL_DEPS


:HAS_MSYS
echo [Setup] MSYS2 detected at C:\msys32. Skipping download.
echo.


:INSTALL_DEPS
echo [4/4] Installing required Python dependencies...
echo [Setup] Reading requirements from: %REQ_FILE_UNIX%

:: Execute pip install using the correct mingw32 python environment directly
"%MSYS_BASH%" -lc "MSYSTEM=MINGW32 CHERE_INVOKING=1 /mingw32/bin/python.exe -m pip install setuptools wheel && MSYSTEM=MINGW32 CHERE_INVOKING=1 /mingw32/bin/python.exe -m pip install --user -r '%REQ_FILE_UNIX%'"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python dependencies installation failed.
    goto END_ERROR
)

echo.
echo =======================================================
echo   [SUCCESS] Windows environment configured perfectly!
echo   You can now compile and upload from the Arduino IDE.
echo =======================================================
echo.
pause
exit /b 0


:END_ERROR
echo.
echo Press any key to exit...
pause >nul
exit /b 1