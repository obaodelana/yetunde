from typing import Optional, Union, List

from .enums import AudioQuality, VideoQuality, AudioFormat, VideoFormat
from .core import (
    _handle_url_input,
    _run_bulk_gen,
    _audio_download_single,
    _video_download_single,
    _download_single
)

def audio_download(
    url: Union[str, List[str]],
    *,
    format: AudioFormat = AudioFormat.MP3,
    quality: AudioQuality = AudioQuality.HIGH,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
):
    urls = _handle_url_input(url)
    if isinstance(url, list):
        return _run_bulk_gen(
            _audio_download_single,
            urls,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            playlist=playlist
        )
    return _audio_download_single(
        url,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries,
        playlist=playlist
    )

def video_download(
    url: Union[str, List[str]],
    *,
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
):
    urls = _handle_url_input(url)
    if isinstance(url, list):
        return _run_bulk_gen(
            _video_download_single,
            urls,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            playlist=playlist
        )
    return _video_download_single(
        url,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries,
        playlist=playlist
    )

def download(
    url: Union[str, List[str]],
    *,
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
):
    urls = _handle_url_input(url)
    if isinstance(url, list):
        return _run_bulk_gen(
            _download_single,
            urls,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            playlist=playlist
        )
    return _download_single(
        url,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries,
        playlist=playlist
    )
