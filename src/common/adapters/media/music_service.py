import asyncio
import uuid
from io import BytesIO
from typing import List, Optional, Sequence

import aiohttp

from ...interfaces.imedia_service import (
    IAudioDownloadService,
    IMusicService,
    IYouTubeService,
)
from ...interfaces.istorage_service import IStorageService
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
from ...utils.validators import MediaDataValidator, TextCleaner


class ThumbnailProcessor(LoggingMixin):
    """Procesador de thumbnails independiente"""

    def __init__(self, image_storage, retry_manager: RetryManager):
        super().__init__()
        self.image_storage = image_storage
        self.retry_manager = retry_manager

    async def process_thumbnail(self, video_info: VideoInfo) -> Optional[str]:
        """Descarga y sube el thumbnail al almacenamiento"""
        try:
            return await self.retry_manager.execute_with_retry(
                self._download_and_upload_thumbnail, video_info
            )
        except Exception as e:
            self.logger.error(
                f"Error processing thumbnail for {video_info.video_id}: {str(e)}"
            )
            return None

    async def _download_and_upload_thumbnail(
        self, video_info: VideoInfo
    ) -> Optional[str]:
        """Descarga y sube el thumbnail"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                video_info.thumbnail_url, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    image_data = await response.read()

                    # Validar tamaño de imagen
                    if len(image_data) > 10 * 1024 * 1024:  # 10MB max
                        self.logger.warning(
                            f"Thumbnail too large: {len(image_data)} bytes"
                        )
                        return None

                    # Generar nombre único para la imagen
                    image_filename = (
                        f"thumbnails/{video_info.video_id}_{uuid.uuid4().hex[:8]}.jpg"
                    )

                    # Subir imagen al almacenamiento
                    image_file_obj = BytesIO(image_data)
                    uploaded = self.image_storage.upload_item(
                        image_filename, image_file_obj
                    )

                    if uploaded:
                        return self.image_storage.get_item_url(image_filename)

        return None


class AudioProcessor(LoggingMixin):
    """Procesador de audio independiente"""

    def __init__(
        self,
        audio_service: Optional[IAudioDownloadService],
        music_storage,
        retry_manager: RetryManager,
    ):
        super().__init__()
        self.audio_service = audio_service
        self.music_storage = music_storage
        self.retry_manager = retry_manager
        self.media_validator = MediaDataValidator()

    async def process_audio(
        self, video_info: VideoInfo
    ) -> tuple[Optional[bytes], Optional[str]]:
        """Procesa el audio de un video"""
        if not self.audio_service:
            return None, None

        try:
            return await self.retry_manager.execute_with_retry(
                self._download_and_upload_audio, video_info
            ) or (None, None)
        except Exception as e:
            self.logger.error(
                f"Error processing audio for {video_info.video_id}: {str(e)}"
            )
            return None, None

    async def _download_and_upload_audio(
        self, video_info: VideoInfo
    ) -> tuple[Optional[bytes], Optional[str]]:
        """Descarga y sube el audio"""
        if not self.audio_service:
            return None, None

        audio_data = await self.audio_service.download_audio(video_info.url)

        if audio_data:
            # Validar tamaño del archivo
            if not self.media_validator.validate_filesize(len(audio_data)):
                self.logger.warning(f"Audio file too large: {len(audio_data)} bytes")
                return None, None

            # Generar nombre único para el archivo de audio
            audio_filename = f"audio/{video_info.video_id}_{uuid.uuid4().hex[:8]}.mp3"

            # Subir audio a storage
            if await self._upload_audio_to_storage(audio_data, audio_filename):
                return audio_data, audio_filename

        return None, None

    async def _upload_audio_to_storage(self, audio_data: bytes, filename: str) -> bool:
        """Sube el archivo de audio al almacenamiento"""
        try:
            audio_file_obj = BytesIO(audio_data)
            return self.music_storage.upload_item(filename, audio_file_obj)
        except Exception as e:
            self.logger.error(f"Error uploading audio to storage: {str(e)}")
            return False


class MetadataExtractor(LoggingMixin):
    """Extractor de metadatos independiente"""

    def __init__(self):
        super().__init__()
        self.text_cleaner = TextCleaner()

    def extract_track_metadata(
        self, video_info: VideoInfo
    ) -> tuple[str, str, Optional[str]]:
        """Extrae metadatos de la pista"""
        # Limpiar título
        clean_title = self.text_cleaner.clean_title(video_info.title)

        # Extraer información del artista
        artist_from_title = self.text_cleaner.extract_artist_from_title(
            video_info.title
        )

        if artist_from_title:
            artist_name = artist_from_title
        else:
            artist_name = self.text_cleaner.clean_channel_name(video_info.channel_title)

        # Por ahora no extraemos álbum, pero se puede implementar
        album_title = None

        return clean_title, artist_name, album_title


class MusicService(IMusicService, LoggingMixin):
    """Servicio principal mejorado para gestionar música desde YouTube"""

    def __init__(
        self,
        config: Optional[MusicServiceConfig] = None,
        youtube_service: Optional[IYouTubeService] = None,
        audio_service: Optional[IAudioDownloadService] = None,
        music_storage: Optional[IStorageService] = None,
        image_storage: Optional[IStorageService] = None,
    ):
        super().__init__()
        self.config = config or MusicServiceConfig()
        self.youtube_service = youtube_service
        self.audio_service = audio_service

        # Inyección de dependencias para servicios de almacenamiento
        # Si no se proporcionan, se pueden crear lazy loading en el factory
        self.music_storage = music_storage
        self.image_storage = image_storage

        # Inicializar componentes auxiliares
        self.retry_manager = RetryManager(
            max_retries=self.config.max_retries, base_delay=self.config.retry_delay
        )

        # Inicializar procesadores especializados solo si los servicios están disponibles
        self.thumbnail_processor = (
            ThumbnailProcessor(self.image_storage, self.retry_manager)
            if self.image_storage
            else None
        )

        self.audio_processor = AudioProcessor(
            self.audio_service if self.config.enable_audio_download else None,
            self.music_storage,
            self.retry_manager,
        )

        self.metadata_extractor = MetadataExtractor()

    async def search_and_process_audio(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        """Busca y procesa audio desde videos"""
        try:
            if not self.youtube_service:
                self.logger.error("YouTube service not configured")
                return []

            videos = await self.youtube_service.search_videos(query, options)
            return await self._process_videos_to_tracks(videos)

        except Exception as e:
            self.logger.error(f"Error in search_and_process_audio: {str(e)}")
            return []

    async def get_random_audio_tracks(
        self, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        """Obtiene pistas de audio aleatorias procesadas"""
        try:
            if not self.youtube_service:
                self.logger.error("YouTube service not configured")
                return []

            videos = await self.youtube_service.get_random_videos(options)
            return await self._process_videos_to_tracks(videos)

        except Exception as e:
            self.logger.error(f"Error in get_random_audio_tracks: {str(e)}")
            return []

    async def process_video_to_audio_track(
        self, video_info: VideoInfo
    ) -> Optional[AudioTrackData]:
        """Convierte información de video a datos de pista de audio"""
        try:
            # Extraer metadatos
            (
                title,
                artist_name,
                album_title,
            ) = self.metadata_extractor.extract_track_metadata(video_info)

            # Procesar thumbnail si está habilitado y el procesador está disponible
            thumbnail_url = video_info.thumbnail_url
            if self.config.enable_thumbnail_processing and self.thumbnail_processor:
                processed_thumbnail = await self.thumbnail_processor.process_thumbnail(
                    video_info
                )
                if processed_thumbnail:
                    thumbnail_url = processed_thumbnail

            # Procesar audio si está habilitado
            audio_data, audio_filename = None, None
            if self.config.enable_audio_download:
                audio_data, audio_filename = await self.audio_processor.process_audio(
                    video_info
                )

            # Crear datos de la pista como MusicTrackData
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
            self.logger.error(f"Error processing video {video_info.video_id}: {str(e)}")
            return None

    async def _process_videos_to_tracks(
        self, videos: Sequence[VideoInfo]
    ) -> List[AudioTrackData]:
        """Procesa una lista de videos en paralelo"""
        if not videos:
            return []

        # Procesar videos en paralelo con semáforo para limitar concurrencia
        semaphore = asyncio.Semaphore(self.config.max_concurrent_operations)

        async def process_with_semaphore(video):
            async with semaphore:
                return await self.process_video_to_audio_track(video)

        tasks = [process_with_semaphore(video) for video in videos]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar resultados exitosos
        processed_tracks = []
        for result in results:
            if isinstance(result, AudioTrackData):
                processed_tracks.append(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Error processing video: {str(result)}")

        self.logger.info(
            f"Successfully processed {len(processed_tracks)}/{len(videos)} videos"
        )
        return processed_tracks

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
