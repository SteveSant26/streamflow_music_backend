from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ...music_search.infrastructure.music_service import MusicService
from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository


class GetRandomSongsUseCase(BaseUseCase[dict, List[SongEntity]]):
    """Caso de uso para obtener canciones aleatorias"""

    def __init__(self, song_repository: ISongRepository, music_service: MusicService):
        super().__init__()
        self.song_repository = song_repository
        self.music_service = music_service

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    async def execute(
        self, count: int = 6, force_refresh: bool = False
    ) -> List[SongEntity]:
        """
        Obtiene canciones aleatorias. Si no hay suficientes en la BD o force_refresh=True,
        busca nuevas canciones desde YouTube.

        Args:
            count: Número de canciones a obtener
            force_refresh: Si debe buscar nuevas canciones aunque existan suficientes

        Returns:
            Lista de canciones aleatorias
        """
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
            new_tracks = await self.music_service.get_random_music_tracks(count)

            # Guardar las nuevas canciones en la base de datos
            saved_songs = []
            for track in new_tracks:
                existing_song = await self.song_repository.get_by_source(
                    "youtube", track.video_id
                )

                if existing_song:
                    saved_songs.append(existing_song)
                else:
                    # Usar otro caso de uso para guardar la canción
                    from .save_track_as_song_use_case import SaveTrackAsSongUseCase

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
            # En caso de error, intentar devolver canciones existentes
            return await self.song_repository.get_random(count)
