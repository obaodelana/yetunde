from typing import Optional, Union, List

from .enums import AudioQuality, VideoQuality, AudioFormat, VideoFormat
from .core import (
    _dispatch_download,
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
    return _dispatch_download(
        url,
        _audio_download_single,
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
    return _dispatch_download(
        url,
        _video_download_single,
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
    return _dispatch_download(
        url,
        _download_single,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries,
        playlist=playlist
    )
