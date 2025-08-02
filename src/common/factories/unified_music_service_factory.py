from typing import Optional

from django.conf import settings

from ..adapters.media.audio_download_service import AudioDownloadService
from ..adapters.media.unified_music_service import UnifiedMusicService
from ..adapters.media.youtube_service import YouTubeAPIService
from ..types.media_types import (
    AudioServiceConfig,
    MusicServiceConfig,
    YouTubeServiceConfig,
)


class UnifiedMusicServiceFactory:
    """Factory para crear el servicio unificado de música con configuración automática"""

    @staticmethod
    def create_default_service() -> UnifiedMusicService:
        """
        Crea un servicio unificado con configuración por defecto

        Returns:
            UnifiedMusicService configurado y listo para usar
        """
        # Configuraciones por defecto
        music_config = MusicServiceConfig(
            enable_audio_download=True,
            enable_thumbnail_processing=True,
            max_concurrent_operations=3,
        )

        youtube_config = YouTubeServiceConfig(
            enable_quota_tracking=True,
            quota_limit_per_day=getattr(settings, "YOUTUBE_QUOTA_LIMIT", 10000),
            max_retries=3,
        )

        audio_config = AudioServiceConfig(
            default_quality="192", cleanup_temp_files=True, max_retries=3
        )

        # Crear servicios auxiliares
        youtube_service = YouTubeAPIService(config=youtube_config)
        audio_service = AudioDownloadService(config=audio_config)

        # Crear y retornar servicio unificado
        return UnifiedMusicService(
            config=music_config,
            youtube_service=youtube_service,
            audio_service=audio_service,
        )

    @staticmethod
    def create_lightweight_service() -> UnifiedMusicService:
        """
        Crea un servicio ligero sin descarga de audio (solo metadatos y búsqueda)

        Returns:
            UnifiedMusicService configurado para operaciones ligeras
        """
        # Configuración ligera
        music_config = MusicServiceConfig(
            enable_audio_download=False,
            enable_thumbnail_processing=False,
            max_concurrent_operations=5,
        )

        youtube_config = YouTubeServiceConfig(
            enable_quota_tracking=True,
            quota_limit_per_day=getattr(settings, "YOUTUBE_QUOTA_LIMIT", 5000),
            max_retries=2,
        )

        # Solo YouTube service (sin audio download)
        youtube_service = YouTubeAPIService(config=youtube_config)

        return UnifiedMusicService(
            config=music_config,
            youtube_service=youtube_service,
            audio_service=None,  # Sin descarga de audio
        )

    @staticmethod
    def create_development_service() -> UnifiedMusicService:
        """
        Crea un servicio optimizado para desarrollo

        Returns:
            UnifiedMusicService optimizado para desarrollo
        """
        # Configuración de desarrollo
        music_config = MusicServiceConfig(
            enable_audio_download=True,
            enable_thumbnail_processing=False,  # Deshabilitar thumbnails en dev
            max_concurrent_operations=2,
            max_retries=1,
            retry_delay=0.1,
        )

        youtube_config = YouTubeServiceConfig(
            enable_quota_tracking=True,
            quota_limit_per_day=getattr(settings, "YOUTUBE_QUOTA_LIMIT", 5000),
            max_retries=1,
            retry_delay=0.1,
        )

        audio_config = AudioServiceConfig(
            default_quality="128",
            cleanup_temp_files=True,
            max_retries=1,
            retry_delay=0.1,
            request_timeout=60,
        )

        # Crear servicios con configuración optimizada para desarrollo
        youtube_service = YouTubeAPIService(config=youtube_config)
        audio_service = AudioDownloadService(config=audio_config)

        return UnifiedMusicService(
            config=music_config,
            youtube_service=youtube_service,
            audio_service=audio_service,
        )

    @staticmethod
    def create_podcast_service() -> UnifiedMusicService:
        """
        Crea un servicio optimizado para podcasts

        Returns:
            UnifiedMusicService optimizado para podcasts
        """
        # Configuración para podcasts
        music_config = MusicServiceConfig(
            enable_audio_download=True,
            enable_thumbnail_processing=False,  # No necesario para podcasts
            max_concurrent_operations=3,
            max_retries=3,
            retry_delay=1.0,
        )

        youtube_config = YouTubeServiceConfig(
            enable_quota_tracking=True,
            max_retries=3,
            retry_delay=1.0,
        )

        audio_config = AudioServiceConfig(
            default_quality="192",
            cleanup_temp_files=True,
            max_retries=3,
            request_timeout=120,  # Timeout más largo para podcasts
        )

        # Crear servicios
        youtube_service = YouTubeAPIService(config=youtube_config)
        audio_service = AudioDownloadService(config=audio_config)

        return UnifiedMusicService(
            config=music_config,
            youtube_service=youtube_service,
            audio_service=audio_service,
        )

    @staticmethod
    def create_production_service() -> UnifiedMusicService:
        """
        Crea un servicio optimizado para producción

        Returns:
            UnifiedMusicService optimizado para producción
        """
        # Configuración de producción
        music_config = MusicServiceConfig(
            enable_audio_download=True,
            enable_thumbnail_processing=True,
            max_concurrent_operations=2,  # Conservador para producción
            enable_caching=True,
            cache_ttl=3600,
        )

        youtube_config = YouTubeServiceConfig(
            enable_quota_tracking=True,
            quota_limit_per_day=getattr(settings, "YOUTUBE_QUOTA_LIMIT", 8000),
            max_retries=5,  # Más reintentos en producción
            retry_delay=2.0,
        )

        audio_config = AudioServiceConfig(
            default_quality="320",  # Mayor calidad en producción
            cleanup_temp_files=True,
            max_retries=5,
            request_timeout=60,  # Timeout más largo
        )

        # Crear servicios con configuración robusta
        youtube_service = YouTubeAPIService(config=youtube_config)
        audio_service = AudioDownloadService(config=audio_config)

        return UnifiedMusicService(
            config=music_config,
            youtube_service=youtube_service,
            audio_service=audio_service,
        )

    @staticmethod
    def create_custom_service(
        music_config: Optional[MusicServiceConfig] = None,
        youtube_config: Optional[YouTubeServiceConfig] = None,
        audio_config: Optional[AudioServiceConfig] = None,
        with_repositories: bool = False,
    ) -> UnifiedMusicService:
        """
        Crea un servicio con configuración personalizada

        Args:
            music_config: Configuración del servicio de música
            youtube_config: Configuración del servicio de YouTube
            audio_config: Configuración del servicio de audio
            with_repositories: Si configurar repositorios automáticamente

        Returns:
            UnifiedMusicService personalizado
        """
        # Usar configuraciones por defecto si no se proporcionan
        music_config = music_config or MusicServiceConfig()
        youtube_config = youtube_config or YouTubeServiceConfig()
        audio_config = audio_config or AudioServiceConfig()

        # Crear servicios auxiliares
        youtube_service = YouTubeAPIService(config=youtube_config)
        audio_service = (
            AudioDownloadService(config=audio_config)
            if music_config.enable_audio_download
            else None
        )

        # Crear servicio unificado
        service = UnifiedMusicService(
            config=music_config,
            youtube_service=youtube_service,
            audio_service=audio_service,
        )

        # Configurar repositorios si se solicita
        if with_repositories:
            service = UnifiedMusicServiceFactory._configure_repositories(service)

        return service

    @staticmethod
    def _configure_repositories(service: UnifiedMusicService) -> UnifiedMusicService:
        """
        Configura repositorios automáticamente basado en la configuración de Django

        Args:
            service: Servicio a configurar

        Returns:
            Servicio con repositorios configurados
        """
        try:
            # Importar repositorios dinámicamente para evitar dependencias circulares
            from apps.albums.infrastructure.repository import AlbumRepository
            from apps.artists.infrastructure.repository import ArtistRepository

            artist_repo = ArtistRepository()
            album_repo = AlbumRepository()

            service.configure_repositories(
                artist_repository=artist_repo, album_repository=album_repo
            )

        except ImportError as e:
            service.logger.warning(f"Could not configure repositories: {str(e)}")

        return service


# Función de conveniencia para uso directo
def get_music_service(service_type: str = "default") -> UnifiedMusicService:
    """
    Función de conveniencia para obtener un servicio de música configurado

    Args:
        service_type: Tipo de servicio ("default", "lightweight", "production", "development", "podcast", "custom")

    Returns:
        UnifiedMusicService configurado
    """
    factory = UnifiedMusicServiceFactory()

    if service_type == "lightweight":
        return factory.create_lightweight_service()
    elif service_type == "production":
        return factory.create_production_service()
    elif service_type == "development":
        return factory.create_development_service()
    elif service_type == "podcast":
        return factory.create_podcast_service()
    elif service_type == "custom":
        return factory.create_custom_service(with_repositories=True)
    else:  # default
        return factory.create_default_service()
