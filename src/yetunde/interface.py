from typing import Optional, Union, List, Any

from .enums import AudioQuality, VideoQuality, AudioFormat, VideoFormat
from .core import (
    _run_bulk_gen,
    _expand_playlist,
    _audio_download_single,
    _video_download_single,
    _download_single
)


def _handle_url_input(url: Any) -> List[str]:
    if isinstance(url, str):
        return [url]
    if isinstance(url, list):
        if not all(isinstance(u, str) for u in url):
            raise ValueError("All items in the list must be strings")
        return url
    raise ValueError("url must be a string or a list of strings")


def audio_download(
    url: Union[str, List[str]],
    *,
    format: AudioFormat = AudioFormat.MP3,
    quality: AudioQuality = AudioQuality.HIGH,
    filename: Optional[str] = None,
    retries: int = 3,
    quiet: bool = True
):
    if isinstance(url, list):
        urls = _handle_url_input(url)
        return _run_bulk_gen(
            _audio_download_single,
            urls,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            quiet=quiet
        )
    if isinstance(url, str):
        expanded_urls, is_playlist = _expand_playlist(url, quiet=quiet)
        if is_playlist:
            return _run_bulk_gen(
                _audio_download_single,
                expanded_urls,
                format=format,
                quality=quality,
                filename=filename,
                retries=retries,
                quiet=quiet
            )
        return _audio_download_single(
            url,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            quiet=quiet
        )
    raise ValueError("url must be a string or a list of strings")


def video_download(
    url: Union[str, List[str]],
    *,
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    filename: Optional[str] = None,
    retries: int = 3,
    quiet: bool = True
):
    if isinstance(url, list):
        urls = _handle_url_input(url)
        return _run_bulk_gen(
            _video_download_single,
            urls,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            quiet=quiet
        )
    if isinstance(url, str):
        expanded_urls, is_playlist = _expand_playlist(url, quiet=quiet)
        if is_playlist:
            return _run_bulk_gen(
                _video_download_single,
                expanded_urls,
                format=format,
                quality=quality,
                filename=filename,
                retries=retries,
                quiet=quiet
            )
        return _video_download_single(
            url,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            quiet=quiet
        )
    raise ValueError("url must be a string or a list of strings")


def download(
    url: Union[str, List[str]],
    *,
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    filename: Optional[str] = None,
    retries: int = 3,
    quiet: bool = True
):
    if isinstance(url, list):
        urls = _handle_url_input(url)
        return _run_bulk_gen(
            _download_single,
            urls,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            quiet=quiet
        )
    if isinstance(url, str):
        expanded_urls, is_playlist = _expand_playlist(url, quiet=quiet)
        if is_playlist:
            return _run_bulk_gen(
                _download_single,
                expanded_urls,
                format=format,
                quality=quality,
                filename=filename,
                retries=retries,
                quiet=quiet
            )
        return _download_single(
            url,
            format=format,
            quality=quality,
            filename=filename,
            retries=retries,
            quiet=quiet
        )
    raise ValueError("url must be a string or a list of strings")
