@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ============================================================================
:: AI CLI MCP Server - Windows Batch Runner
:: Resolves local venv or system Python and launches MCP server with unbuffered stdio.
:: All diagnostics are printed to STDERR to ensure clean STDOUT for MCP JSON-RPC.
:: ============================================================================

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check for help flags
if /i "%~1"=="-h" goto :help
if /i "%~1"=="--help" goto :help
if /i "%~1"=="help" goto :help

:: Locate Python executable
set "PYTHON_EXE="

if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%SCRIPT_DIR%venv\Scripts\python.exe" set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%SCRIPT_DIR%env\Scripts\python.exe" set "PYTHON_EXE=%SCRIPT_DIR%env\Scripts\python.exe"

if not defined PYTHON_EXE (
    for /f "tokens=*" %%i in ('where python 2^>nul') do (
        if not defined PYTHON_EXE (
            set "candidate=%%i"
            echo !candidate! | findstr /i "WindowsApps" >nul
            if errorlevel 1 (
                set "PYTHON_EXE=!candidate!"
            )
        )
    )
)

if not defined PYTHON_EXE (
    for /f "tokens=*" %%i in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)

if not defined PYTHON_EXE (
    for /f "tokens=*" %%i in ('where py 2^>nul') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)

if not defined PYTHON_EXE goto :python_not_found

:: Check for status flag
if /i "%~1"=="--status" goto :status
if /i "%~1"=="status" goto :status

:: Run MCP Server in unbuffered mode (-u) for fast and reliable stdio communication
"%PYTHON_EXE%" -u "%SCRIPT_DIR%server.py" %*
exit /b %ERRORLEVEL%

:status
"%PYTHON_EXE%" -c "import asyncio, server; print(asyncio.run(server.cli_status()))"
exit /b %ERRORLEVEL%

:help
echo AI CLI MCP Server Runner
echo.
echo Usage:
echo   run_server.bat            Start the MCP Server on stdio transport
echo   run_server.bat --status   Check local CLI binary health and paths
echo   run_server.bat --help     Display this help menu
echo.
echo Environment Variables:
echo   CLI_YOLO_MODE             Enable non-interactive YOLO execution (default: true)
echo   CLI_DEFAULT_TIMEOUT       Default task execution timeout in seconds (default: 300)
echo   ALLOWED_WORKING_DIRECTORIES Permitted directory roots (default: *)
exit /b 0

:python_not_found
>&2 echo [ERROR] Python 3.10+ was not found on PATH or in a virtual environment.
>&2 echo [ERROR] Please install Python 3.10+ from https://www.python.org/ or add it to PATH.
exit /b 1
