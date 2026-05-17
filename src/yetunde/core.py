import yt_dlp
import asyncio
import time
from typing import Optional, Dict, Any, Union, List

from .enums import AudioQuality, VideoQuality, AudioFormat, VideoFormat
from .errors import YetundeError

def get_audio_quality_format(quality: AudioQuality) -> str:
    if quality == AudioQuality.LOW:
        return "worstaudio"
    elif quality == AudioQuality.MEDIUM:
        return "bestaudio[abr<=128]"
    else:  # HIGH
        return "bestaudio"

def get_video_quality_format(quality: VideoQuality) -> str:
    height = quality.value.replace("p", "")
    return f"bestvideo[height<={height}]"

async def _run_bulk_gen(func, urls: List[str], **kwargs):
    async def _wrapped_download(url: str):
        try:
            res = await asyncio.to_thread(func, url, **kwargs)
            return {"status": "success", "data": res}
        except Exception as e:
            return {"status": "error", "url": url, "error": str(e)}

    tasks = [_wrapped_download(url) for url in urls]
    for future in asyncio.as_completed(tasks):
        result = await future
        if result["status"] == "success":
            yield result["data"]
        else:
            yield {
                "url": result["url"],
                "error": result["error"],
                "status": "error"
            }

def _handle_url_input(url: Any) -> List[str]:
    if isinstance(url, str):
        return [url]
    if isinstance(url, list):
        if not all(isinstance(u, str) for u in url):
            raise ValueError("All items in the list must be strings")
        return url
    raise ValueError("url must be a string or a list of strings")

def _simplify_info(info_dict: Dict[str, Any], original_url: str, default_quality: Any) -> Dict[str, Any]:
    if info_dict.get('_type') == 'playlist':
        entries = info_dict.get('entries', []) or []
        paths = []
        for entry in entries:
            if entry:
                path = entry.get('_filename') or entry.get('filepath') or entry.get('filename')
                if path:
                    paths.append(path)
        
        res = None
        for entry in entries:
            if entry and (entry.get('height') or entry.get('resolution')):
                res = f"{entry.get('height')}p" if entry.get('height') else entry.get('resolution')
                break
        if not res:
            res = info_dict.get('resolution')
        if not res:
            res = default_quality.value if hasattr(default_quality, 'value') else str(default_quality)
            
        return {
            "quality": res,
            "path": paths,
            "url": original_url
        }
    else:
        res = None
        if info_dict.get('height'):
            res = f"{info_dict.get('height')}p"
        elif info_dict.get('resolution'):
            res = info_dict.get('resolution')
        elif info_dict.get('abr'):
            res = f"{int(info_dict.get('abr'))}kbps"
        elif info_dict.get('format_note'):
            res = info_dict.get('format_note')
            
        if not res:
            res = default_quality.value if hasattr(default_quality, 'value') else str(default_quality)
            
        path = info_dict.get('_filename') or info_dict.get('filepath') or info_dict.get('filename')
        return {
            "quality": res,
            "path": path,
            "url": original_url
        }

def _run_ydl(ydl_opts: Dict[str, Any], url: str, playlist: bool = True) -> Dict[str, Any]:
    ydl_opts["noplaylist"] = not playlist
    retries = ydl_opts.get("retries", 3)
    last_exception = None

    for attempt in range(retries + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info_dict = ydl.extract_info(url, download=True)
                    if not info_dict:
                        raise YetundeError(
                            message=f"Could not extract info for URL: {url}",
                            url=url,
                            error_type="extraction"
                        )
                    return info_dict
                except yt_dlp.utils.DownloadError as e:
                    raise YetundeError(
                        message=f"Failed to download {url}: {str(e)}",
                        url=url,
                        error_type="download",
                        original_error=e
                    ) from e
                except Exception as e:
                    raise YetundeError(
                        message=f"Extraction failed for {url}: {str(e)}",
                        url=url,
                        error_type="extraction",
                        original_error=e
                    ) from e
        except YetundeError as e:
            last_exception = e
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise YetundeError(
                message=f"An unexpected error occurred: {str(e)}",
                url=url,
                error_type="unknown",
                original_error=e
            ) from e

    if last_exception:
        raise last_exception
    raise YetundeError(
        message=f"Failed to download {url} after {retries} retries",
        url=url,
        error_type="unknown"
    )

def _audio_download_single(
    url: str,
    format: AudioFormat = AudioFormat.MP3,
    quality: AudioQuality = AudioQuality.HIGH,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Dict[str, Any]:
    audio_format_str = get_audio_quality_format(quality)

    ydl_opts = {
        'format': audio_format_str,
        'retries': retries,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format.value,
        }],
    }

    if filename:
        ydl_opts['outtmpl'] = filename

    info_dict = _run_ydl(ydl_opts, url, playlist=playlist)
    return _simplify_info(info_dict, url, quality)

def audio_download(
    url: Union[str, List[str]],
    format: AudioFormat = AudioFormat.MP3,
    quality: AudioQuality = AudioQuality.HIGH,
    *,
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

def _video_download_single(
    url: str,
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Dict[str, Any]:
    video_format_str = get_video_quality_format(quality)

    ydl_opts = {
        'format': video_format_str,
        'retries': retries,
        'merge_output_format': format.value,
    }

    ydl_opts['postprocessors'] = [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': format.value,
    }]

    if filename:
        ydl_opts['outtmpl'] = filename

    info_dict = _run_ydl(ydl_opts, url, playlist=playlist)
    return _simplify_info(info_dict, url, quality)

def video_download(
    url: Union[str, List[str]],
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
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

def _download_single(
    url: str,
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Dict[str, Any]:
    # Download merged video + audio
    video_format_str = get_video_quality_format(quality)
    combined_format = f"{video_format_str}+bestaudio/best"

    ydl_opts = {
        'format': combined_format,
        'retries': retries,
        'merge_output_format': format.value,
    }

    ydl_opts['postprocessors'] = [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': format.value,
    }]

    if filename:
        ydl_opts['outtmpl'] = filename

    info_dict = _run_ydl(ydl_opts, url, playlist=playlist)
    return _simplify_info(info_dict, url, quality)

def download(
    url: Union[str, List[str]],
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
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
