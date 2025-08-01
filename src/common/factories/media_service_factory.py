"""
Factory para servicios de medios
"""
from typing import Optional

from ..adapters.media import AudioDownloadService, MusicService, YouTubeAPIService
from ..interfaces.imedia_service import (
    IAudioDownloadService,
    IMusicService,
    IYouTubeService,
)
from ..types.media_types import DownloadOptions


class MediaServiceFactory:
    """Factory para crear servicios de medios con configuración por defecto"""

    _youtube_service_instance: Optional[IYouTubeService] = None
    _audio_download_service_instance: Optional[IAudioDownloadService] = None
    _music_service_instance: Optional[IMusicService] = None

    @classmethod
    def create_youtube_service(cls, api_key: Optional[str] = None) -> IYouTubeService:
        """Crea o retorna la instancia singleton del servicio de YouTube"""
        if cls._youtube_service_instance is None:
            cls._youtube_service_instance = YouTubeAPIService(api_key)
        return cls._youtube_service_instance

    @classmethod
    def create_audio_download_service(
        cls, default_options: Optional[DownloadOptions] = None
    ) -> IAudioDownloadService:
        """Crea o retorna la instancia singleton del servicio de descarga de audio"""
        if cls._audio_download_service_instance is None:
            cls._audio_download_service_instance = AudioDownloadService(default_options)
        return cls._audio_download_service_instance

    @classmethod
    def create_music_service(
        cls,
        youtube_service: Optional[IYouTubeService] = None,
        audio_service: Optional[IAudioDownloadService] = None,
        max_concurrent_downloads: int = 3,
    ) -> IMusicService:
        """Crea o retorna la instancia singleton del servicio de música"""
        if cls._music_service_instance is None:
            youtube_svc = youtube_service or cls.create_youtube_service()
            audio_svc = audio_service or cls.create_audio_download_service()

            cls._music_service_instance = MusicService(
                youtube_service=youtube_svc,
                audio_service=audio_svc,
                max_concurrent_downloads=max_concurrent_downloads,
            )
        return cls._music_service_instance

    @classmethod
    def reset_instances(cls):
        """Resetea todas las instancias singleton (útil para testing)"""
        cls._youtube_service_instance = None
        cls._audio_download_service_instance = None
        cls._music_service_instance = None
