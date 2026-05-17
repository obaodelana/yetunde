# yetunde

`yetunde` is a Python meta-package built around `yt-dlp` designed to simplify downloading YouTube videos, audio, or a merged format with support for retries, formatting, concurrent bulk downloading, and more.

## Installation

You can install the package using `uv` (recommended) or `pip`:

```bash
uv add yetunde
# or
pip install yetunde
```

## Usage

### Simple & Bulk Downloads

The core interface provides three main functions that accept either a single URL string or a list of URL strings.

- **Single URL:** Returns a simplified dictionary with key metadata:
  ```python
  {
      "quality": "1080p",  # or bitrate e.g., "320kbps"
      "path": "/path/to/file.mp4",
      "url": "https://..."
  }
  ```
- **Multiple URLs (Bulk):** Returns an **async generator** yielding each video as it finishes downloading. This allows real-time iteration (`async for ...`) without waiting for all downloads to complete.

All functions accept an optional `filename` using `yt-dlp` formatting, an optional `retries` parameter (defaults to 3), and a `quiet` boolean to suppress `yt-dlp`'s verbose output and keep your terminal clean (defaults to `True`).

Playlists and channels are **automatically detected and downloaded concurrently** using the async generator.

```python
import asyncio
from yetunde import (
    audio_download,
    video_download,
    download,
    AudioQuality,
    VideoQuality,
    AudioFormat,
    VideoFormat
)

# Single URL download
result = audio_download(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    format=AudioFormat.MP3,
    quality=AudioQuality.HIGH
)
print(result["path"])  # Path to the downloaded file

# Bulk download with async generator
async def main():
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=another-video"
    ]
    
    async for video in download(urls, format=VideoFormat.MP4, quality=VideoQuality.RES_1080P):
        if video.get("status") == "error":
            print(f"Failed to download {video['url']}: {video['error']}")
        else:
            print(f"Successfully downloaded {video['url']} to {video['path']} ({video['quality']})")

asyncio.run(main())

# Playlist / Channel support (automatically detects and returns an async generator yielding downloads in real time):
async def main():
    async for video in download("https://www.youtube.com/playlist?list=..."):
        if video.get("status") == "error":
            print(f"Failed to download {video['url']}: {video['error']}")
        else:
            print(f"Downloaded {video['url']} to {video['path']}")

asyncio.run(main())
```

### Error Handling

If there are download issues, `yetunde` will raise a `YetundeError`. The exception object contains helpful fields:
- `url`: The URL that caused the error.
- `error_type`: E.g., 'download' or 'extraction'.
- `original_error`: The original exception raised by `yt-dlp`.
- `message`: A descriptive error message.
