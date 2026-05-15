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

### Simple Downloads

The core interface provides three main functions depending on what you want to download. All functions accept an optional `filename` using `yt-dlp` formatting, and an optional `retries` parameter (defaults to 3).

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

# Download an audio file (default is high quality MP3)
result = audio_download(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    format=AudioFormat.MP3,
    quality=AudioQuality.HIGH
)

# Download video only (without audio)
result = video_download(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    format=VideoFormat.MP4,
    quality=VideoQuality.RES_1080P
)

# Download merged video and audio
result = download(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    format=VideoFormat.MKV,
    quality=VideoQuality.RES_720P,
    filename="%(title)s.%(ext)s",
    retries=5
)
```

### Bulk Downloads

You can download multiple URLs concurrently. The functions will return a dictionary summarizing the success or error for each URL.

```python
from yetunde import bulk_download

urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=badurl"
]

results = bulk_download(urls)

for url, result in results.items():
    if result["status"] == "success":
        print(f"Successfully downloaded {url}")
    else:
        print(f"Failed to download {url}: {result['error']}")
```

### Error Handling

If there are download issues, `yetunde` will raise a `YetundeError`. The exception object contains helpful fields:
- `url`: The URL that caused the error.
- `error_type`: E.g., 'download' or 'extraction'.
- `original_error`: The original exception raised by `yt-dlp`.
- `message`: A descriptive error message.
