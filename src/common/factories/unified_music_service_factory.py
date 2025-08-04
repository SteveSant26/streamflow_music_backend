from django.conf import settings

from apps.albums.infrastructure.repository import AlbumRepository
from apps.artists.infrastructure.repository import ArtistRepository

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

        service = UnifiedMusicService(
            config=music_config,
            youtube_service=youtube_service,
            audio_service=audio_service,
        )

        # Configurar repositorios automáticamente
        return UnifiedMusicServiceFactory._configure_repositories(service)

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

            artist_repo = ArtistRepository()
            album_repo = AlbumRepository()

            service.configure_repositories(
                artist_repository=artist_repo, album_repository=album_repo
            )

        except ImportError as e:
            service.logger.warning(f"Could not configure repositories: {str(e)}")

        return service


# Función de conveniencia para uso directo
def get_music_service() -> UnifiedMusicService:
    """
    Función de conveniencia para obtener un servicio de música configurado

    Args:

    Returns:
        UnifiedMusicService configurado
    """
    factory = UnifiedMusicServiceFactory()

    return factory.create_default_service()
