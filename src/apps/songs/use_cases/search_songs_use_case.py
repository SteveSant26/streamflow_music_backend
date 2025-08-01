from typing import List

from common.factories import MediaServiceFactory
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository


class SearchSongsUseCase(BaseUseCase[dict, List[SongEntity]]):
    """Caso de uso para buscar canciones"""

    def __init__(self, song_repository: ISongRepository, music_service=None):
        super().__init__()
        self.song_repository = song_repository
        self.music_service = music_service or MediaServiceFactory.create_music_service()

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)  # Búsqueda puede incluir consultas externas
    async def execute(
        self, query: str, limit: int = 20, include_youtube: bool = True
    ) -> List[SongEntity]:
        """
        Busca canciones. Primero en la BD local, luego opcionalmente en YouTube.

        Args:
            query: Texto de búsqueda
            limit: Límite de resultados
            include_youtube: Si debe buscar en YouTube si no hay suficientes resultados

        Returns:
            Lista de canciones encontradas
        """
        try:
            # Buscar en la base de datos local
            self.logger.debug(f"Searching songs locally for: '{query}'")
            local_songs = await self.song_repository.search(query, limit)

            if len(local_songs) >= limit or not include_youtube:
                self.logger.info(
                    f"Found {len(local_songs)} songs locally for query: '{query}'"
                )
                return local_songs

            # Buscar en YouTube para completar los resultados
            self.logger.info(f"Searching YouTube for additional results: '{query}'")
            from common.types.media_types import SearchOptions

            options = SearchOptions(max_results=limit - len(local_songs))
            youtube_tracks = await self.music_service.search_and_process_audio(
                query, options
            )

            # Guardar nuevas canciones encontradas
            for track in youtube_tracks:
                existing_song = await self.song_repository.get_by_source(
                    "youtube", track.video_id
                )

                if not existing_song:
                    from .save_track_as_song_use_case import SaveTrackAsSongUseCase

                    save_track_use_case = SaveTrackAsSongUseCase(self.song_repository)
                    new_song = await save_track_use_case.execute(track)
                    if new_song:
                        local_songs.append(new_song)

            self.logger.info(
                f"Total songs found for query '{query}': {len(local_songs[:limit])}"
            )
            return local_songs[:limit]

        except Exception as e:
            self.logger.error(f"Error searching songs with query '{query}': {str(e)}")
            # Return existing local results if any, otherwise empty list
            try:
                return await self.song_repository.search(query, limit)
            except Exception:
                return []
