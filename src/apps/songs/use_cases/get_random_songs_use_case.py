import asyncio
from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.types.media_types import SearchOptions
from common.utils.logging_decorators import log_execution, log_performance
from src.common.factories.unified_music_service_factory import get_music_service

from ..api.dtos.song_dtos import RandomSongsRequestDTO
from ..domain.entities import SongEntity
from ..domain.repository import ISongRepository
from .save_track_as_song_use_case import SaveTrackAsSongUseCase


class GetRandomSongsUseCase(BaseUseCase[RandomSongsRequestDTO, List[SongEntity]]):
    """Caso de uso para obtener canciones aleatorias"""

    def __init__(self, song_repository: ISongRepository, music_service=None):
        super().__init__()
        self.song_repository = song_repository
        self.music_service = music_service or get_music_service()
        # Semáforo para limitar concurrencia en descargas
        self.download_semaphore = asyncio.Semaphore(2)  # Máximo 2 descargas simultáneas

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(
        threshold_seconds=4.0
    )  # Puede incluir búsquedas externas y procesamiento
    async def execute(self, request_dto: RandomSongsRequestDTO) -> List[SongEntity]:
        """
        Obtiene canciones aleatorias. Si no hay suficientes en la BD o force_refresh=True,
        busca nuevas canciones desde YouTube.

        Args:
            request_dto: DTO con count y force_refresh

        Returns:
            Lista de canciones aleatorias
        """
        count = request_dto.count
        force_refresh = request_dto.force_refresh
        try:
            # Primero intentar obtener canciones de la base de datos
            if not force_refresh:
                existing_songs = await self.song_repository.get_random(count)
                if len(existing_songs) >= count:
                    self.logger.info(
                        f"Returning {len(existing_songs)} existing random songs"
                    )
                    return existing_songs

            # Si no hay suficientes canciones, buscar nuevas desde YouTube
            self.logger.info("Fetching new random songs from YouTube")

            # Reducir el número de resultados solicitados para mejorar rendimiento
            search_count = min(count, 8)  # Máximo 8 por solicitud
            options = SearchOptions(max_results=search_count)
            new_tracks = await self.music_service.get_random_audio_tracks(options)

            # Procesar tracks de forma más eficiente
            saved_songs = await self._process_tracks_concurrently(new_tracks)

            # Si aún no tenemos suficientes, combinar con las existentes
            if len(saved_songs) < count:
                needed = count - len(saved_songs)
                existing_songs = await self.song_repository.get_random(needed)
                saved_songs.extend(existing_songs)

            return saved_songs[:count]

        except Exception as e:
            self.logger.error(f"Error getting random songs: {str(e)}")
            # Fallback: intentar obtener solo canciones existentes
            try:
                return await self.song_repository.get_random(count)
            except Exception as fallback_error:
                self.logger.error(f"Fallback also failed: {str(fallback_error)}")
                return []

    async def _process_tracks_concurrently(self, tracks) -> List[SongEntity]:
        """Procesa múltiples tracks de forma concurrente pero controlada"""
        saved_songs = []

        async def process_single_track(track):
            """Procesa un track individual"""
            async with self.download_semaphore:
                try:
                    # Verificar si ya existe
                    existing_song = await self.song_repository.get_by_source(
                        "youtube", track.video_id
                    )

                    if existing_song:
                        return existing_song

                    # Crear nuevo caso de uso para cada track para evitar conflictos
                    save_track_use_case = SaveTrackAsSongUseCase(self.song_repository)
                    new_song = await save_track_use_case.execute(track)
                    return new_song
                except Exception as e:
                    self.logger.warning(
                        f"Failed to process track {track.video_id}: {str(e)}"
                    )
                    return None

        # Procesar tracks de forma concurrente pero limitada
        tasks = [process_single_track(track) for track in tracks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar resultados válidos
        for result in results:
            if isinstance(result, SongEntity):
                saved_songs.append(result)
            elif isinstance(result, Exception):
                self.logger.warning(f"Task failed with exception: {str(result)}")

        return saved_songs
