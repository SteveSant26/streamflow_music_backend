from typing import List

from common.factories import MediaServiceFactory
from common.interfaces.ibase_use_case import BaseUseCase
from common.types.media_types import SearchOptions
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos.song_dtos import RandomSongsRequestDTO
from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository
from .save_track_as_song_use_case import SaveTrackAsSongUseCase


class GetRandomSongsUseCase(BaseUseCase[RandomSongsRequestDTO, List[SongEntity]]):
    """Caso de uso para obtener canciones aleatorias"""

    def __init__(self, song_repository: ISongRepository, music_service=None):
        super().__init__()
        self.song_repository = song_repository
        self.music_service = music_service or MediaServiceFactory.create_music_service()

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

            options = SearchOptions(max_results=count)
            new_tracks = await self.music_service.get_random_audio_tracks(options)

            # Guardar las nuevas canciones en la base de datos
            saved_songs = []
            for track in new_tracks:
                existing_song = await self.song_repository.get_by_source(
                    "youtube", track.video_id
                )

                if existing_song:
                    saved_songs.append(existing_song)
                else:
                    save_track_use_case = SaveTrackAsSongUseCase(self.song_repository)
                    new_song = await save_track_use_case.execute(track)
                    if new_song:
                        saved_songs.append(new_song)

            # Si aún no tenemos suficientes, combinar con las existentes
            if len(saved_songs) < count:
                existing_songs = await self.song_repository.get_random(
                    count - len(saved_songs)
                )
                saved_songs.extend(existing_songs)

            return saved_songs[:count]

        except Exception as e:
            self.logger.error(f"Error getting random songs: {str(e)}")
            return await self.song_repository.get_random(
                count,
            )
