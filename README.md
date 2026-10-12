# 🎵 YouTube Playlist Audio Downloader (MP3)

A lightweight, reliable Python script to download YouTube playlists as high-quality, sequentially numbered MP3 tracks. Works cross-platform on **Windows, macOS, Linux, and iOS** (via terminal environments).

The resulting MP3 files are universally playable offline on **Windows, macOS, Linux, iOS (iPhone/iPad), and Android**.

---

## ✨ Features

- **Audio-Only Download**: Downloads audio streams directly without fetching video.
- **192 kbps MP3 Conversion**: Converts tracks into MP3 format and embeds ID3 tags (Title, Artist, Album).
- **Preserves Playlist Order**: Names files sequentially with zero-padded prefixes (e.g., `001 - Song Title.mp3`).
- **Resuming & Duplicate Skipping**: Maintains a `download_archive.txt` file so interrupted downloads resume seamlessly and existing tracks are never re-downloaded.
- **Fault-Tolerant with Retry**: Continues through network glitches and offers an instant retry prompt for any failed tracks.
- **Built-in Anti-403 Protection**: Uses mobile/embedded stream clients to avoid YouTube's `HTTP Error 403: Forbidden` rate limits.
- **Auto-Dependency Detection**: Automatically detects FFmpeg and Node.js challenge runtimes.

---

## 💻 Prerequisites

- **Python 3.11+**
- **FFmpeg** (for MP3 conversion and metadata tagging)

---

## 🚀 Quick Setup

### 1. Windows (PowerShell)

```powershell
# Install FFmpeg
winget install Gyan.FFmpeg

# Set up environment & install requirements
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Tip for Windows**: If `ffmpeg -version` is not recognized right after running `winget`, refresh your terminal PATH:
> ```powershell
> $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
> ```

### 2. macOS

```bash
# Install FFmpeg (Homebrew)
brew install ffmpeg

# Set up environment & install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Linux

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg python3-venv

# Fedora
sudo dnf install -y ffmpeg python3

# Arch Linux
sudo pacman -S ffmpeg python

# Set up environment & install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. iOS (iPhone / iPad)

You can run this script directly on iOS using terminal apps like **[a-Shell](https://apps.apple.com/app/a-shell/id1473805438)** or **[iSH](https://apps.apple.com/app/ish-shell/id1436902243)**:

```bash
# In a-Shell (Python and ffmpeg are built-in):
pip install -r requirements.txt
python playlist_downloader.py

# In iSH (Alpine Linux):
apk add python3 py3-pip ffmpeg
pip install -r requirements.txt
python3 playlist_downloader.py
```

---

## 🎧 How to Run

### Option A: One-Click Launchers
- **Windows**: Double-click `run.bat` (or run `.\run.bat` in PowerShell).
- **macOS / Linux**: Run `./run.sh` in Terminal.

### Option B: Command Line
```bash
python playlist_downloader.py
# (or 'python3 playlist_downloader.py' on macOS/Linux/iOS)
```

---

## 📝 Usage Prompts

1. **Playlist URL**: Paste your YouTube playlist or single video URL:
   ```text
   Enter YouTube Playlist URL: https://www.youtube.com/playlist?list=PL...
   ```
2. **Destination Folder**: Press **Enter** to use the default `./downloads` folder, or type a custom path (e.g., `D:\Music\My Playlist`).
3. **Browser Cookies (Optional)**: If any tracks are age-restricted or strictly blocked, enter your browser name (`chrome`, `edge`, `firefox`, `brave`, or `safari`), or simply press **Enter** to skip.

---

## 🛠️ Troubleshooting

### `HTTP Error 403: Forbidden`
- The script includes automatic fallback to mobile stream clients (`android`, `ios`) to bypass YouTube's web CDN rate limits.
- If individual tracks fail during a long playlist download, answer `y` when prompted to **retry failed tracks** at the end.
- If tracks still fail, enter your browser name (e.g., `chrome` or `edge`) when prompted for browser cookies at startup.

### Missing FFmpeg
- Make sure FFmpeg is installed and added to your system `PATH`.
- On Windows, you can also place `ffmpeg.exe` and `ffprobe.exe` directly into the script folder.

---

## ⚙️ Configuration

In `playlist_downloader.py`, you can customize:
- `DEFAULT_BITRATE = "192"` (e.g., set to `"320"` for 320 kbps).
- `ARCHIVE_FILENAME = "download_archive.txt"`.

---

## ⚖️ Disclaimer

Use this tool only to download content that you own or are authorized to download. Respect YouTube's Terms of Service and applicable copyright laws.
