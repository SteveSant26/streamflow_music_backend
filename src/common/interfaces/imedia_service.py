"""
Interfaces para servicios de medios (video, audio, etc.)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence

from ..types.media_types import (
    AudioTrackData,
    DownloadOptions,
    SearchOptions,
    VideoInfo,
    YouTubeVideoInfo,
)


class IVideoService(ABC):
    """Interface base para servicios de video"""

    @abstractmethod
    async def search_videos(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> Sequence[VideoInfo]:
        """Busca videos"""

    @abstractmethod
    async def get_video_details(self, video_id: str) -> Optional[VideoInfo]:
        """Obtiene detalles de un video específico"""


class IYouTubeService(IVideoService):
    """Interface para servicios de YouTube"""

    @abstractmethod
    async def search_videos(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[YouTubeVideoInfo]:
        """Busca videos en YouTube"""

    @abstractmethod
    async def get_video_details(self, video_id: str) -> Optional[YouTubeVideoInfo]:
        """Obtiene detalles de un video específico de YouTube"""

    @abstractmethod
    async def get_random_videos(
        self, options: Optional[SearchOptions] = None
    ) -> List[YouTubeVideoInfo]:
        """Obtiene videos aleatorios"""


class IAudioDownloadService(ABC):
    """Interface para servicios de descarga de audio"""

    @abstractmethod
    async def download_audio(
        self, video_url: str, options: Optional[DownloadOptions] = None
    ) -> Optional[bytes]:
        """Descarga el audio de un video como bytes"""

    @abstractmethod
    async def get_audio_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Obtiene información del audio sin descargarlo"""

    @abstractmethod
    async def validate_url(self, video_url: str) -> bool:
        """Valida si la URL es válida para descarga"""


class IAudioProcessingService(ABC):
    """Interface para servicios de procesamiento de audio"""

    @abstractmethod
    async def process_video_to_audio_track(
        self, video_info: VideoInfo
    ) -> Optional[AudioTrackData]:
        """Convierte información de video a datos de pista de audio"""

    @abstractmethod
    async def search_and_process_audio(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        """Busca y procesa audio desde videos"""

    @abstractmethod
    async def get_random_audio_tracks(
        self, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        """Obtiene pistas de audio aleatorias procesadas"""


class IMusicService(IAudioProcessingService):
    """Interface específica para servicios de música"""

    # Métodos para compatibilidad con implementación existente
    @abstractmethod
    async def search_and_process_music(
        self, query: str, max_results: int = 6
    ) -> List[AudioTrackData]:
        """Busca y procesa música - método para compatibilidad"""

    @abstractmethod
    async def get_random_music_tracks(
        self, max_results: int = 6
    ) -> List[AudioTrackData]:
        """Obtiene pistas de música aleatorias - método para compatibilidad"""
