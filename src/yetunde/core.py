import yt_dlp
import concurrent.futures
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

def _handle_url_input(url: Any) -> List[str]:
    if isinstance(url, str):
        return [url]
    if isinstance(url, list):
        if not all(isinstance(u, str) for u in url):
            raise ValueError("All items in the list must be strings")
        return url
    raise ValueError("url must be a string or a list of strings")

def _run_ydl(ydl_opts: Dict[str, Any], url: str, playlist: bool = True) -> Dict[str, Any]:
    ydl_opts["noplaylist"] = not playlist
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
    except Exception as e:
        if isinstance(e, YetundeError):
            raise
        raise YetundeError(
            message=f"An unexpected error occurred: {str(e)}",
            url=url,
            error_type="unknown",
            original_error=e
        ) from e

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

    return _run_ydl(ydl_opts, url, playlist=playlist)

def audio_download(
    url: Union[str, List[str]],
    format: AudioFormat = AudioFormat.MP3,
    quality: AudioQuality = AudioQuality.HIGH,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    urls = _handle_url_input(url)
    if isinstance(url, list):
        return _run_bulk(
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

    return _run_ydl(ydl_opts, url, playlist=playlist)

def video_download(
    url: Union[str, List[str]],
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    urls = _handle_url_input(url)
    if isinstance(url, list):
        return _run_bulk(
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

    return _run_ydl(ydl_opts, url, playlist=playlist)

def download(
    url: Union[str, List[str]],
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3,
    playlist: bool = True
) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    urls = _handle_url_input(url)
    if isinstance(url, list):
        return _run_bulk(
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
