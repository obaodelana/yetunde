import yt_dlp
from typing import Optional, Dict, Any

from .enums import AudioQuality, VideoQuality, AudioFormat, VideoFormat
from .errors import DownloadError, ExtractionError

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

def _run_ydl(ydl_opts: Dict[str, Any], url: str) -> Dict[str, Any]:
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=True)
                if not info_dict:
                    raise ExtractionError(f"Could not extract info for URL: {url}")
                return info_dict
            except yt_dlp.utils.DownloadError as e:
                raise DownloadError(f"Failed to download {url}: {str(e)}") from e
            except Exception as e:
                raise ExtractionError(f"Extraction failed for {url}: {str(e)}") from e
    except Exception as e:
        if isinstance(e, (DownloadError, ExtractionError)):
            raise
        raise DownloadError(f"An unexpected error occurred: {str(e)}") from e

def audio_download(
    url: str,
    format: AudioFormat = AudioFormat.MP3,
    quality: AudioQuality = AudioQuality.HIGH,
    *,
    filename: Optional[str] = None,
    retries: int = 3
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

    return _run_ydl(ydl_opts, url)

def video_download(
    url: str,
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3
) -> Dict[str, Any]:
    video_format_str = get_video_quality_format(quality)

    ydl_opts = {
        'format': video_format_str,
        'retries': retries,
        'merge_output_format': format.value,
    }

    # yt-dlp uses 'merge_output_format' mainly when combining. If it's a single video file,
    # FFmpegVideoConvertor may be needed.
    ydl_opts['postprocessors'] = [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': format.value,
    }]

    if filename:
        ydl_opts['outtmpl'] = filename

    return _run_ydl(ydl_opts, url)

def download(
    url: str,
    format: VideoFormat = VideoFormat.MP4,
    quality: VideoQuality = VideoQuality.RES_1080P,
    *,
    filename: Optional[str] = None,
    retries: int = 3
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

    return _run_ydl(ydl_opts, url)
