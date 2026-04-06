import os
import uuid
import logging
import yt_dlp
from typing import Optional

logger = logging.getLogger(__name__)

class VideoFetcher:
    """Service to safely download audio from social media URLs"""
    
    def __init__(self, output_dir: str = "/tmp/video_downloads"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def download_audio(self, url: str) -> str:
        """
        Downloads the audio of a video from a URL.
        Restricts max length to ~5 minutes.
        Returns the local path to the audio file.
        """
        try:
            file_id = str(uuid.uuid4())
            
            def duration_filter(info, *, incomplete):
                duration = info.get('duration')
                if duration and duration > 300:
                    return 'Video is too long (over 5 minutes)'
                return None

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, f'{file_id}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'match_filter': duration_filter
            }

            logger.info(f"Downloading audio from {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise Exception("Failed to extract info from URL")
                
                expected_filepath = os.path.join(self.output_dir, f"{file_id}.wav")
                if os.path.exists(expected_filepath):
                    logger.info(f"Successfully downloaded audio to {expected_filepath}")
                    return expected_filepath
                
                raise FileNotFoundError(f"Downloaded audio not found at {expected_filepath}")
                
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if 'Video is too long' in msg:
                raise ValueError("Video exceeds maximum supported length (5 minutes).")
            raise Exception(f"Video download failed: {msg[:100]}")
        except Exception as e:
            logger.error(f"Video fetcher error: {e}", exc_info=True)
            raise ValueError(f"Failed to fetch video: {str(e)[:100]}")

video_fetcher = VideoFetcher()
