=================================
LINUX INSTALLER (install.sh)
=================================


#!/bin/bash
APPDIR="$HOME/.cloudsync"
mkdir -p "$APPDIR"
cd "$APPDIR"


echo "=========================================="
echo " CloudSync Installer - Linux"
echo "=========================================="


echo "Creating virtual environment..."
python3 -m venv venv


source venv/bin/activate


echo "Upgrading pip..."
pip install --upgrade pip


echo "Installing dependencies..."
pip install flask watchdog


echo "Checking rclone..."
if ! command -v rclone &> /dev/null; then
echo "Rclone not found. Install it first."
echo "Arch: sudo pacman -S rclone"
echo "Debian/Ubuntu: sudo apt install rclone"
exit 1
fi


echo "------------------------------------------"
CONFIG_FILE="$HOME/.config/rclone/rclone.conf"


if [ ! -f "$CONFIG_FILE" ]; then
echo "No rclone config found. Starting login setup..."
rclone config
else
echo "Rclone config already exists. Skipping login."
fi


echo "------------------------------------------"
echo "Launching CloudSync..."
python3 main.py