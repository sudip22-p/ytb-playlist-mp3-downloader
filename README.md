# 🎵 YouTube Playlist Audio Downloader (MP3)

A fast, reliable, and beginner-friendly Python command-line tool to download YouTube playlists as high-quality, sequentially numbered MP3 tracks. Works cross-platform on **Windows and macOS**, creating offline music collections for **Android, Windows, iOS (iPhone/iPad), and Mac**.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Cross-Platform Compatibility (Windows, Mac, Android, iOS)](#-cross-platform-compatibility)
- [Prerequisites](#-prerequisites)
- [Complete Installation & Setup Guide](#-complete-installation--setup-guide)
  - [Windows Setup (PowerShell)](#windows-setup-powershell)
  - [macOS Setup (Terminal / Homebrew)](#macos-setup-terminal--homebrew)
- [How to Use the Downloader](#-how-to-use-the-downloader)
- [Example Terminal Session](#-example-terminal-session)
- [Smart Features & Recovery](#-smart-features--recovery)
- [Playing Offline Music on Android & iOS](#-playing-offline-music-on-android--ios)
  - [Transferring to Android](#transferring-to-android)
  - [Transferring to iOS (iPhone & iPad)](#transferring-to-ios-iphone--ipad)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)
- [Advanced Customization](#-advanced-customization)
- [Legal & Usage Disclaimer](#-legal--usage-disclaimer)

---

## ✨ Key Features

- **Audio-Only Stream Extraction**: Directly downloads the audio stream without wasting bandwidth or time on unnecessary video streams.
- **Crystal-Clear MP3 Encoding**: Converts audio to standard **192 kbps MP3** (configurable) for maximum compatibility with all car stereos, Windows media players, and Android music apps.
- **Preserves Playlist Order**: Prepend files with zero-padded numbers (e.g., `001 - Song Title.mp3`, `002 - Song Title.mp3`) so tracks play in their exact playlist order anywhere.
- **Embedded Metadata**: Injects ID3 tags (Song Title, Artist, Album) straight into the MP3 file using FFmpeg.
- **Zero-Friction Resuming**: Tracks previously downloaded songs in a `download_archive.txt` file. If a download is stopped or interrupted, restarting the script instantly skips completed tracks.
- **Fault-Tolerant & Retry Mechanism**: If an individual song fails (e.g. temporary network blip or region lock), the script continues downloading the remaining tracks, shows a failure summary, and prompts you to retry failed songs.
- **Windows Path & Character Friendly**: Accepts paths with spaces, paths wrapped in quotes (from Windows *Copy as Path*), and handles Unicode/non-ASCII characters and emojis without crashes.

---

## 💻 Prerequisites

| Tool | Minimum Version | Purpose |
| :--- | :--- | :--- |
| **Python** | 3.11 or later | Executes the script (`playlist_downloader.py`) |
| **yt-dlp** | 2025.01.01+ | Fetches playlist metadata and downloads media streams |
| **FFmpeg** | Any modern build | Converts audio streams to MP3 and embeds ID3 tags |

---

## 🚀 Complete Installation & Setup Guide

Open **PowerShell** on Windows and follow these steps:

### Step 1: Verify Python
Make sure Python 3.11 or later is installed:
```powershell
python --version
```
*If Python is not installed or version is older than 3.11:*
- Install via Windows Package Manager:
  ```powershell
  winget install Python.Python.3.13
  ```
- Or download the installer directly from [python.org](https://www.python.org/downloads/) (make sure to check **"Add python.exe to PATH"**).

---

### Step 2: Create a Virtual Environment
Navigate to this project folder in PowerShell:
```powershell
cd "c:\Users\Victus\OneDrive\Documents\personal\projects\extra-projects\music-playlist-downloader"
```

Create and activate a virtual environment to keep packages isolated:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note**: If PowerShell shows an error like `running scripts is disabled on this system`, run this command to temporarily allow script execution in your session:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

---

### Step 3: Install Python Dependencies
Install `yt-dlp` using the provided `requirements.txt`:
```powershell
pip install -r requirements.txt
```

---

### Step 4: Install FFmpeg
FFmpeg is required to convert downloaded audio streams to MP3 files and attach metadata tags.

#### Recommended Method: WinGet
Run this command in PowerShell:
```powershell
winget install Gyan.FFmpeg
```

#### ⚠️ Important Note on Windows PATH Refresh:
When WinGet installs FFmpeg, newly added PATH entries are not visible to the current terminal session until PATH is refreshed.

Run this quick command in your PowerShell window to refresh PATH immediately without restarting:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
```

*(Note: Even if you do not refresh PATH, `playlist_downloader.py` includes a built-in search that automatically locates your WinGet FFmpeg installation!)*

---

### Step 5: Verify Your Installation
Run these commands to verify that all tools are working:

```powershell
python --version
ffmpeg -version
yt-dlp --version
```
Each command should return a version number without any error messages.

---

### macOS Setup (Terminal / Homebrew)

The script runs identically on **macOS**. If you are on a Mac:

1. Install prerequisites via [Homebrew](https://brew.sh/):
   ```bash
   brew install python ffmpeg
   ```
2. Set up virtual environment and dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python3 playlist_downloader.py
   ```

---

## 🎧 How to Use the Downloader

### Quick Start (One-Click Launchers)
- **On Windows**: Double-click [`run.bat`](file:///c:/Users/Victus/OneDrive/Documents/personal/projects/extra-projects/music-playlist-downloader/run.bat) (or run `.\run.bat` in PowerShell). It verifies Python, installs dependencies if missing, and starts the downloader automatically!
- **On Mac / Linux**: Run `./run.sh` in Terminal.

---

### Running via Terminal / Command Line
Make sure your virtual environment is active (or call Python directly from `.venv`):

```powershell
python playlist_downloader.py
```
*Alternatively, run directly via the virtual environment executable:*
```powershell
.\.venv\Scripts\python playlist_downloader.py
```

---

### Input Prompts Explained

#### 1. YouTube Playlist URL
When prompted:
```text
Enter YouTube Playlist URL (or 'q' to quit):
```
Paste any public or unlisted YouTube playlist or video URL. Supported formats include:
- Standard Playlist: `https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxx`
- YouTube Music Playlist: `https://music.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxx`
- Video inside a Playlist: `https://www.youtube.com/watch?v=xxxxxx&list=PLxxxxxxxxxxxxxxxx`
- Single Video: `https://www.youtube.com/watch?v=xxxxxx` (processed cleanly as a 1-track download)

#### 2. Destination Folder
When prompted:
```text
Enter destination folder [Press Enter for default: 'C:\...\downloads']:
> 
```
- **Option A (Default)**: Press **Enter** to save songs in a `downloads` subfolder inside the project.
- **Option B (Custom Folder)**: Type or paste any folder path.
  - Windows paths with spaces are fully supported: `D:\Music\Favorite Songs`
  - Quoted paths copied from Windows File Explorer (*Copy as Path*) work out of the box: `"C:\Users\Victus\Music\Roadtrip 2026"`
  - If the directory does not exist, the script creates it automatically.

---

## 🖥️ Example Terminal Session

```text
============================================================
         YouTube Playlist Audio Downloader (MP3)          
============================================================
Download high-quality MP3 tracks from any YouTube playlist
Preserves track order, embeds metadata, and skips duplicates.

============================================================
=============== Checking System Dependencies ===============
============================================================
[*] Python version: 3.13.4 -> [OK]
[*] yt-dlp version: 2026.08.19 -> [OK]
[*] FFmpeg detected: C:\Users\Victus\AppData\Local\Microsoft\WinGet\Links\ffmpeg.EXE -> [OK]

Enter YouTube Playlist URL (or 'q' to quit): https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj

Enter destination folder [Press Enter for default: 'C:\...\music-playlist-downloader\downloads']:
> "D:\Music\Pop Favorites"
[+] Destination folder ready: D:\Music\Pop Favorites

[*] Connecting to YouTube and fetching playlist details...

------------------------------------------------------------
 Playlist : Pop Music Playlist - Timeless Pop Songs
 Total    : 200 track(s) found
 Save to  : D:\Music\Pop Favorites
 Format   : MP3 @ 192 kbps
------------------------------------------------------------

Starting download process...

[1/200] 001 - ROSÉ & Bruno Mars - APT.
    [Downloading] 100.0% | Speed: 5.2MiB/s | ETA: 00:00
    [Processing] Download finished. Converting to MP3 & embedding metadata...
    [SUCCESS] Finished and saved as MP3.

[2/200] 002 - Lady Gaga, Bruno Mars - Die With A Smile
    [Downloading] 100.0% | Speed: 4.9MiB/s | ETA: 00:00
    [Processing] Download finished. Converting to MP3 & embedding metadata...
    [SUCCESS] Finished and saved as MP3.

[3/200] 003 - Sabrina Carpenter - Espresso
    [SKIPPED] Already downloaded (recorded in archive).

============================================================
================ Download Session Summary ==================
============================================================
  Total tracks in playlist : 200
  Successfully downloaded  : 2
  Already existed (skipped): 1
  Failed tracks            : 0
============================================================

[SUCCESS] All tracks are up to date and downloaded successfully!

All done! Enjoy your music offline.
```

---

## 🧠 Smart Features & Recovery

### 1. Resuming Interrupted Downloads
If your computer disconnects, your Wi-Fi drops, or you press `Ctrl + C` to stop:
1. Rerun the script: `python playlist_downloader.py`
2. Enter the same playlist URL and the same destination folder.
3. The script reads the archive and **immediately skips all completed tracks**, picking up right where it left off.

### 2. Duplicate Prevention (`download_archive.txt`)
Inside your destination folder, the script automatically maintains a `download_archive.txt` file storing YouTube video IDs.
- Tracks recorded in this file are never downloaded twice.
- If the owner of the playlist adds new songs to the playlist in the future, simply run the script pointing to the same folder: **only the new songs will be downloaded**.

### 3. Automatic Retry for Failed Tracks
If an individual video fails due to a network glitch:
- The script logs the error, continues to the next song, and maintains a list of failed tracks.
- At the end of the run, if any songs failed, you will see:
  ```text
  Would you like to retry the 2 failed track(s) now? (y/N): y
  ```
- Typing `y` immediately attempts downloading only the failed tracks.

### 4. Auto-Detection of WinGet FFmpeg
If FFmpeg was installed using WinGet (`winget install Gyan.FFmpeg`) but PowerShell has not refreshed its PATH variables, the script automatically scans the `%LOCALAPPDATA%\Microsoft\WinGet\Links\` directory and links `ffmpeg.exe` and `ffprobe.exe` into the execution path on the fly.

---

## 📱 Playing Offline Music on Android & iOS

### Transferring to Android
1. Connect your Android phone to your PC/Mac with a USB cable.
2. Select **File Transfer / MTP** in the Android notification panel.
3. In File Explorer (or Android File Transfer on Mac), open your phone's **`Music`** folder.
4. Copy the downloaded playlist folder over.
5. Recommended Android offline players: **Musicolet**, **VLC**, **Retro Music**, **Poweramp**.

---

### Transferring to iOS (iPhone & iPad)

Because the files are standard MP3s with embedded ID3 metadata tags (Title, Artist, Album), iOS plays them natively. You can use any of these straightforward methods:

#### Method 1: Using AirDrop (Fastest from Mac)
1. Select the downloaded MP3 files or folder on your Mac.
2. Right-click $\rightarrow$ **Share** $\rightarrow$ **AirDrop** $\rightarrow$ select your iPhone or iPad.
3. On your iPhone, open them in **Files** or **VLC for Mobile**.

#### Method 2: Cloud Sync (iCloud Drive / Google Drive / OneDrive)
1. Copy the downloaded MP3 folder into your **iCloud Drive**, **Google Drive**, or **OneDrive**.
2. On your iPhone, open the **Files** app (or Google Drive/OneDrive app).
3. The songs can be played directly offline or downloaded to local storage.

#### Method 3: Using Free Offline Player Apps (VLC / Documents by Readdle)
- Download **VLC for Mobile** or **Documents by Readdle** from the iOS App Store.
- Both apps offer **Wi-Fi Sharing**: they provide a local URL (e.g. `http://192.168.1.50`) that you can open in your computer browser to drag-and-drop the MP3 files straight onto your iPhone without any cables or iTunes!

#### Method 4: Syncing via Apple Music / iTunes
- **On Mac**: Drag the downloaded MP3 folder into the **Apple Music** app, connect your iPhone via cable, open **Finder**, click on your device, go to the **Music** tab, and click **Sync**.
- **On Windows**: Open iTunes (or Apple Devices app), add the MP3 folder to your Library (`File -> Add Folder to Library`), connect your iPhone, and click **Sync**.

---

## 🛠️ Troubleshooting & FAQs

### Q: `ffmpeg : The term 'ffmpeg' is not recognized` in PowerShell
**Cause**: WinGet installed FFmpeg, but your current terminal window hasn't reloaded the environment variables.  
**Fix**: Run this in PowerShell:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
```
Alternatively, restart your terminal or rely on the script's built-in WinGet auto-detection.

---

### Q: `File .venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled`
**Cause**: PowerShell's default execution policy restricts unsigned scripts.  
**Fix**: Run this command to enable script execution for your current session:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then run `.\.venv\Scripts\Activate.ps1` again.

---

### Q: How do I re-download a song if I deleted its MP3?
**Cause**: The video ID is recorded in `download_archive.txt`.  
**Fix**: 
1. Open `download_archive.txt` in your destination folder with Notepad.
2. Delete the line containing that video's ID, or delete `download_archive.txt` entirely if you want to re-download the entire playlist.
3. Rerun the script.

---

### Q: `ERROR: unable to download video data: HTTP Error 403: Forbidden`
**Cause**: YouTube's content delivery network (`googlevideo.com`) periodically blocks or throttles anonymous web media stream requests using anti-bot/Proof-of-Origin token checks (SABR streaming).

**How the script protects against this**:
1. **Built-in Mobile Player Clients**: The updated script automatically requests streams using YouTube's Android and iOS player endpoints (`android`, `ios`, `mweb`), which do not enforce the same strict web SABR 403 blocks.
2. **Automatic Fallback**: If a track triggers a 403, the script automatically retries that track with alternate player clients.
3. **Chunked Streaming**: Audio streams are requested in 10MB chunks to avoid TCP connection resets and CDN throttling.

**If you still encounter 403 on specific videos**:
- **Use Browser Cookies**: When starting the script, answer the optional prompt with your browser name (e.g. `chrome`, `edge`, `firefox`, `brave`, or `safari`). This authenticates the stream with your browser session and completely bypasses the 403 restriction.
- **Update yt-dlp**: YouTube continuously updates its streaming endpoints. Run:
  ```powershell
  pip install --upgrade yt-dlp
  ```

---

### Q: Does this download age-restricted or private videos?
- **Private / Deleted videos**: Skipped automatically with a clean notification.
- **Age-restricted videos**: YouTube requires authentication cookies for age-gated media. Simply type `chrome` or `edge` when prompted for browser cookies at script startup.

---

## ⚙️ Advanced Customization

You can tweak settings at the top of [playlist_downloader.py](file:///c:/Users/Victus/OneDrive/Documents/personal/projects/extra-projects/music-playlist-downloader/playlist_downloader.py):

- **Change Default Audio Bitrate**:
  Change line 47:
  ```python
  DEFAULT_BITRATE = "192"  # Change to "320" for 320 kbps or "128" for smaller file size
  ```
- **Change Default Output Folder**:
  In `get_destination_folder()`, change:
  ```python
  default_dir = os.path.abspath(os.path.join(".", "downloads"))
  ```
  to any preferred default path (e.g., `os.path.expanduser("~/Music/YouTube")`).

---

## ⚖️ Legal & Usage Disclaimer

This tool is created for personal, offline educational and archival purposes. Download content only if you own the rights to it, have authorization from the copyright holder, or if the media is licensed under Creative Commons / Public Domain. Respect YouTube's Terms of Service and applicable local copyright laws.
