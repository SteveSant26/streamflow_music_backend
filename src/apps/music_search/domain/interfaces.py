from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class YouTubeVideoInfo:
    """Información detallada de un video de YouTube"""

    video_id: str
    title: str
    channel_title: str
    channel_id: str
    thumbnail_url: str
    description: str
    duration_seconds: int
    published_at: datetime
    view_count: int
    like_count: int
    tags: List[str]
    category_id: str
    genre: str
    url: str


@dataclass
class MusicTrackData:
    """Datos procesados de una pista musical"""

    video_id: str
    title: str
    artist_name: str
    album_title: Optional[str]
    duration_seconds: int
    thumbnail_url: str
    genre: str
    tags: List[str]
    url: str
    audio_file_data: Optional[bytes] = None
    audio_file_name: Optional[str] = None


class IYouTubeService(ABC):
    """Interface para servicios de YouTube"""

    @abstractmethod
    async def search_videos(
        self, query: str, max_results: int = 6
    ) -> List[YouTubeVideoInfo]:
        """Busca videos en YouTube"""

    @abstractmethod
    async def get_video_details(self, video_id: str) -> Optional[YouTubeVideoInfo]:
        """Obtiene detalles de un video específico"""

    @abstractmethod
    async def get_random_music_videos(
        self, max_results: int = 6
    ) -> List[YouTubeVideoInfo]:
        """Obtiene videos de música aleatorios"""


class IAudioDownloadService(ABC):
    """Interface para servicios de descarga de audio"""

    @abstractmethod
    async def download_audio(self, video_url: str) -> Optional[bytes]:
        """Descarga el audio de un video como bytes"""

    @abstractmethod
    async def get_audio_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Obtiene información del audio sin descargarlo"""


class IMusicService(ABC):
    """Interface principal para el servicio de música"""

    @abstractmethod
    async def search_and_process_music(
        self, query: str, max_results: int = 6
    ) -> List[MusicTrackData]:
        """Busca y procesa música desde YouTube"""

    @abstractmethod
    async def get_random_music_tracks(
        self, max_results: int = 6
    ) -> List[MusicTrackData]:
        """Obtiene pistas de música aleatorias procesadas"""

    @abstractmethod
    async def process_video_to_track(
        self, video_info: YouTubeVideoInfo
    ) -> Optional[MusicTrackData]:
        """Convierte información de video de YouTube a datos de pista musical"""
