import asyncio
import re
import uuid
from io import BytesIO
from typing import List, Optional, Sequence

import aiohttp

from ...factories import StorageServiceFactory
from ...interfaces.imedia_service import (
    IAudioDownloadService,
    IMusicService,
    IYouTubeService,
)
from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import (
    AudioTrackData,
    MusicTrackData,
    SearchOptions,
    VideoInfo,
    YouTubeVideoInfo,
)


class MusicService(IMusicService, LoggingMixin):
    """Servicio principal mejorado para gestionar música desde YouTube"""

    def __init__(
        self,
        youtube_service: Optional[IYouTubeService] = None,
        audio_service: Optional[IAudioDownloadService] = None,
        max_concurrent_downloads: int = 3,
    ):
        super().__init__()
        self.youtube_service = youtube_service
        self.audio_service = audio_service
        self.max_concurrent_downloads = max_concurrent_downloads

        # Inicializar servicios de almacenamiento
        self.music_storage = StorageServiceFactory.create_music_files_service()
        self.image_storage = StorageServiceFactory.create_album_covers_service()

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
            # Descargar audio si el servicio está disponible
            audio_data = None
            audio_filename = None

            if self.audio_service:
                audio_data = await self.audio_service.download_audio(video_info.url)

                if audio_data:
                    # Generar nombre único para el archivo de audio
                    audio_filename = (
                        f"audio/{video_info.video_id}_{uuid.uuid4().hex[:8]}.mp3"
                    )

                    # Subir audio a storage
                    if not await self._upload_audio_to_storage(
                        audio_data, audio_filename
                    ):
                        self.logger.warning(
                            f"Failed to upload audio for video {video_info.video_id}"
                        )
                        audio_data = None
                        audio_filename = None

            # Procesar thumbnail
            thumbnail_url = await self._process_thumbnail(video_info)

            # Extraer información del artista y álbum
            artist_name, album_title = self._extract_artist_album_info(
                video_info.title, video_info.channel_title
            )

            # Crear datos de la pista como MusicTrackData (hereda de AudioTrackData)
            return MusicTrackData(
                video_id=video_info.video_id,
                title=self._clean_title(video_info.title),
                artist_name=artist_name,
                album_title=album_title,
                duration_seconds=video_info.duration_seconds,
                thumbnail_url=thumbnail_url or video_info.thumbnail_url,
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
        semaphore = asyncio.Semaphore(self.max_concurrent_downloads)

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

    async def _upload_audio_to_storage(self, audio_data: bytes, filename: str) -> bool:
        """Sube el archivo de audio al almacenamiento"""
        try:
            audio_file_obj = BytesIO(audio_data)
            return self.music_storage.upload_item(filename, audio_file_obj)
        except Exception as e:
            self.logger.error(f"Error uploading audio to storage: {str(e)}")
            return False

    async def _process_thumbnail(self, video_info: VideoInfo) -> Optional[str]:
        """Descarga y sube el thumbnail al almacenamiento"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_info.thumbnail_url) as response:
                    if response.status == 200:
                        image_data = await response.read()

                        # Generar nombre único para la imagen
                        image_filename = f"thumbnails/{video_info.video_id}_{uuid.uuid4().hex[:8]}.jpg"

                        # Subir imagen al almacenamiento
                        image_file_obj = BytesIO(image_data)
                        uploaded = self.image_storage.upload_item(
                            image_filename, image_file_obj
                        )

                        if uploaded:
                            return self.image_storage.get_item_url(image_filename)

            return None

        except Exception as e:
            self.logger.error(
                f"Error processing thumbnail for {video_info.video_id}: {str(e)}"
            )
            return None

    def _extract_artist_album_info(
        self, title: str, channel_title: str
    ) -> tuple[str, Optional[str]]:
        """Extrae información del artista y álbum del título y canal"""
        # Patrones comunes para extraer artista y título
        dash_pattern = r"^([^-]+)\s*-\s*(.+)$"
        match = re.match(dash_pattern, title)

        if match:
            artist_part = match.group(1).strip()
            # Limpiar patrones comunes
            artist_part = re.sub(
                r"\s*\(.*?\)\s*", "", artist_part
            )  # Remover paréntesis
            artist_part = re.sub(r"\s*\[.*?\]\s*", "", artist_part)  # Remover corchetes
            return artist_part, None

        # Si no hay patrón, usar el canal como artista
        artist_name = self._clean_channel_name(channel_title)
        return artist_name, None

    def _clean_channel_name(self, channel_name: str) -> str:
        """Limpia el nombre del canal para usar como artista"""
        # Limpiar sufijos comunes de canales
        cleaned = re.sub(r"VEVO$", "", channel_name, flags=re.IGNORECASE)
        cleaned = re.sub(r"Official$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"Records$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"Music$", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def _clean_title(self, title: str) -> str:
        """Limpia el título de la canción"""
        # Remover patrones comunes
        patterns_to_remove = [
            r"\(Official[^\)]*\)",
            r"\[Official[^\]]*\]",
            r"Official Video",
            r"Official Audio",
            r"Music Video",
            r"Lyric Video",
            r"HD",
            r"\(HD\)",
            r"\[HD\]",
        ]

        cleaned = title
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Extraer solo la parte del título si hay " - "
        if " - " in cleaned:
            parts = cleaned.split(" - ")
            if len(parts) >= 2:
                cleaned = parts[1]

        return cleaned.strip()

    # Mantener compatibilidad con la interfaz existente
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
