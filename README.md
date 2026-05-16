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

The core interface provides three main functions that accept either a single URL string or a list of URL strings. When a list is provided, downloads happen concurrently. All functions accept an optional `filename` using `yt-dlp` formatting, an optional `retries` parameter (defaults to 3), and a `playlist` boolean to enable/disable playlist support (defaults to `True`).

```python
from yetunde import (
    audio_download,
    video_download,
    download,
    AudioQuality,
    VideoQuality,
    AudioFormat,
    VideoFormat
)

# Single URL: returns the download info dictionary
result = audio_download(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    format=AudioFormat.MP3,
    quality=AudioQuality.HIGH
)

# Multiple URLs: returns a dictionary of results keyed by URL
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=another-video"
]
results = download(urls, format=VideoFormat.MP4, quality=VideoQuality.RES_1080P)

for url, res in results.items():
    if res["status"] == "success":
        print(f"Downloaded {url}")
    else:
        print(f"Error {url}: {res['error']}")

# Playlist support: Enabled by default
result = download("https://www.youtube.com/playlist?list=...", playlist=True)
```

### Legacy Bulk Functions

For backward compatibility, the `bulk_*` functions are still available and now simply wrap the unified functions.

### Error Handling

If there are download issues, `yetunde` will raise a `YetundeError`. The exception object contains helpful fields:
- `url`: The URL that caused the error.
- `error_type`: E.g., 'download' or 'extraction'.
- `original_error`: The original exception raised by `yt-dlp`.
- `message`: A descriptive error message.
