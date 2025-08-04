from datetime import datetime
from typing import Any, Dict, List, Optional

from ...interfaces.imedia_service import IMusicService
from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import (
    AudioTrackData,
    DownloadOptions,
    MusicServiceConfig,
    SearchOptions,
    VideoInfo,
    YouTubeVideoInfo,
)
from ...utils.music_metadata_extractor import MusicMetadataExtractor
from .audio_download_service import AudioDownloadService
from .youtube_service import YouTubeAPIService


class UnifiedMusicService(IMusicService, LoggingMixin):
    """
    Servicio unificado que combina todas las funcionalidades de música:
    - Búsqueda en YouTube con extracción de metadatos
    - Descarga de audio
    - Integración con artistas y álbumes
    """

    def __init__(
        self,
        config: Optional[MusicServiceConfig] = None,
        youtube_service: Optional[YouTubeAPIService] = None,
        audio_service: Optional[AudioDownloadService] = None,
    ):
        super().__init__()
        self.config = config or MusicServiceConfig()

        # Servicios auxiliares
        self.youtube_service = youtube_service or YouTubeAPIService()
        self.audio_service = audio_service or AudioDownloadService()
        self.metadata_extractor = MusicMetadataExtractor()

        # Repositorios (se inyectarán externamente si es necesario)
        self.artist_repository = None
        self.album_repository = None

        # Métricas
        self._metrics = {
            "searches_performed": 0,
            "videos_processed": 0,
            "audio_downloads": 0,
            "metadata_extractions": 0,
            "errors": 0,
        }

    def configure_repositories(self, artist_repository: Any, album_repository: Any):
        self.artist_repository = artist_repository
        self.album_repository = album_repository

    async def search_and_process_audio(
        self,
        query: str,
        options: Optional[SearchOptions] = None,
        download_audio: bool = False,
        extract_metadata: bool = True,
    ) -> List[AudioTrackData]:
        """
        Busca música y procesa completamente

        Args:
            query: Consulta de búsqueda
            options: Opciones de búsqueda
            download_audio: Si descargar el audio
            extract_metadata: Si extraer metadatos de artistas/álbumes

        Returns:
            Lista de pistas de audio procesadas
        """
        try:
            self._metrics["searches_performed"] += 1

            # 1. Buscar videos en YouTube
            videos = await self._search_videos_with_metadata(
                query, options, extract_metadata
            )

            if not videos:
                self.logger.warning(f"No videos found for query: {query}")
                return []

            # 2. Procesar videos a pistas de audio
            audio_tracks = []
            for video in videos:
                try:
                    track = await self._process_video_to_audio_track(
                        video, download_audio=download_audio
                    )
                    if track:
                        audio_tracks.append(track)
                        self._metrics["videos_processed"] += 1

                except Exception as e:
                    self.logger.error(
                        f"Error processing video {video.video_id}: {str(e)}"
                    )
                    self._metrics["errors"] += 1

            self.logger.info(
                f"Processed {len(audio_tracks)} tracks from query '{query}'"
            )
            return audio_tracks

        except Exception as e:
            self.logger.error(f"Error in search_and_process_audio: {str(e)}")
            self._metrics["errors"] += 1
            return []

    async def get_random_music(
        self,
        options: Optional[SearchOptions] = None,
        download_audio: bool = False,
        extract_metadata: bool = True,
    ) -> List[AudioTrackData]:
        """
        Obtiene música aleatoria completamente procesada

        Args:
            options: Opciones de búsqueda
            download_audio: Si descargar el audio
            extract_metadata: Si extraer metadatos

        Returns:
            Lista de pistas de audio aleatorias
        """
        try:
            # 1. Obtener videos aleatorios
            videos = await self._get_random_videos_with_metadata(
                options, extract_metadata
            )

            if not videos:
                self.logger.warning("No random videos obtained")
                return []

            # 2. Procesar a pistas de audio
            audio_tracks = []
            for video in videos:
                try:
                    track = await self._process_video_to_audio_track(
                        video, download_audio=download_audio
                    )
                    if track:
                        audio_tracks.append(track)

                except Exception as e:
                    self.logger.error(
                        f"Error processing random video {video.video_id}: {str(e)}"
                    )

            return audio_tracks

        except Exception as e:
            self.logger.error(f"Error getting random music: {str(e)}")
            return []

    async def download_audio_from_video(
        self, video_id: str, options: Optional[DownloadOptions] = None
    ) -> Optional[bytes]:
        """
        Descarga audio de un video específico

        Args:
            video_id: ID del video de YouTube
            options: Opciones de descarga

        Returns:
            Datos del audio en bytes o None si falló
        """
        try:
            self._metrics["audio_downloads"] += 1
            url = f"https://www.youtube.com/watch?v={video_id}"
            return await self.audio_service.download_audio(url, options)

        except Exception as e:
            self.logger.error(f"Error downloading audio for video {video_id}: {str(e)}")
            self._metrics["errors"] += 1
            return None

    async def _search_videos_with_metadata(
        self,
        query: str,
        options: Optional[SearchOptions],
        extract_metadata: bool = True,
    ) -> List[YouTubeVideoInfo]:
        """Busca videos y opcionalmente extrae metadatos"""
        videos = await self.youtube_service.search_videos(query, options)

        if extract_metadata and videos:
            self._metrics["metadata_extractions"] += len(videos)
            return [
                self.metadata_extractor.extract_music_metadata(video)
                for video in videos
            ]

        return videos

    async def _get_random_videos_with_metadata(
        self, options: Optional[SearchOptions], extract_metadata: bool = True
    ) -> List[YouTubeVideoInfo]:
        """Obtiene videos aleatorios y opcionalmente extrae metadatos"""
        videos = await self.youtube_service.get_random_videos(options)

        if extract_metadata and videos:
            self._metrics["metadata_extractions"] += len(videos)
            return [
                self.metadata_extractor.extract_music_metadata(video)
                for video in videos
            ]

        return videos

    async def _process_video_to_audio_track(
        self, video: YouTubeVideoInfo, download_audio: bool = False
    ) -> Optional[AudioTrackData]:
        """Convierte un video a AudioTrackData"""
        try:
            # Determinar artista principal
            main_artist = "Unknown Artist"
            if video.extracted_artists:
                main_artist = video.extracted_artists[0].name
            else:
                main_artist = video.channel_title

            # Determinar álbum
            album_title = None
            if video.extracted_albums:
                album_title = video.extracted_albums[0].title

            # Descargar audio si se solicita
            audio_data = None
            audio_filename = None
            if download_audio:
                audio_data = await self.download_audio_from_video(video.video_id)
                if audio_data:
                    audio_filename = f"{video.video_id}.mp3"

            # Crear AudioTrackData
            return AudioTrackData(
                video_id=video.video_id,
                title=video.title,
                artist_name=main_artist,
                album_title=album_title,
                duration_seconds=video.duration_seconds,
                thumbnail_url=video.thumbnail_url,
                genre=video.genre,
                tags=video.tags,
                url=video.url,
                audio_file_data=audio_data,
                audio_file_name=audio_filename,
                extracted_artists=video.extracted_artists,
                extracted_albums=video.extracted_albums,
            )

        except Exception as e:
            self.logger.error(f"Error converting video to audio track: {str(e)}")
            return None

    def get_service_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del servicio"""
        return {
            **self._metrics,
            "youtube_quota_usage": (
                self.youtube_service.get_quota_usage()
                if hasattr(self.youtube_service, "get_quota_usage")
                else {}
            ),
            "service_uptime": "N/A",  # Se podría implementar
            "last_activity": datetime.now().isoformat(),
        }

    async def cleanup(self):
        """Limpia recursos del servicio"""
        try:
            await self.audio_service.cleanup()
            # Limpiar métricas
            self._metrics = {
                "searches_performed": 0,
                "videos_processed": 0,
                "audio_downloads": 0,
                "metadata_extractions": 0,
                "errors": 0,
            }

            self.logger.info("UnifiedMusicService cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    async def get_random_music_tracks(
        self, max_results: int = 6
    ) -> List[AudioTrackData]:
        """Implementación requerida por IMusicService"""
        options = SearchOptions(max_results=max_results)
        return await self.get_random_music(options, download_audio=False)

    async def search_and_process_music(
        self, query: str, max_results: int = 6
    ) -> List[AudioTrackData]:
        """Implementación requerida por IMusicService"""
        options = SearchOptions(max_results=max_results)
        return await self.search_and_process_audio(query, options, download_audio=False)

    # Métodos adicionales para más funcionalidad
    async def search_music_tracks(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        """Búsqueda avanzada con opciones personalizadas"""
        return await self.search_and_process_audio(query, options, download_audio=False)

    async def get_music_track_details(self, track_id: str) -> Optional[AudioTrackData]:
        """Obtiene detalles de una pista específica"""
        try:
            video = await self.youtube_service.get_video_details(track_id)
            if video:
                # Extraer metadatos
                video_with_metadata = self.metadata_extractor.extract_music_metadata(
                    video
                )
                return await self._process_video_to_audio_track(video_with_metadata)
            return None
        except Exception as e:
            self.logger.error(f"Error getting track details for {track_id}: {str(e)}")
            return None

    # Implementar métodos requeridos por IAudioProcessingService
    async def get_random_audio_tracks(
        self, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        """Implementación requerida por IAudioProcessingService"""
        return await self.get_random_music(options, download_audio=False)

    async def process_video_to_audio_track(
        self, video_info: VideoInfo
    ) -> Optional[AudioTrackData]:
        """Implementación requerida por IAudioProcessingService"""
        try:
            # Convertir a YouTubeVideoInfo si es necesario
            if isinstance(video_info, YouTubeVideoInfo):
                youtube_video = video_info
            else:
                # Crear YouTubeVideoInfo básico desde VideoInfo
                youtube_video = YouTubeVideoInfo(
                    video_id=video_info.video_id,
                    title=video_info.title,
                    channel_title=video_info.channel_title,
                    channel_id=video_info.channel_id,
                    thumbnail_url=video_info.thumbnail_url,
                    description=video_info.description,
                    duration_seconds=video_info.duration_seconds,
                    published_at=video_info.published_at,
                    view_count=video_info.view_count,
                    like_count=video_info.like_count,
                    tags=video_info.tags,
                    category_id=video_info.category_id,
                    genre=video_info.genre,
                    url=video_info.url,
                )

            # Extraer metadatos si no están presentes
            if (
                not youtube_video.extracted_artists
                and not youtube_video.extracted_albums
            ):
                youtube_video = self.metadata_extractor.extract_music_metadata(
                    youtube_video
                )

            return await self._process_video_to_audio_track(
                youtube_video, download_audio=False
            )
        except Exception as e:
            self.logger.error(f"Error processing video to audio track: {str(e)}")
            return None
