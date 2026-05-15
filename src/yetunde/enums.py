from enum import Enum

class AudioQuality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class VideoQuality(str, Enum):
    RES_144P = "144p"
    RES_360P = "360p"
    RES_720P = "720p"
    RES_1080P = "1080p"
    RES_1440P = "1440p"
    RES_2160P = "2160p"

class AudioFormat(str, Enum):
    MP3 = "mp3"
    M4A = "m4a"
    WAV = "wav"
    FLAC = "flac"

class VideoFormat(str, Enum):
    MP4 = "mp4"
    MKV = "mkv"
    WEBM = "webm"
