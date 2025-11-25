#!/bin/bash
set -e

# CloudSync installer for Linux
# - Creates venv in current folder
# - Installs deps
# - Ensures rclone is configured
# - Starts main.py

# Get directory of this script
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo " CloudSync Installer - Linux"
echo "=========================================="

# Pick python command
if command -v python3 &> /dev/null; then
    PY=python3
elif command -v python &> /dev/null; then
    PY=python
else
    echo "No python interpreter found. Install python first."
    exit 1
fi

echo "[*] Creating virtual environment (./venv)..."
$PY -m venv venv

echo "[*] Activating venv..."
# shellcheck disable=SC1091
source venv/bin/activate

echo "[*] Upgrading pip..."
pip install --upgrade pip

echo "[*] Installing dependencies..."
pip install flask watchdog

echo "[*] Checking for rclone..."
if ! command -v rclone &> /dev/null; then
    echo "rclone not found. Install it first:"
    echo "  Arch:   sudo pacman -S rclone"
    echo "  Debian: sudo apt install rclone"
    exit 1
fi

RCLONE_CONF="$HOME/.config/rclone/rclone.conf"

echo "------------------------------------------"
if [ ! -f "$RCLONE_CONF" ]; then
    echo "[*] No rclone config found. Starting 'rclone config'..."
    echo "    A browser window will open for Google Drive login."
    rclone config
else
    echo "[*] rclone already configured. Skipping login."
fi

echo "------------------------------------------"
echo "[*] Starting CloudSync (main.py)..."
exec python main.py
