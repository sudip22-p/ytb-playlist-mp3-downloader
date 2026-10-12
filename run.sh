#!/usr/bin/env bash
# macOS & Linux one-click launcher for YouTube Playlist Audio Downloader

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "      YouTube Playlist Audio Downloader Launcher"
echo "============================================================"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed."
    echo "Please install Python 3.11+ (e.g., 'brew install python' on macOS)."
    exit 1
fi

# Run via virtual environment if present, else run system python
if [ -f ".venv/bin/python3" ]; then
    .venv/bin/python3 playlist_downloader.py
else
    echo "[*] Checking required packages..."
    python3 -m pip install -q -r requirements.txt
    python3 playlist_downloader.py
fi

