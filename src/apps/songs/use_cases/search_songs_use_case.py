from typing import List

<<<<<<< HEAD
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance
from src.common.factories.unified_music_service_factory import get_music_service
=======
from common.factories.unified_music_service_factory import get_music_service
from common.interfaces.ibase_use_case import BaseUseCase
from common.types.media_types import SearchOptions
from common.utils.logging_decorators import log_execution, log_performance
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

from ..api.dtos import SongSearchRequestDTO
from ..domain.entities import SongEntity
from ..domain.repository import ISongRepository
<<<<<<< HEAD
=======
from .save_track_as_song_use_case import SaveTrackAsSongUseCase
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33


class SearchSongsUseCase(BaseUseCase[SongSearchRequestDTO, List[SongEntity]]):
    """Caso de uso para buscar canciones"""

    def __init__(self, song_repository: ISongRepository, music_service=None):
        super().__init__()
        self.song_repository = song_repository
        self.music_service = get_music_service()

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)  # Búsqueda puede incluir consultas externas
    async def execute(self, request_dto: SongSearchRequestDTO) -> List[SongEntity]:
        """
        Busca canciones. Primero en la BD local, luego opcionalmente en YouTube.

        Args:
            request_dto: DTO con query, limit e include_youtube

        Returns:
            Lista de canciones encontradas
        """
        try:
            # Buscar en la base de datos local
            self.logger.debug(f"Searching songs locally for: '{request_dto.query}'")
            local_songs = await self.song_repository.search(
                request_dto.query, request_dto.limit
            )

            if len(local_songs) >= request_dto.limit or not request_dto.include_youtube:
                self.logger.info(
                    f"Found {len(local_songs)} songs locally for query: '{request_dto.query}'"
                )
                return local_songs

            # Buscar en YouTube para completar los resultados
            self.logger.info(
                f"Searching YouTube for additional results: '{request_dto.query}'"
            )
<<<<<<< HEAD
            from common.types.media_types import SearchOptions
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

            options = SearchOptions(max_results=request_dto.limit - len(local_songs))
            youtube_tracks = await self.music_service.search_and_process_audio(
                request_dto.query, options
            )

            # Guardar nuevas canciones encontradas
            for track in youtube_tracks:
                existing_song = await self.song_repository.get_by_source(
                    "youtube", track.video_id
                )

                if not existing_song:
<<<<<<< HEAD
                    from .save_track_as_song_use_case import SaveTrackAsSongUseCase

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
                    save_track_use_case = SaveTrackAsSongUseCase(self.song_repository)
                    new_song = await save_track_use_case.execute(track)
                    if new_song:
                        local_songs.append(new_song)

            self.logger.info(
                f"Total songs found for query '{request_dto.query}': {len(local_songs[:request_dto.limit])}"
            )
            return local_songs[: request_dto.limit]

        except Exception as e:
            self.logger.error(
                f"Error searching songs with query '{request_dto.query}': {str(e)}"
            )
<<<<<<< HEAD
            # Return existing local results if any, otherwise empty list
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            try:
                return await self.song_repository.search(
                    request_dto.query, request_dto.limit
                )
            except Exception:
                return []
