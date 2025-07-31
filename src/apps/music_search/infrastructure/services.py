import asyncio
import re
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import yt_dlp
from django.conf import settings
from googleapiclient.discovery import build

from common.mixins.logging_mixin import LoggingMixin

from ..domain.interfaces import IAudioDownloadService, IYouTubeService, YouTubeVideoInfo


class YouTubeAPIService(IYouTubeService, LoggingMixin):
    """Servicio para interactuar con la API de YouTube"""

    def __init__(self):
        super().__init__()
        self.youtube = build(
            settings.YOUTUBE_API_SERVICE_NAME,
            settings.YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY,
        )

    async def search_videos(
        self, query: str, max_results: int = 6
    ) -> List[YouTubeVideoInfo]:
        """Busca videos en YouTube"""
        try:
            search_response = (
                self.youtube.search()
                .list(
                    q=query,
                    part="snippet",
                    type="video",
                    maxResults=max_results,
                    videoCategoryId="10",  # Categoría de música
                )
                .execute()
            )

            video_ids = [
                item["id"]["videoId"] for item in search_response.get("items", [])
            ]

            if not video_ids:
                return []

            # Obtener detalles adicionales de los videos
            videos_response = (
                self.youtube.videos()
                .list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
                .execute()
            )

            return [
                self._build_video_info(video)
                for video in videos_response.get("items", [])
            ]

        except Exception as e:
            self.logger.error(f"Error searching videos: {str(e)}")
            return []

    async def get_video_details(self, video_id: str) -> Optional[YouTubeVideoInfo]:
        """Obtiene detalles de un video específico"""
        try:
            video_response = (
                self.youtube.videos()
                .list(part="snippet,statistics,contentDetails", id=video_id)
                .execute()
            )

            videos = video_response.get("items", [])
            if not videos:
                return None

            return self._build_video_info(videos[0])

        except Exception as e:
            self.logger.error(f"Error getting video details for {video_id}: {str(e)}")
            return None

    async def get_random_music_videos(
        self, max_results: int = 6
    ) -> List[YouTubeVideoInfo]:
        """Obtiene videos de música aleatorios"""
        import random

        random_queries = settings.RANDOM_MUSIC_QUERIES
        query = random.choice(random_queries)  # nosec B311

        return await self.search_videos(query, max_results)

    def _build_video_info(self, video_data: Dict[str, Any]) -> YouTubeVideoInfo:
        """Construye un objeto YouTubeVideoInfo a partir de datos de la API"""
        snippet = video_data["snippet"]
        statistics = video_data.get("statistics", {})
        content_details = video_data["contentDetails"]

        # Parsear duración ISO 8601
        duration_seconds = self._parse_duration(content_details["duration"])

        # Parsear fecha de publicación
        published_at = datetime.fromisoformat(
            snippet["publishedAt"].replace("Z", "+00:00")
        )

        # Obtener género basado en categoría
        category_id = snippet.get("categoryId", "10")
        genre = settings.YOUTUBE_CATEGORIES.get(int(category_id), "Music")

        return YouTubeVideoInfo(
            video_id=video_data["id"],
            title=snippet["title"],
            channel_title=snippet["channelTitle"],
            channel_id=snippet["channelId"],
            thumbnail_url=snippet["thumbnails"]["high"]["url"],
            description=snippet["description"],
            duration_seconds=duration_seconds,
            published_at=published_at,
            view_count=int(statistics.get("viewCount", 0)),
            like_count=int(statistics.get("likeCount", 0)),
            tags=snippet.get("tags", []),
            category_id=category_id,
            genre=genre,
            url=f"https://www.youtube.com/watch?v={video_data['id']}",
        )

    def _parse_duration(self, duration_str: str) -> int:
        """Convierte duración ISO 8601 a segundos"""
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
        if not match:
            return 0

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

        return hours * 3600 + minutes * 60 + seconds


class AudioDownloadService(IAudioDownloadService, LoggingMixin):
    """Servicio para descargar audio de YouTube"""

    def __init__(self):
        super().__init__()
        self.ydl_opts = {
            "format": "bestaudio/best",
            "extractaudio": True,
            "audioformat": "mp3",
            "audioquality": "192",
            "quiet": True,
            "no_warnings": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "referer": "https://www.youtube.com/",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    async def download_audio(self, video_url: str) -> Optional[bytes]:
        """Descarga el audio de un video como bytes"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, self._download_audio_sync, video_url
            )
        except Exception as e:
            self.logger.error(f"Error downloading audio from {video_url}: {str(e)}")
            return None

    def _download_audio_sync(self, video_url: str) -> Optional[bytes]:
        """Descarga sincrónica del audio"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = f"{temp_dir}/{uuid.uuid4()}.%(ext)s"

            opts = self.ydl_opts.copy()
            opts["outtmpl"] = output_path

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([video_url])

                # Buscar el archivo descargado
                import os

                for file in os.listdir(temp_dir):
                    if file.endswith((".mp3", ".m4a", ".webm")):
                        file_path = os.path.join(temp_dir, file)
                        with open(file_path, "rb") as f:
                            return f.read()

                return None

            except Exception as e:
                self.logger.error(f"yt-dlp error: {str(e)}")
                return None

    async def get_audio_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Obtiene información del audio sin descargarlo"""
        try:
            opts = self.ydl_opts.copy()
            opts["extract_flat"] = True

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, self._get_audio_info_sync, video_url, opts
            )
        except Exception as e:
            self.logger.error(f"Error getting audio info from {video_url}: {str(e)}")
            return None

    def _get_audio_info_sync(
        self, video_url: str, opts: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Obtiene información sincrónica del audio"""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return {
                    "title": info.get("title", ""),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", ""),
                    "formats": info.get("formats", []),
                }
        except Exception as e:
            self.logger.error(f"yt-dlp info error: {str(e)}")
            return None
