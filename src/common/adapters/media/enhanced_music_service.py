"""
⚠️  SERVICIO DEPRECADO ⚠️

EnhancedMusicService ha sido deprecado en favor de UnifiedMusicService.
Por favor, migra tu código usando:

from src.common.factories.unified_music_service_factory import get_music_service
music_service = get_music_service("default")

Consulta docs/MIGRATION_GUIDE.md para más detalles.
"""

import warnings
from typing import Any, Dict, List, Optional

from ...interfaces.imedia_service import IMusicService, IYouTubeService
from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import (
    AudioTrackData,
    MusicServiceConfig,
    MusicTrackData,
    SearchOptions,
    VideoInfo,
    YouTubeVideoInfo,
)
from ...utils.retry_manager import RetryManager
from .video_processing_pipeline import VideoProcessingPipeline

# Emitir warning de deprecación al importar
warnings.warn(
    "EnhancedMusicService está deprecado. Usa UnifiedMusicService en su lugar. "
    "Consulta docs/MIGRATION_GUIDE.md para migrar.",
    DeprecationWarning,
    stacklevel=2,
)


class EnhancedMusicService(IMusicService, LoggingMixin):
    """Servicio de música mejorado con pipeline de procesamiento configurable"""

    def __init__(
        self,
        config: MusicServiceConfig,
        youtube_service: IYouTubeService,
        processing_pipeline: VideoProcessingPipeline,
        retry_manager: RetryManager,
    ):
        super().__init__()
        self.config = config
        self.youtube_service = youtube_service
        self.processing_pipeline = processing_pipeline
        self.retry_manager = retry_manager

        # Métricas de rendimiento
        self._stats: Dict[str, Any] = {
            "videos_processed": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "cache_hits": 0,
        }

    async def search_and_process_audio(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        """Busca y procesa audio desde videos usando el pipeline configurado"""
        if not query or not query.strip():
            self.logger.warning("Empty search query provided")
            return []

        try:
            if not self.youtube_service:
                self.logger.error("YouTube service not configured")
                return []

            self.logger.info(f"Searching for: '{query}' with options: {options}")

            # Buscar videos
            videos = await self.retry_manager.execute_with_retry(
                self.youtube_service.search_videos, query, options
            )

            if not videos:
                self.logger.warning(f"No videos found for query: '{query}'")
                return []

            # Procesar usando el pipeline
            return await self._process_videos_with_stats(videos)

        except Exception as e:
            self.logger.error(f"Error in search_and_process_audio: {str(e)}")
            return []

    async def get_random_audio_tracks(
        self, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        """Obtiene pistas de audio aleatorias usando el pipeline configurado"""
        try:
            if not self.youtube_service:
                self.logger.error("YouTube service not configured")
                return []

            self.logger.info(f"Getting random tracks with options: {options}")

            # Obtener videos aleatorios
            videos = await self.retry_manager.execute_with_retry(
                self.youtube_service.get_random_videos, options
            )

            if not videos:
                self.logger.warning("No random videos found")
                return []

            # Procesar usando el pipeline
            return await self._process_videos_with_stats(videos)

        except Exception as e:
            self.logger.error(f"Error in get_random_audio_tracks: {str(e)}")
            return []

    async def process_video_to_audio_track(
        self, video_info: VideoInfo
    ) -> Optional[AudioTrackData]:
        """Procesa un video individual usando el pipeline"""
        try:
            self.logger.debug(f"Processing single video: {video_info.video_id}")

            result = await self.processing_pipeline.process_single_video(video_info)

            # Actualizar estadísticas
            self._stats["videos_processed"] += 1
            if result:
                self._stats["successful_conversions"] += 1
            else:
                self._stats["failed_conversions"] += 1

            return result

        except Exception as e:
            self.logger.error(f"Error processing video {video_info.video_id}: {str(e)}")
            self._stats["failed_conversions"] += 1
            return None

    async def _process_videos_with_stats(
        self, videos: List[VideoInfo]
    ) -> List[AudioTrackData]:
        """Procesa videos y actualiza estadísticas"""
        self.logger.info(f"Processing {len(videos)} videos")

        # Procesar usando el pipeline
        results = await self.processing_pipeline.process_videos(videos)

        # Actualizar estadísticas
        self._stats["videos_processed"] += len(videos)
        self._stats["successful_conversions"] += len(results)
        self._stats["failed_conversions"] += len(videos) - len(results)

        return results

    # Métodos para mantener compatibilidad con la interfaz existente
    async def search_and_process_music(
        self, query: str, max_results: int = 6
    ) -> List[AudioTrackData]:
        """Método para mantener compatibilidad con la interfaz existente"""
        options = SearchOptions(max_results=max_results)
        tracks = await self.search_and_process_audio(query, options)
        return [track for track in tracks if isinstance(track, MusicTrackData)]

    async def get_random_music_tracks(
        self, max_results: int = 6
    ) -> List[AudioTrackData]:
        """Método para mantener compatibilidad con la interfaz existente"""
        options = SearchOptions(max_results=max_results)
        tracks = await self.get_random_audio_tracks(options)
        return [track for track in tracks if isinstance(track, MusicTrackData)]

    async def process_video_to_track(
        self, video_info: YouTubeVideoInfo
    ) -> Optional[MusicTrackData]:
        """Método para mantener compatibilidad con la interfaz existente"""
        track = await self.process_video_to_audio_track(video_info)
        return track if isinstance(track, MusicTrackData) else None

    # Métodos de utilidad y estadísticas
    def get_performance_stats(self) -> dict:
        """Obtiene estadísticas de rendimiento del servicio"""
        stats = self._stats.copy()
        if stats["videos_processed"] > 0:
            success_rate = (
                stats["successful_conversions"] / stats["videos_processed"] * 100
            )
            stats["success_rate"] = round(success_rate, 2)
        else:
            stats["success_rate"] = 0.0

        return stats

    def reset_stats(self):
        """Resetea las estadísticas de rendimiento"""
        self._stats = {
            "videos_processed": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "cache_hits": 0,
        }

    async def health_check(self) -> dict:
        """Verifica el estado de salud del servicio"""
        health = {
            "service": "healthy",
            "youtube_service": "unknown",
            "pipeline": "healthy",
            "stats": self.get_performance_stats(),
        }

        # Verificar YouTube service si es posible
        try:
            if hasattr(self.youtube_service, "get_quota_usage"):
                quota_info = getattr(self.youtube_service, "get_quota_usage")()
                health["youtube_quota"] = quota_info
                health["youtube_service"] = "healthy"
        except Exception as e:
            health["youtube_service"] = f"error: {str(e)}"

        return health

    def get_config_summary(self) -> dict:
        """Obtiene un resumen de la configuración actual"""
        return {
            "max_concurrent_operations": self.config.max_concurrent_operations,
            "enable_audio_download": self.config.enable_audio_download,
            "enable_thumbnail_processing": self.config.enable_thumbnail_processing,
            "max_retries": self.config.max_retries,
            "retry_delay": self.config.retry_delay,
        }
