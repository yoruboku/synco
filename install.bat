@echo off
setlocal ENABLEDELAYEDEXPANSION

REM CloudSync installer for Windows
REM - Creates venv in current folder
REM - Installs deps
REM - Ensures rclone is configured
REM - Starts main.py

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ==========================================
echo   CloudSync Installer - Windows
echo ==========================================

echo [*] Creating virtual environment (.venv)...
python -m venv venv
if errorlevel 1 (
    echo Failed to create venv. Make sure Python is installed and in PATH.
    pause
    exit /b 1
)

echo [*] Activating venv...
call venv\Scripts\activate

echo [*] Upgrading pip...
pip install --upgrade pip

echo [*] Installing dependencies...
pip install flask watchdog

echo [*] Checking for rclone...
rclone version >nul 2>&1
if errorlevel 1 (
    echo rclone not found. Install it and add to PATH:
    echo   https://rclone.org/downloads/
    pause
    exit /b 1
)

set "RCLONE_CONF=%USERPROFILE%\.config\rclone\rclone.conf"

echo ------------------------------------------
if not exist "%RCLONE_CONF%" (
    echo [*] No rclone config found. Running "rclone config"...
    echo     A browser window will open for Google Drive login.
    rclone config
) else (
    echo [*] rclone already configured. Skipping login.
)

echo ------------------------------------------
echo [*] Starting CloudSync (main.py)...
python main.py
pause
