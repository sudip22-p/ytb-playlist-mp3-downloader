"""
YouTube Playlist Audio Downloader
=================================
A reliable, cross-platform Python script (Windows, macOS, Linux) to download audio tracks
from a YouTube playlist and save them locally as MP3 files for offline playback on
Windows, macOS, Android, and iOS devices.

Features:
- Downloads highest quality audio stream without downloading video.
- Converts audio to MP3 at 192 kbps using FFmpeg.
- Saves clean filenames using the song title (e.g. 'Song Title.mp3') without numeric prefixes.
- Embeds track metadata (title, artist, album) into the MP3 tags.
- Built-in Anti-403 Protection: Uses mobile/embedded player clients (Android, iOS)
  and chunked streaming to avoid YouTube 'HTTP Error 403: Forbidden'.
- Optional Browser Cookie Support: Unlocks age-restricted or strictly protected tracks.
- Prevents duplicate downloads via a persistent archive file (supports resume).
- Handles errors gracefully, continuing to the next track if one fails.
- Displays download progress and a final success/failure summary.
- Provides an interactive retry prompt for failed tracks.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure UTF-8 output encoding on Windows consoles to prevent charmap encoding errors
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yt_dlp
except ImportError:
    print("\n[ERROR] 'yt-dlp' is not installed.")
    print("Please install it using pip:")
    print("    pip install -r requirements.txt")
    print("or:")
    print("    pip install yt-dlp\n")
    sys.exit(1)


ARCHIVE_FILENAME = "download_archive.txt"
DEFAULT_BITRATE = "192"

# Player clients used to bypass YouTube anti-bot & 403 Forbidden SABR stream restrictions
DEFAULT_PLAYER_CLIENTS = ["android", "ios", "mweb", "web"]
FALLBACK_PLAYER_CLIENTS = ["ios", "web_embedded", "mweb"]


def ensure_ffmpeg_in_path() -> Optional[str]:
    """
    Ensure FFmpeg and ffprobe are discoverable in PATH.
    Automatically searches OS-specific directories:
    - Windows: WinGet Links (%LOCALAPPDATA%\\Microsoft\\WinGet\\Links) & Packages
    - macOS: Apple Silicon (/opt/homebrew/bin) & Intel (/usr/local/bin)
    - Linux: Standard bin directories
    - Script directory
    """
    # 1. Already in PATH?
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # 2. Windows: Check WinGet Links and user directories
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            winget_links = os.path.join(local_app_data, "Microsoft", "WinGet", "Links")
            if os.path.isdir(winget_links) and os.path.exists(os.path.join(winget_links, "ffmpeg.exe")):
                os.environ["PATH"] = winget_links + os.pathsep + os.environ.get("PATH", "")
                return shutil.which("ffmpeg")

    # 3. macOS & Linux: Check Homebrew and common Unix directories
    elif sys.platform == "darwin" or sys.platform.startswith("linux"):
        common_paths = [
            "/opt/homebrew/bin",  # Apple Silicon Mac (Homebrew)
            "/usr/local/bin",     # Intel Mac (Homebrew) / Linux
            "/usr/bin",
            os.path.expanduser("~/.local/bin"),
        ]
        for p in common_paths:
            candidate = os.path.join(p, "ffmpeg")
            if os.path.exists(candidate) and os.access(candidate, os.X_OK):
                os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
                return candidate

    # 4. Check current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for binary in ("ffmpeg.exe", "ffmpeg"):
        local_ffmpeg = os.path.join(script_dir, binary)
        if os.path.exists(local_ffmpeg):
            os.environ["PATH"] = script_dir + os.pathsep + os.environ.get("PATH", "")
            return local_ffmpeg

    return None


def check_dependencies() -> bool:
    """
    Check if Python version and required external tools (FFmpeg) are present.
    Returns True if all required dependencies are met, or False if critical tools are missing.
    """
    print("\n" + "=" * 60)
    print(" Checking System Dependencies ".center(60, "="))
    print("=" * 60)

    # 1. Check Python version (>= 3.11 recommended)
    py_version = sys.version_info
    print(f"[*] Python version: {py_version.major}.{py_version.minor}.{py_version.micro}", end="")
    if py_version < (3, 11):
        print(" -> [WARNING] Python 3.11 or newer is recommended.")
    else:
        print(" -> [OK]")

    # 2. Check yt-dlp
    print(f"[*] yt-dlp version: {yt_dlp.version.__version__} -> [OK]")

    # 3. Check FFmpeg
    ffmpeg_path = ensure_ffmpeg_in_path()
    if ffmpeg_path:
        print(f"[*] FFmpeg detected: {ffmpeg_path} -> [OK]")
        return True

    print("\n[!] FFmpeg was NOT found on your system.")
    print("-" * 60)
    print("FFmpeg is required to extract audio and convert it to MP3.")
    print("Without FFmpeg, downloads will fail during the audio conversion step.")

    if sys.platform == "win32":
        print("\nHow to install FFmpeg on Windows:")
        print("  Run in PowerShell:")
        print("      winget install Gyan.FFmpeg")
        print("  Then close and reopen PowerShell.")
    elif sys.platform == "darwin":
        print("\nHow to install FFmpeg on macOS:")
        print("  Run in Terminal (using Homebrew):")
        print("      brew install ffmpeg")
    else:
        print("\nHow to install FFmpeg on Linux:")
        print("  Ubuntu/Debian:  sudo apt install ffmpeg")
        print("  Fedora:         sudo dnf install ffmpeg")
        print("  Arch:           sudo pacman -S ffmpeg")
    print("-" * 60)

    try:
        user_choice = input("\nDo you want to continue anyway? (y/N): ").strip().lower()
        return user_choice in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled by user.")
        return False


def get_playlist_url() -> str:
    """
    Prompt the user to enter a valid YouTube URL (playlist or single video).
    Handles extra whitespace, quotation marks, and allows choosing between
    the entire playlist or just the single video if both are in the URL.
    """
    while True:
        try:
            raw_url = input("\nEnter YouTube URL (Playlist or Single Video, 'q' to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        url = raw_url.strip("'\"").strip()

        if not url:
            print("[!] URL cannot be empty. Please enter a valid URL.")
            continue

        if url.lower() in ("q", "quit", "exit"):
            print("Exiting.")
            sys.exit(0)

        # Basic validation: ensure it looks like a YouTube URL
        if not ("youtube.com" in url.lower() or "youtu.be" in url.lower()):
            print("[!] That does not look like a YouTube URL.")
            print("    Examples:")
            print("      Playlist: https://www.youtube.com/playlist?list=PL...")
            print("      Single:   https://www.youtube.com/watch?v=...")
            retry = input("    Use this URL anyway? (y/N): ").strip().lower()
            if retry not in ("y", "yes"):
                continue

        # Check if URL contains both a specific video and a playlist parameter
        has_video = ("watch?v=" in url or "youtu.be/" in url) and ("list=" in url)
        if has_video:
            print("\n[?] This URL points to a specific video inside a playlist:")
            print("    [1] Download the ENTIRE playlist (Default)")
            print("    [2] Download ONLY this single song")
            try:
                choice = input("    Choose option [1/2, default: 1]: ").strip()
            except (KeyboardInterrupt, EOFError):
                choice = "1"
            if choice == "2":
                # Remove &list=... or ?list=... to download only the single track
                url = re.sub(r"[?&]list=[^&]+", "", url)
                if "?" not in url and "&" in url:
                    url = url.replace("&", "?", 1)
                print("    -> Selected: Single song only.")
            else:
                print("    -> Selected: Entire playlist.")

        return url


def get_destination_folder() -> str:
    """
    Prompt the user for a destination folder path.
    Supports paths with spaces and enclosed in quotation marks.
    Creates the directory if it does not exist.
    """
    default_dir = os.path.abspath(os.path.join(".", "downloads"))

    while True:
        try:
            prompt = f"\nEnter destination folder [Press Enter for default: '{default_dir}']:\n> "
            raw_input = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        if not raw_input:
            target_path = default_dir
        else:
            cleaned_path = raw_input.strip("'\"").strip()
            expanded_path = os.path.expandvars(os.path.expanduser(cleaned_path))
            target_path = os.path.abspath(expanded_path)

        # Create destination folder if it doesn't exist
        try:
            os.makedirs(target_path, exist_ok=True)
            # Verify write permissions by touching a temporary file
            test_file = os.path.join(target_path, ".test_write_perm.tmp")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("test")
            os.remove(test_file)
            print(f"[+] Destination folder ready: {target_path}")
            return target_path
        except Exception as err:
            print(f"[!] Cannot use folder '{target_path}': {err}")
            print("    Please enter a valid, writable path.")


def get_browser_cookies_preference() -> Optional[str]:
    """
    Prompt the user if they want to load cookies from an installed browser.
    Helps resolve HTTP 403 Forbidden errors and unlock age-restricted tracks.
    """
    print("\n" + "-" * 60)
    print(" Browser Cookies (Optional) ".center(60, "-"))
    print("If you encounter 'HTTP 403 Forbidden' errors or age-restricted")
    print("tracks, loading cookies from your browser can fix them.")
    print("-" * 60)
    try:
        prompt = "Load cookies from browser? [Press Enter to skip, or type chrome / edge / firefox / brave / safari]:\n> "
        choice = input(prompt).strip().lower()
    except (KeyboardInterrupt, EOFError):
        return None

    if choice in ("chrome", "edge", "firefox", "brave", "safari", "opera", "vivaldi"):
        print(f"[+] Using cookies from: {choice}")
        return choice
    return None


def fetch_playlist_info(
    playlist_url: str, browser_cookie: Optional[str] = None
) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Extract playlist metadata and track list without downloading the media files.
    Uses mobile player clients to avoid 403 Forbidden during metadata extraction.
    Returns a tuple of (playlist_title, list_of_track_info_dicts).
    """
    print("\n[*] Connecting to YouTube and fetching playlist details...")

    ydl_opts: Dict[str, Any] = {
        "extract_flat": True,     # Fast metadata extraction
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extractor_args": {
            "youtube": {
                "player_client": DEFAULT_PLAYER_CLIENTS,
            }
        },
    }

    if browser_cookie:
        ydl_opts["cookiesfrombrowser"] = (browser_cookie, None, None, None)

    js_runtimes = get_js_runtimes()
    if js_runtimes:
        ydl_opts["js_runtimes"] = js_runtimes

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
    except yt_dlp.utils.DownloadError as err:
        print(f"\n[!] Failed to load playlist: {err}")
        return None, []
    except Exception as err:
        print(f"\n[!] An unexpected error occurred while loading playlist: {err}")
        return None, []

    if not info:
        print("[!] No information could be retrieved for this URL.")
        return None, []

    playlist_title = info.get("title", "YouTube Playlist")
    raw_entries = info.get("entries")

    # If it's a single video rather than a playlist, treat as a 1-item list
    if raw_entries is None:
        track = {
            "id": info.get("id"),
            "title": info.get("title", "Unknown Title"),
            "url": info.get("webpage_url") or playlist_url,
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
        }
        return playlist_title, [track]

    # Filter out empty or unavailable entries (e.g. deleted/private videos)
    valid_entries: List[Dict[str, Any]] = []
    for entry in raw_entries:
        if not entry:
            continue
        title = entry.get("title", "")
        if title in ("[Private video]", "[Deleted video]"):
            continue
        track_id = entry.get("id")
        track_url = entry.get("url") or f"https://www.youtube.com/watch?v={track_id}"
        valid_entries.append({
            "id": track_id,
            "title": title or "Untitled Track",
            "url": track_url,
            "duration": entry.get("duration"),
            "uploader": entry.get("uploader"),
        })

    return playlist_title, valid_entries


def load_download_archive(archive_path: str) -> Set[str]:
    """
    Load previously downloaded video IDs from the archive file.
    yt-dlp formats archive lines as '<extractor> <id>', e.g. 'youtube dQw4w9WgXcQ'.
    """
    archived_ids: Set[str] = set()
    if os.path.exists(archive_path):
        try:
            with open(archive_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        archived_ids.add(parts[1])
                    elif len(parts) == 1:
                        archived_ids.add(parts[0])
        except Exception as err:
            print(f"[!] Warning: Could not read archive file ({err}).")
    return archived_ids


class ProgressTracker:
    """Tracks and formats progress output for yt-dlp downloads."""

    def __init__(self, track_display: str) -> None:
        self.track_display = track_display
        self._last_line_len = 0

    def hook(self, d: Dict[str, Any]) -> None:
        status = d.get("status")
        if status == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if total_bytes > 0:
                percent = (downloaded / total_bytes) * 100
                percent_str = f"{percent:5.1f}%"
            else:
                percent_str = d.get("_percent_str", "  N/A")

            speed_str = d.get("_speed_str", "N/A/s")
            eta_str = d.get("_eta_str", "N/A")

            msg = f"    [Downloading] {percent_str} | Speed: {speed_str} | ETA: {eta_str}"
            sys.stdout.write(f"\r{msg.ljust(self._last_line_len)}")
            sys.stdout.flush()
            self._last_line_len = len(msg)

        elif status == "finished":
            sys.stdout.write(f"\r{' ' * self._last_line_len}\r")
            sys.stdout.flush()
            print("    [Processing] Download finished. Converting to MP3 & embedding metadata...")


def get_js_runtimes() -> Dict[str, Any]:
    """Detect available JavaScript runtimes (Node.js, Deno) to solve YouTube challenges."""
    runtimes: Dict[str, Any] = {}
    if shutil.which("node"):
        runtimes["node"] = {}
    if shutil.which("deno"):
        runtimes["deno"] = {}
    return runtimes


def _build_ydl_options(
    outtmpl: str,
    archive_path: str,
    bitrate: str,
    player_clients: List[str],
    progress_hook: Any,
    browser_cookie: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to assemble yt-dlp configuration options with anti-403 defenses."""
    opts: Dict[str, Any] = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "download_archive": archive_path,
        "noplaylist": True,
        "windowsfilenames": True,
        "quiet": True,
        "no_warnings": True,
        # Network resilience & Anti-403 configurations
        "retries": 10,
        "fragment_retries": 10,
        "file_access_retries": 3,
        "socket_timeout": 30,
        "http_chunk_size": 10485760,  # 10MB chunks prevent CDN throttling / drops
        "extractor_args": {
            "youtube": {
                "player_client": player_clients,
            }
        },
        "progress_hooks": [progress_hook],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ],
    }

    # Attach JS runtime if available (e.g. Node.js on Windows) to solve YouTube challenge tokens
    js_runtimes = get_js_runtimes()
    if js_runtimes:
        opts["js_runtimes"] = js_runtimes

    if browser_cookie:
        opts["cookiesfrombrowser"] = (browser_cookie, None, None, None)

    return opts


def download_single_track(
    track_info: Dict[str, Any],
    track_number: int,
    total_tracks: int,
    destination_dir: str,
    archive_path: str,
    bitrate: str = DEFAULT_BITRATE,
    browser_cookie: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Download a single track using yt-dlp and extract audio to MP3.
    Includes an automatic fallback to alternate player clients if HTTP 403 occurs.

    Returns:
        (success: bool, error_message: Optional[str])
    """
    track_title = track_info.get("title", "Unknown Title")
    track_url = track_info.get("url")

    # Clean filename without numeric prefix (e.g. "Song Title.mp3")
    track_header = f"[{track_number}/{total_tracks}] {track_title}"
    outtmpl = os.path.join(destination_dir, "%(title)s.%(ext)s")

    print(f"\n{track_header}")
    tracker = ProgressTracker(track_header)

    # Attempt 1: Using Primary Mobile Player Clients (Android, iOS)
    ydl_opts = _build_ydl_options(
        outtmpl=outtmpl,
        archive_path=archive_path,
        bitrate=bitrate,
        player_clients=DEFAULT_PLAYER_CLIENTS,
        progress_hook=tracker.hook,
        browser_cookie=browser_cookie,
    )

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            exit_code = ydl.download([track_url])
            if exit_code == 0:
                print("    [SUCCESS] Finished and saved as MP3.")
                return True, None
    except Exception as exc:
        err_msg = str(exc)

        # If HTTP 403 Forbidden occurred, pause briefly and retry with alternate player client
        if "403" in err_msg or "Forbidden" in err_msg:
            print("    [!] HTTP 403 rate limit detected. Pausing 1.5s & retrying with alternate client...")
            time.sleep(1.5)
            fallback_opts = _build_ydl_options(
                outtmpl=outtmpl,
                archive_path=archive_path,
                bitrate=bitrate,
                player_clients=FALLBACK_PLAYER_CLIENTS,
                progress_hook=tracker.hook,
                browser_cookie=browser_cookie,
            )
            try:
                with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                    fallback_exit = ydl.download([track_url])
                    if fallback_exit == 0:
                        print("    [SUCCESS] Fallback succeeded! Saved as MP3.")
                        return True, None
            except Exception as fallback_exc:
                err_msg = str(fallback_exc)

        print(f"    [FAILED] Error: {err_msg}")
        return False, err_msg

    return False, "Unknown download failure"


def display_summary(
    total_tracks: int,
    successful_tracks: List[str],
    skipped_tracks: List[str],
    failed_tracks: List[Tuple[int, str, str]],
) -> None:
    """Print a clear summary of the download session."""
    print("\n" + "=" * 60)
    print(" Download Session Summary ".center(60, "="))
    print("=" * 60)
    print(f"  Total tracks in playlist : {total_tracks}")
    print(f"  Successfully downloaded  : {len(successful_tracks)}")
    print(f"  Already existed (skipped): {len(skipped_tracks)}")
    print(f"  Failed tracks            : {len(failed_tracks)}")
    print("=" * 60)

    if failed_tracks:
        print("\n[!] The following tracks encountered errors:")
        for track_num, title, err in failed_tracks:
            print(f"    - Track {track_num}: {title}")
            print(f"      Reason: {err}")
        print("\nNote: You can run the script again to resume; successfully")
        print("downloaded tracks will be preserved and not re-downloaded.")
    else:
        print("\n[SUCCESS] All tracks are up to date and downloaded successfully!")


def retry_failed_tracks_prompt(
    failed_tracks: List[Tuple[int, str, str]],
    all_tracks: List[Dict[str, Any]],
    destination_dir: str,
    archive_path: str,
    successful_tracks: List[str],
    current_browser: Optional[str],
) -> None:
    """Ask the user if they want to retry failed tracks and re-attempt downloads."""
    if not failed_tracks:
        return

    try:
        choice = input(f"\nWould you like to retry the {len(failed_tracks)} failed track(s) now? (y/N): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return

    if choice not in ("y", "yes"):
        return

    # If any error was 403 and no browser cookie was used, suggest loading browser cookies
    has_403 = any("403" in err for _, _, err in failed_tracks)
    retry_browser = current_browser
    if has_403 and not current_browser:
        print("\nSome tracks failed with HTTP 403 Forbidden.")
        print("Using browser cookies can authenticate the stream and solve this.")
        try:
            browser_input = input("Use cookies from a browser for retry? [Press Enter to skip, or chrome/edge/firefox]: ").strip().lower()
            if browser_input in ("chrome", "edge", "firefox", "brave", "safari"):
                retry_browser = browser_input
        except (KeyboardInterrupt, EOFError):
            pass

    print("\n[*] Retrying failed tracks...")
    still_failed: List[Tuple[int, str, str]] = []

    for track_num, title, _ in failed_tracks:
        idx = track_num - 1
        if 0 <= idx < len(all_tracks):
            track_info = all_tracks[idx]
            success, err_msg = download_single_track(
                track_info=track_info,
                track_number=track_num,
                total_tracks=len(all_tracks),
                destination_dir=destination_dir,
                archive_path=archive_path,
                browser_cookie=retry_browser,
            )
            if success:
                successful_tracks.append(title)
            else:
                still_failed.append((track_num, title, err_msg or "Unknown error"))

    if still_failed:
        print(f"\n[!] Retry complete. {len(still_failed)} track(s) still could not be downloaded.")
    else:
        print("\n[SUCCESS] All retried tracks were downloaded successfully!")


def main() -> None:
    """Main program entry point."""
    print("=" * 60)
    print(" YouTube Playlist Audio Downloader (MP3) ".center(60, "="))
    print("=" * 60)
    print("Universal Cross-Platform Downloader (Windows, macOS, Linux)")
    print("Preserves track order, embeds metadata, and skips duplicates.")

    # 1. Dependency checks
    if not check_dependencies():
        print("\nCannot proceed without dependencies. Exiting.")
        sys.exit(1)

    # 2. Get user inputs
    playlist_url = get_playlist_url()
    destination_dir = get_destination_folder()
    browser_cookie = get_browser_cookies_preference()
    archive_path = os.path.join(destination_dir, ARCHIVE_FILENAME)

    # 3. Fetch playlist track details
    playlist_title, tracks = fetch_playlist_info(playlist_url, browser_cookie=browser_cookie)
    if not tracks:
        print("[!] No downloadable tracks found. Please check the URL and your network connection.")
        sys.exit(1)

    total_tracks = len(tracks)
    print("\n" + "-" * 60)
    if total_tracks == 1:
        print(f" Track    : {tracks[0].get('title', playlist_title)}")
        print(f" Mode     : Single Video / Song Download")
    else:
        print(f" Playlist : {playlist_title}")
        print(f" Total    : {total_tracks} track(s) found")
    print(f" Save to  : {destination_dir}")
    print(f" Format   : MP3 @ {DEFAULT_BITRATE} kbps")
    if browser_cookie:
        print(f" Cookies  : Enabled ({browser_cookie})")
    print("-" * 60)

    # 4. Load download archive for fast duplicate skipping
    archived_ids = load_download_archive(archive_path)

    successful_tracks: List[str] = []
    skipped_tracks: List[str] = []
    failed_tracks: List[Tuple[int, str, str]] = []

    # 5. Process tracks sequentially, one at a time
    padding_width = max(3, len(str(total_tracks)))
    print("\nStarting download process...")

    for index, track in enumerate(tracks, start=1):
        track_id = track.get("id")
        track_title = track.get("title", f"Track {index}")

        # Check if already in download archive
        if track_id and track_id in archived_ids:
            print(f"\n[{index}/{total_tracks}] {track_title}")
            print("    [SKIPPED] Already downloaded (recorded in archive).")
            skipped_tracks.append(track_title)
            continue

        # Download track
        success, error_msg = download_single_track(
            track_info=track,
            track_number=index,
            total_tracks=total_tracks,
            destination_dir=destination_dir,
            archive_path=archive_path,
            browser_cookie=browser_cookie,
        )

        if success:
            successful_tracks.append(track_title)
            if track_id:
                archived_ids.add(track_id)
        else:
            failed_tracks.append((index, track_title, error_msg or "Unknown error"))

        # Small pause between tracks to be polite to the host server
        time.sleep(0.5)

    # 6. Display final summary
    display_summary(total_tracks, successful_tracks, skipped_tracks, failed_tracks)

    # 7. Offer retry for failed tracks
    if failed_tracks:
        retry_failed_tracks_prompt(
            failed_tracks=failed_tracks,
            all_tracks=tracks,
            destination_dir=destination_dir,
            archive_path=archive_path,
            successful_tracks=successful_tracks,
            current_browser=browser_cookie,
        )

    print("\nAll done! Enjoy your music offline.")


if __name__ == "__main__":
    main()
