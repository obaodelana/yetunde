import concurrent.futures
from typing import List, Dict, Any, Optional

from .enums import AudioQuality, VideoQuality, AudioFormat, VideoFormat
from .core import audio_download, video_download, download

def _run_bulk(func, urls: List[str], **kwargs) -> Dict[str, Any]:
    results = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # submit tasks
        future_to_url = {executor.submit(func, url, **kwargs): url for url in urls}

        # collect results as they complete
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                results[url] = {"status": "success", "data": data}
            except Exception as exc:
                results[url] = {"status": "error", "error": str(exc)}

    return results

def bulk_audio_download(
    urls: List[str],
    format: AudioFormat = AudioFormat.MP3,
    quality: AudioQuality = AudioQuality.HIGH,
    *,
    filename: Optional[str] = None,
    retries: int = 3
) -> Dict[str, Any]:
    return _run_bulk(
        audio_download,
        urls,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries
    )

def bulk_video_download(
    urls: List[str],
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3
) -> Dict[str, Any]:
    return _run_bulk(
        video_download,
        urls,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries
    )

def bulk_download(
    urls: List[str],
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3
) -> Dict[str, Any]:
    return _run_bulk(
        download,
        urls,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries
    )
