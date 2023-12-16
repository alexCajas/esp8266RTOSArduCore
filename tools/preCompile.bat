@echo off
setlocal

REM Script: preCompile.cmd
REM Description: create an install files before to compile an IDF project.

REM Check if required options are provided
if "%~1"=="" (
    echo Usage: %~nx0 -b ^<build.path^>
    exit /b 1
)

REM Parse command-line options
set "build_dir=%~2"
set "extensa=%~4"
REM Print command-line options
echo preCompile -b: %build_dir% >&2
echo ext: %extensa% >&2
REM Create the directory and the file
mkdir "%build_dir%\preproc"
type nul > "%build_dir%\preproc\ctags_target_for_gcc_minus_e.cpp"
