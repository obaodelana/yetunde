from typing import List, Dict, Any, Optional

from .enums import AudioQuality, VideoQuality, AudioFormat, VideoFormat
from .core import audio_download, video_download, download

def bulk_audio_download(
    urls: List[str],
    format: AudioFormat = AudioFormat.MP3,
    quality: AudioQuality = AudioQuality.HIGH,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Dict[str, Any]:
    return audio_download(
        urls,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries,
        playlist=playlist
    )

def bulk_video_download(
    urls: List[str],
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Dict[str, Any]:
    return video_download(
        urls,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries,
        playlist=playlist
    )

def bulk_download(
    urls: List[str],
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Dict[str, Any]:
    return download(
        urls,
        format=format,
        quality=quality,
        filename=filename,
        retries=retries,
        playlist=playlist
    )
