@echo off
setlocal
title YouTube Playlist Audio Downloader

echo ============================================================
echo       YouTube Playlist Audio Downloader Launcher
echo ============================================================
echo.

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.11 or later from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: If .venv exists, use its Python; otherwise run using system python
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" playlist_downloader.py
) else (
    echo [*] Checking required packages...
    python -m pip install -q -r requirements.txt
    python playlist_downloader.py
)

pause

