"""
Estrategias para procesamiento de videos específicas por tipo de contenido
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import AudioTrackData, MusicTrackData, VideoInfo
from .video_processing_pipeline import VideoProcessor


class BaseVideoProcessor(VideoProcessor, LoggingMixin, ABC):
    """Procesador base para videos"""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    @abstractmethod
    async def process(self, video_info: VideoInfo) -> Optional[AudioTrackData]:
        """Procesa un video y retorna datos de audio track"""

    def should_process(self, video_info: VideoInfo) -> bool:
        """Determina si este procesador debe manejar el video"""
        return True


class MusicVideoProcessor(BaseVideoProcessor):
    """Procesador especializado para videos musicales"""

    def __init__(
        self,
        thumbnail_processor,
        audio_processor,
        metadata_extractor,
        quality_filters: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("MusicVideoProcessor")
        self.thumbnail_processor = thumbnail_processor
        self.audio_processor = audio_processor
        self.metadata_extractor = metadata_extractor
        self.quality_filters = quality_filters or {}

    def should_process(self, video_info: VideoInfo) -> bool:
        """Verifica si el video es apropiado para procesamiento musical"""
        # Filtros de calidad básicos
        min_duration = self.quality_filters.get("min_duration", 30)  # 30 segundos
        max_duration = self.quality_filters.get("max_duration", 600)  # 10 minutos

        if not (min_duration <= video_info.duration_seconds <= max_duration):
            self.logger.debug(
                f"Video {video_info.video_id} duration out of range: {video_info.duration_seconds}s"
            )
            return False

        # Verificar que tenga título válido
        if not video_info.title or len(video_info.title.strip()) < 3:
            self.logger.debug(f"Video {video_info.video_id} has invalid title")
            return False

        return True

    async def process(self, video_info: VideoInfo) -> Optional[AudioTrackData]:
        """Procesa un video musical"""
        if not self.should_process(video_info):
            self.logger.debug(
                f"Skipping video {video_info.video_id} - quality filters failed"
            )
            return None

        try:
            # Extraer metadatos
            title, artist_name, album_title = await self._extract_metadata(video_info)

            # Procesar thumbnail y audio en paralelo si es posible
            thumbnail_task = self._process_thumbnail(video_info)
            audio_task = self._process_audio(video_info)

            results = await asyncio.gather(
                thumbnail_task, audio_task, return_exceptions=True
            )

            thumbnail_result, audio_result = results

            # Manejar excepciones de las tareas paralelas
            if isinstance(thumbnail_result, Exception):
                self.logger.warning(f"Thumbnail processing failed: {thumbnail_result}")
                thumbnail_url = video_info.thumbnail_url
            elif isinstance(thumbnail_result, str):
                thumbnail_url = thumbnail_result
            else:
                thumbnail_url = video_info.thumbnail_url

            if isinstance(audio_result, Exception):
                self.logger.warning(f"Audio processing failed: {audio_result}")
                audio_data, audio_filename = None, None
            elif isinstance(audio_result, tuple) and len(audio_result) == 2:
                audio_data, audio_filename = audio_result
            else:
                audio_data, audio_filename = None, None

            # Crear track data
            return MusicTrackData(
                video_id=video_info.video_id,
                title=title,
                artist_name=artist_name,
                album_title=album_title,
                duration_seconds=video_info.duration_seconds,
                thumbnail_url=thumbnail_url,
                genre=video_info.genre,
                tags=video_info.tags,
                url=video_info.url,
                audio_file_data=audio_data,
                audio_file_name=audio_filename,
            )

        except Exception as e:
            self.logger.error(
                f"Failed to process music video {video_info.video_id}: {str(e)}"
            )
            return None

    async def _extract_metadata(
        self, video_info: VideoInfo
    ) -> tuple[str, str, Optional[str]]:
        """Extrae metadatos del video"""
        return self.metadata_extractor.extract_track_metadata(video_info)

    async def _process_thumbnail(self, video_info: VideoInfo) -> Optional[str]:
        """Procesa el thumbnail del video"""
        return await self.thumbnail_processor.process_thumbnail(video_info)

    async def _process_audio(
        self, video_info: VideoInfo
    ) -> tuple[Optional[bytes], Optional[str]]:
        """Procesa el audio del video"""
        return await self.audio_processor.process_audio(video_info)


class PodcastVideoProcessor(BaseVideoProcessor):
    """Procesador especializado para podcasts y contenido hablado"""

    def __init__(self, audio_processor, metadata_extractor):
        super().__init__("PodcastVideoProcessor")
        self.audio_processor = audio_processor
        self.metadata_extractor = metadata_extractor

    def should_process(self, video_info: VideoInfo) -> bool:
        """Verifica si el video es un podcast o contenido hablado"""
        # Criterios para podcasts: duración larga, palabras clave específicas
        if video_info.duration_seconds < 300:  # Menos de 5 minutos
            return False

        podcast_keywords = [
            "podcast",
            "interview",
            "talk",
            "discussion",
            "conversation",
        ]
        title_lower = video_info.title.lower()

        return any(keyword in title_lower for keyword in podcast_keywords)

    async def process(self, video_info: VideoInfo) -> Optional[AudioTrackData]:
        """Procesa un podcast"""
        # Implementación específica para podcasts
        # Por ahora, procesamiento básico
        title, artist_name, _ = self.metadata_extractor.extract_track_metadata(
            video_info
        )
        audio_data, audio_filename = await self.audio_processor.process_audio(
            video_info
        )

        return AudioTrackData(
            video_id=video_info.video_id,
            title=title,
            artist_name=artist_name,
            album_title="Podcast",
            duration_seconds=video_info.duration_seconds,
            thumbnail_url=video_info.thumbnail_url,
            genre="Podcast",
            tags=video_info.tags,
            url=video_info.url,
            audio_file_data=audio_data,
            audio_file_name=audio_filename,
        )


class VideoProcessorStrategy:
    """Estrategia que selecciona el procesador apropiado para cada video"""

    def __init__(self, processors: List[BaseVideoProcessor]):
        self.processors = processors

    def get_processor(self, video_info: VideoInfo) -> Optional[BaseVideoProcessor]:
        """Selecciona el procesador apropiado para un video"""
        for processor in self.processors:
            if processor.should_process(video_info):
                return processor
        return None

    async def process(self, video_info: VideoInfo) -> Optional[AudioTrackData]:
        """Procesa un video usando el procesador apropiado"""
        processor = self.get_processor(video_info)
        if processor:
            return await processor.process(video_info)
        return None
