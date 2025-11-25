###############################################
# CLOUDSYNC AUTO INSTALLER (with rclone login)
# Creates venv, installs deps, forces rclone auth
###############################################


=================================
WINDOWS INSTALLER (install.bat)
=================================


@echo off
set APPDIR=%~dp0cloudsync
if not exist %APPDIR% mkdir %APPDIR%
cd %APPDIR%


echo ==========================================
echo CloudSync Installer - Windows
echo ==========================================


echo Creating virtual environment...
python -m venv venv


call venv\Scripts\activate


echo Upgrading pip...
pip install --upgrade pip


echo Installing dependencies...
pip install flask watchdog


echo Checking rclone...
rclone version >nul 2>&1
if errorlevel 1 (
echo Rclone not found. Please install rclone and add it to PATH.
echo Download: https://rclone.org/downloads/
pause
exit
)


echo ------------------------------------------
echo Checking rclone configuration...
set RCLONE_CONF=%USERPROFILE%\.config\rclone\rclone.conf


if not exist %RCLONE_CONF% (
echo No rclone config found.
echo Opening browser for Google Drive login...
rclone config
) else (
echo Rclone config found. Skipping login.
)


echo ------------------------------------------
echo Launching CloudSync...
python main.py
pause