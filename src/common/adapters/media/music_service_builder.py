from __future__ import annotations

from typing import Any, Dict, List

from ...interfaces.imedia_service import IMusicService
from ...types.media_types import (
    AudioServiceConfig,
    DownloadOptions,
    MusicServiceConfig,
    YouTubeServiceConfig,
)
from ...utils.retry_manager import RetryManager
from .audio_download_service import AudioDownloadService
from .enhanced_music_service import EnhancedMusicService
from .music_service import AudioProcessor, MetadataExtractor, ThumbnailProcessor
from .video_processing_pipeline import VideoProcessingPipeline
from .video_processors import (
    BaseVideoProcessor,
    MusicVideoProcessor,
    PodcastVideoProcessor,
    VideoProcessorStrategy,
)
from .youtube_service import YouTubeAPIService


class MusicServiceBuilder:
    """Builder para construir servicios de música configurados"""

    def __init__(self):
        self.reset()

    def reset(self) -> MusicServiceBuilder:
        """Resetea el builder a su estado inicial"""
        self._music_config = MusicServiceConfig()
        self._youtube_config = YouTubeServiceConfig()
        self._audio_config = AudioServiceConfig()
        self._download_options = DownloadOptions()
        self._quality_filters: Dict[str, Any] = {}
        self._custom_processors: List[BaseVideoProcessor] = []
        self._enable_detailed_logging = False
        return self

    def with_music_config(self, config: MusicServiceConfig) -> MusicServiceBuilder:
        """Configura el servicio de música"""
        self._music_config = config
        return self

    def with_youtube_config(self, config: YouTubeServiceConfig) -> MusicServiceBuilder:
        """Configura el servicio de YouTube"""
        self._youtube_config = config
        return self

    def with_audio_config(self, config: AudioServiceConfig) -> MusicServiceBuilder:
        """Configura el servicio de audio"""
        self._audio_config = config
        return self

    def with_download_options(self, options: DownloadOptions) -> MusicServiceBuilder:
        """Configura opciones de descarga"""
        self._download_options = options
        return self

    def with_quality_filters(self, filters: Dict[str, Any]) -> MusicServiceBuilder:
        """Configura filtros de calidad para videos"""
        self._quality_filters = filters
        return self

    def with_detailed_logging(self, enable: bool = True) -> MusicServiceBuilder:
        """Habilita logging detallado"""
        self._enable_detailed_logging = enable
        return self

    def add_custom_processor(
        self, processor: BaseVideoProcessor
    ) -> MusicServiceBuilder:
        """Añade un procesador personalizado"""
        self._custom_processors.append(processor)
        return self

    def for_development(self) -> MusicServiceBuilder:
        """Configuración optimizada para desarrollo"""
        self._music_config = MusicServiceConfig(
            max_concurrent_operations=2,
            enable_audio_download=True,
            enable_thumbnail_processing=False,  # Deshabilitar thumbnails en dev
            max_retries=1,
            retry_delay=0.1,
        )

        self._youtube_config = YouTubeServiceConfig(
            max_retries=1, retry_delay=0.1, enable_quota_tracking=True
        )

        self._audio_config = AudioServiceConfig(
            max_retries=1,
            retry_delay=0.1,
            cleanup_temp_files=True,
            default_quality="128",
        )

        self._download_options = DownloadOptions(
            audio_quality="128", timeout=60, max_retries=1
        )

        self._quality_filters = {
            "min_duration": 10,  # Más permisivo en desarrollo
            "max_duration": 300,
        }

        self._enable_detailed_logging = True
        return self

    def for_production(self) -> MusicServiceBuilder:
        """Configuración optimizada para producción"""
        self._music_config = MusicServiceConfig(
            max_concurrent_operations=5,
            enable_audio_download=True,
            enable_thumbnail_processing=True,
            max_retries=3,
            retry_delay=1.0,
        )

        self._youtube_config = YouTubeServiceConfig(
            max_retries=3,
            retry_delay=1.0,
            enable_quota_tracking=True,
            quota_limit_per_day=9000,
        )

        self._audio_config = AudioServiceConfig(
            max_retries=3,
            retry_delay=1.0,
            cleanup_temp_files=True,
            default_quality="192",
        )

        self._download_options = DownloadOptions(
            audio_quality="192",
            timeout=300,
            max_retries=3,
            max_filesize=50 * 1024 * 1024,
        )

        self._quality_filters = {"min_duration": 30, "max_duration": 600}

        self._enable_detailed_logging = False
        return self

    def for_podcasts(self) -> MusicServiceBuilder:
        """Configuración optimizada para podcasts"""
        self._music_config = MusicServiceConfig(
            max_concurrent_operations=3,
            enable_audio_download=True,
            enable_thumbnail_processing=False,  # No necesario para podcasts
            max_retries=3,
            retry_delay=1.0,
        )

        self._quality_filters = {
            "min_duration": 300,  # Al menos 5 minutos
            "max_duration": 7200,  # Máximo 2 horas
        }
        return self

    def build(self) -> IMusicService:
        """Construye el servicio de música configurado"""
        # Crear servicios base
        youtube_service = YouTubeAPIService(config=self._youtube_config)
        audio_service = AudioDownloadService(
            config=self._audio_config, default_options=self._download_options
        )

        # Crear retry manager
        retry_manager = RetryManager(
            max_retries=self._music_config.max_retries,
            base_delay=self._music_config.retry_delay,
        )

        # Crear procesadores auxiliares
        from ...factories import StorageServiceFactory

        music_storage = StorageServiceFactory.create_music_files_service()
        image_storage = StorageServiceFactory.create_album_covers_service()

        thumbnail_processor = ThumbnailProcessor(image_storage, retry_manager)
        audio_processor = AudioProcessor(
            audio_service if self._music_config.enable_audio_download else None,
            music_storage,
            retry_manager,
        )
        metadata_extractor = MetadataExtractor()

        # Crear procesadores de video
        processors: List[BaseVideoProcessor] = []

        # Añadir procesadores personalizados primero (mayor prioridad)
        processors.extend(self._custom_processors)

        # Añadir procesador de música
        music_processor = MusicVideoProcessor(
            (
                thumbnail_processor
                if self._music_config.enable_thumbnail_processing
                else None
            ),
            audio_processor,
            metadata_extractor,
            self._quality_filters,
        )
        processors.append(music_processor)

        # Añadir procesador de podcasts si hay filtros específicos
        if self._quality_filters.get("min_duration", 0) >= 300:
            podcast_processor = PodcastVideoProcessor(
                audio_processor, metadata_extractor
            )
            processors.append(podcast_processor)

        # Crear estrategia de procesamiento
        processor_strategy = VideoProcessorStrategy(processors)

        # Crear pipeline de procesamiento
        pipeline = VideoProcessingPipeline(
            processor=processor_strategy,
            retry_manager=retry_manager,
            max_concurrent=self._music_config.max_concurrent_operations,
            enable_detailed_logging=self._enable_detailed_logging,
        )

        # Crear el servicio principal

        return EnhancedMusicService(
            config=self._music_config,
            youtube_service=youtube_service,
            processing_pipeline=pipeline,
            retry_manager=retry_manager,
        )
