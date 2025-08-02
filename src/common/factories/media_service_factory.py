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
from ..interfaces.istorage_service import IStorageService
from ..types.media_types import (
    AudioServiceConfig,
    DownloadOptions,
    MusicServiceConfig,
    YouTubeServiceConfig,
)


class MediaServiceFactory:
    """Factory para crear servicios de medios con configuración avanzada"""

    _youtube_service_instance: Optional[IYouTubeService] = None
    _audio_download_service_instance: Optional[IAudioDownloadService] = None
    _music_service_instance: Optional[IMusicService] = None

    @classmethod
    def create_youtube_service(
        cls,
        config: Optional[YouTubeServiceConfig] = None,
    ) -> IYouTubeService:
        """Crea o retorna la instancia singleton del servicio de YouTube"""
        if cls._youtube_service_instance is None:
            cls._youtube_service_instance = YouTubeAPIService(
                config=config,
            )
        return cls._youtube_service_instance

    @classmethod
    def create_audio_download_service(
        cls,
        default_options: Optional[DownloadOptions] = None,
        config: Optional[AudioServiceConfig] = None,
    ) -> IAudioDownloadService:
        """Crea o retorna la instancia singleton del servicio de descarga de audio"""
        if cls._audio_download_service_instance is None:
            cls._audio_download_service_instance = AudioDownloadService(
                config=config, default_options=default_options
            )
        return cls._audio_download_service_instance

    @classmethod
    def create_music_service(
        cls,
        youtube_service: Optional[IYouTubeService] = None,
        audio_service: Optional[IAudioDownloadService] = None,
        config: Optional[MusicServiceConfig] = None,
        music_storage: Optional[IStorageService] = None,
        image_storage: Optional[IStorageService] = None,
    ) -> IMusicService:
        """Crea o retorna la instancia singleton del servicio de música"""
        if cls._music_service_instance is None:
            youtube_svc = youtube_service or cls.create_youtube_service()
            audio_svc = audio_service or cls.create_audio_download_service()

            # Lazy import para evitar dependencia circular
            if music_storage is None or image_storage is None:
                from .storage_service_factory import StorageServiceFactory

                music_storage = (
                    music_storage or StorageServiceFactory.create_music_files_service()
                )
                image_storage = (
                    image_storage or StorageServiceFactory.create_album_covers_service()
                )

            cls._music_service_instance = MusicService(
                config=config,
                youtube_service=youtube_svc,
                audio_service=audio_svc,
                music_storage=music_storage,
                image_storage=image_storage,
            )
        return cls._music_service_instance

    @classmethod
    def create_complete_music_service(
        cls,
        music_config: Optional[MusicServiceConfig] = None,
        youtube_config: Optional[YouTubeServiceConfig] = None,
        audio_config: Optional[AudioServiceConfig] = None,
        audio_options: Optional[DownloadOptions] = None,
    ) -> IMusicService:
        """Crea un servicio de música completo con todos los componentes"""

        # Crear servicio de YouTube
        youtube_service = cls.create_youtube_service(config=youtube_config)

        # Crear servicio de descarga de audio
        audio_service = cls.create_audio_download_service(
            default_options=audio_options, config=audio_config
        )

        # Crear servicio de música principal
        return cls.create_music_service(
            config=music_config,
            youtube_service=youtube_service,
            audio_service=audio_service,
        )

    @classmethod
    def create_development_music_service(cls) -> IMusicService:
        """Crea un servicio de música para desarrollo con configuraciones optimizadas"""

        # Usar el UnifiedMusicServiceFactory para crear la versión mejorada
        from .unified_music_service_factory import get_music_service

        return get_music_service("development")

    @classmethod
    def create_enhanced_music_service(
        cls,
        config: Optional[MusicServiceConfig] = None,
        youtube_service: Optional[IYouTubeService] = None,
        audio_service: Optional[IAudioDownloadService] = None,
    ) -> IMusicService:
        """Crea un servicio de música mejorado con configuración personalizada"""
        from .unified_music_service_factory import UnifiedMusicServiceFactory

        # Si se proporcionan servicios específicos, crear servicio personalizado
        if youtube_service or audio_service or config:
            # Convertir servicios si son necesarios
            from ..adapters.media.audio_download_service import AudioDownloadService
            from ..adapters.media.youtube_service import YouTubeAPIService

            youtube_svc = youtube_service
            if youtube_svc and not isinstance(youtube_svc, YouTubeAPIService):
                # Si necesitas convertir el tipo, hazlo aquí
                pass

            audio_svc = audio_service
            if audio_svc and not isinstance(audio_svc, AudioDownloadService):
                # Si necesitas convertir el tipo, hazlo aquí
                pass

            return UnifiedMusicServiceFactory.create_custom_service(
                music_config=config,
                youtube_config=None,
                audio_config=None,
                with_repositories=False,
            )
        else:
            # Usar configuración por defecto
            return UnifiedMusicServiceFactory.create_default_service()

    @classmethod
    def create_development_enhanced_service(cls) -> IMusicService:
        """Crea un servicio mejorado para desarrollo"""
        from .unified_music_service_factory import get_music_service

        return get_music_service("development")

    @classmethod
    def create_production_enhanced_service(cls) -> IMusicService:
        """Crea un servicio mejorado para producción"""
        from .unified_music_service_factory import get_music_service

        return get_music_service("production")

    @classmethod
    def create_podcast_service(cls) -> IMusicService:
        """Crea un servicio optimizado para podcasts"""
        from .unified_music_service_factory import get_music_service

        return get_music_service("podcast")

    @classmethod
    def reset_instances(cls):
        """Resetea todas las instancias singleton (útil para testing)"""
        cls._youtube_service_instance = None
        cls._audio_download_service_instance = None
        cls._music_service_instance = None
