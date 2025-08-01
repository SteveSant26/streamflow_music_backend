import asyncio
import uuid
from io import BytesIO
from typing import List, Optional

from common.factories import StorageServiceFactory
from common.mixins.logging_mixin import LoggingMixin

from ..domain.interfaces import (
    IAudioDownloadService,
    IMusicService,
    IYouTubeService,
    MusicTrackData,
    YouTubeVideoInfo,
)
from .services import AudioDownloadService, YouTubeAPIService


class MusicService(IMusicService, LoggingMixin):
    """Servicio principal para gestionar música desde YouTube"""

    def __init__(
        self,
        youtube_service: Optional[IYouTubeService] = None,
        audio_service: Optional[IAudioDownloadService] = None,
    ):
        super().__init__()
        self.youtube_service = youtube_service or YouTubeAPIService()
        self.audio_service = audio_service or AudioDownloadService()
        self.music_storage = StorageServiceFactory.create_music_files_service()
        self.image_storage = StorageServiceFactory.create_album_covers_service()

    async def search_and_process_music(
        self, query: str, max_results: int = 6
    ) -> List[MusicTrackData]:
        """Busca y procesa música desde YouTube"""
        try:
            videos = await self.youtube_service.search_videos(query, max_results)

            # Procesar videos en paralelo (limitado para no sobrecargar)
            semaphore = asyncio.Semaphore(3)  # Máximo 3 descargas simultáneas

            async def process_with_semaphore(video):
                async with semaphore:
                    return await self.process_video_to_track(video)

            tasks = [process_with_semaphore(video) for video in videos]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filtrar resultados exitosos
            processed_tracks = []
            for result in results:
                if isinstance(result, MusicTrackData):
                    processed_tracks.append(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"Error processing video: {str(result)}")

            return processed_tracks

        except Exception as e:
            self.logger.error(f"Error in search_and_process_music: {str(e)}")
            return []

    async def get_random_music_tracks(
        self, max_results: int = 6
    ) -> List[MusicTrackData]:
        """Obtiene pistas de música aleatorias procesadas"""
        try:
            videos = await self.youtube_service.get_random_music_videos(max_results)

            # Procesar videos en paralelo
            semaphore = asyncio.Semaphore(3)

            async def process_with_semaphore(video):
                async with semaphore:
                    return await self.process_video_to_track(video)

            tasks = [process_with_semaphore(video) for video in videos]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filtrar resultados exitosos
            processed_tracks = []
            for result in results:
                if isinstance(result, MusicTrackData):
                    processed_tracks.append(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"Error processing random video: {str(result)}")

            return processed_tracks

        except Exception as e:
            self.logger.error(f"Error in get_random_music_tracks: {str(e)}")
            return []

    async def process_video_to_track(
        self, video_info: YouTubeVideoInfo
    ) -> Optional[MusicTrackData]:
        """Convierte información de video de YouTube a datos de pista musical"""
        try:
            # Descargar audio
            audio_data = await self.audio_service.download_audio(video_info.url)
            if not audio_data:
                self.logger.warning(
                    f"Failed to download audio for video {video_info.video_id}"
                )
                return self._create_track_without_audio(video_info)

            # Generar nombre único para el archivo de audio
            audio_filename = f"audio/{video_info.video_id}_{uuid.uuid4().hex[:8]}.mp3"

            # Subir audio a Supabase Storage
            audio_file_obj = BytesIO(audio_data)
            audio_uploaded = self.music_storage.upload_item(
                audio_filename, audio_file_obj
            )

            if not audio_uploaded:
                self.logger.warning(
                    f"Failed to upload audio for video {video_info.video_id}"
                )
                return self._create_track_without_audio(video_info)

            # Descargar y subir thumbnail
            thumbnail_url = await self._process_thumbnail(video_info)

            # Extraer información del artista y álbum del título
            artist_name, album_title = self._extract_artist_album_info(
                video_info.title, video_info.channel_title
            )

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

    def _create_track_without_audio(
        self, video_info: YouTubeVideoInfo
    ) -> MusicTrackData:
        """Crea datos de pista sin archivo de audio"""
        artist_name, album_title = self._extract_artist_album_info(
            video_info.title, video_info.channel_title
        )

        return MusicTrackData(
            video_id=video_info.video_id,
            title=self._clean_title(video_info.title),
            artist_name=artist_name,
            album_title=album_title,
            duration_seconds=video_info.duration_seconds,
            thumbnail_url=video_info.thumbnail_url,
            genre=video_info.genre,
            tags=video_info.tags,
            url=video_info.url,
        )

    async def _process_thumbnail(self, video_info: YouTubeVideoInfo) -> Optional[str]:
        """Descarga y sube el thumbnail a Supabase Storage"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(video_info.thumbnail_url) as response:
                    if response.status == 200:
                        image_data = await response.read()

                        # Generar nombre único para la imagen
                        image_filename = f"thumbnails/{video_info.video_id}_{uuid.uuid4().hex[:8]}.jpg"

                        # Subir imagen a Supabase Storage
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
        import re

        # Patrón: "Artista - Título"
        dash_pattern = r"^([^-]+)\s*-\s*(.+)$"
        match = re.match(dash_pattern, title)

        if match:
            artist_part = match.group(1).strip()
            # song_part = match.group(2).strip()

            # Limpiar patrones comunes
            artist_part = re.sub(
                r"\s*\(.*?\)\s*", "", artist_part
            )  # Remover paréntesis
            artist_part = re.sub(r"\s*\[.*?\]\s*", "", artist_part)  # Remover corchetes

            return artist_part, None

        # Si no hay patrón, usar el canal como artista
        artist_name = channel_title

        # Limpiar sufijos comunes de canales
        artist_name = re.sub(r"VEVO$", "", artist_name, flags=re.IGNORECASE)
        artist_name = re.sub(r"Official$", "", artist_name, flags=re.IGNORECASE)
        artist_name = re.sub(r"Records$", "", artist_name, flags=re.IGNORECASE)
        artist_name = artist_name.strip()

        return artist_name, None

    def _clean_title(self, title: str) -> str:
        """Limpia el título de la canción"""
        import re

        # Remover patrones comunes
        cleaned = re.sub(r"\(Official.*?\)", "", title, flags=re.IGNORECASE)
        cleaned = re.sub(r"\[Official.*?\]", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"Official Video", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"Official Audio", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"Music Video", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"Lyric Video", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"HD", "", cleaned, flags=re.IGNORECASE)

        # Extraer solo la parte del título si hay " - "
        if " - " in cleaned:
            parts = cleaned.split(" - ")
            if len(parts) >= 2:
                cleaned = parts[1]

        return cleaned.strip()
