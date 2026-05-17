import unittest
from unittest.mock import patch, MagicMock

from yetunde import (
    AudioQuality,
    VideoQuality,
    AudioFormat,
    VideoFormat,
    audio_download,
    video_download,
    download
)

class TestYetunde(unittest.IsolatedAsyncioTestCase):

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    async def test_audio_download(self, mock_ydl, mock_sleep):
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            "title": "Test Audio",
            "_filename": "test.mp3",
            "abr": 128
        }
        mock_ydl.return_value.__enter__.return_value = mock_instance

        result = audio_download("http://example.com/audio", format=AudioFormat.MP3, quality=AudioQuality.MEDIUM, filename="test.mp3", retries=5)

        self.assertEqual(result, {
            "quality": "128kbps",
            "path": "test.mp3",
            "url": "http://example.com/audio"
        })
        mock_ydl.assert_called_once()
        ydl_opts = mock_ydl.call_args[0][0]

        self.assertEqual(ydl_opts['format'], 'bestaudio[abr<=128]')
        self.assertEqual(ydl_opts['retries'], 5)
        self.assertEqual(ydl_opts['outtmpl'], 'test.mp3')
        self.assertEqual(ydl_opts['postprocessors'][0]['key'], 'FFmpegExtractAudio')
        self.assertEqual(ydl_opts['postprocessors'][0]['preferredcodec'], 'mp3')

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    async def test_video_download(self, mock_ydl, mock_sleep):
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            "title": "Test Video",
            "_filename": "test.mp4",
            "height": 720
        }
        mock_ydl.return_value.__enter__.return_value = mock_instance

        result = video_download("http://example.com/video", format=VideoFormat.MKV, quality=VideoQuality.RES_720P)

        self.assertEqual(result, {
            "quality": "720p",
            "path": "test.mp4",
            "url": "http://example.com/video"
        })
        mock_ydl.assert_called_once()
        ydl_opts = mock_ydl.call_args[0][0]

        self.assertEqual(ydl_opts['format'], 'bestvideo[height<=720]')
        self.assertEqual(ydl_opts['retries'], 3) # default
        self.assertEqual(ydl_opts['merge_output_format'], 'mkv')
        self.assertEqual(ydl_opts['postprocessors'][0]['key'], 'FFmpegVideoConvertor')
        self.assertEqual(ydl_opts['postprocessors'][0]['preferedformat'], 'mkv')

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    async def test_download(self, mock_ydl, mock_sleep):
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            "title": "Test Combined",
            "_filename": "test_combined.mp4",
            "height": 1080
        }
        mock_ydl.return_value.__enter__.return_value = mock_instance

        result = download("http://example.com/combined", format=VideoFormat.MP4, quality=VideoQuality.RES_1080P)

        self.assertEqual(result, {
            "quality": "1080p",
            "path": "test_combined.mp4",
            "url": "http://example.com/combined"
        })
        mock_ydl.assert_called_once()
        ydl_opts = mock_ydl.call_args[0][0]

        self.assertEqual(ydl_opts['format'], 'bestvideo[height<=1080]+bestaudio/best')
        self.assertEqual(ydl_opts['retries'], 3)
        self.assertEqual(ydl_opts['merge_output_format'], 'mp4')
        self.assertEqual(ydl_opts['postprocessors'][0]['key'], 'FFmpegVideoConvertor')
        self.assertEqual(ydl_opts['postprocessors'][0]['preferedformat'], 'mp4')

    @patch('time.sleep')
    @patch('yt_dlp.YoutubeDL')
    async def test_audio_download_bulk(self, mock_ydl, mock_sleep):
        mock_instance = MagicMock()
        def side_effect(url, download=True):
            if "fail" in url:
                raise ValueError("Simulated failure")
            return {
                "title": f"Test {url}",
                "_filename": f"test_{url.split('/')[-1]}.mp3",
                "abr": 128
            }
        mock_instance.extract_info.side_effect = side_effect
        mock_ydl.return_value.__enter__.return_value = mock_instance

        urls = ["http://example.com/1", "http://example.com/fail", "http://example.com/2"]
        
        results = []
        async for res in audio_download(urls):
            results.append(res)

        self.assertEqual(len(results), 3)
        
        success1 = next(r for r in results if r.get("url") == "http://example.com/1")
        self.assertEqual(success1, {
            "quality": "128kbps",
            "path": "test_1.mp3",
            "url": "http://example.com/1"
        })
        
        success2 = next(r for r in results if r.get("url") == "http://example.com/2")
        self.assertEqual(success2, {
            "quality": "128kbps",
            "path": "test_2.mp3",
            "url": "http://example.com/2"
        })
        
        fail = next(r for r in results if r.get("url") == "http://example.com/fail")
        self.assertEqual(fail["status"], "error")
        self.assertIn("Simulated failure", fail["error"])

    async def test_invalid_input(self):
        with self.assertRaises(ValueError):
            audio_download(123)
        with self.assertRaises(ValueError):
            audio_download(["url1", 123])

    @patch('yt_dlp.YoutubeDL')
    async def test_playlist_support(self, mock_ydl):
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            "title": "Playlist",
            "_type": "playlist",
            "entries": [
                {"_filename": "v1.mp4", "height": 1080},
                {"_filename": "v2.mp4", "height": 1080}
            ]
        }
        mock_ydl.return_value.__enter__.return_value = mock_instance

        # Test with playlist=True (default)
        result = download("http://example.com/playlist", playlist=True)
        self.assertEqual(result, {
            "quality": "1080p",
            "path": ["v1.mp4", "v2.mp4"],
            "url": "http://example.com/playlist"
        })
        ydl_opts = mock_ydl.call_args[0][0]
        self.assertFalse(ydl_opts['noplaylist'])

        # Test with playlist=False
        download("http://example.com/playlist", playlist=False)
        ydl_opts = mock_ydl.call_args[0][0]
        self.assertTrue(ydl_opts['noplaylist'])

if __name__ == '__main__':
    unittest.main()
