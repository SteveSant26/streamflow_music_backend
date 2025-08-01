from typing import Optional

from apps.songs.domain.exceptions import SongPlayCountException
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository


class IncrementPlayCountUseCase(BaseUseCase[str, Optional[SongEntity]]):
    """Caso de uso para incrementar el contador de reproducciones de una canción"""

    def __init__(self, repository: ISongRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)  # Operación de actualización simple
    async def execute(self, song_id: str) -> Optional[SongEntity]:
        """
        Incrementa el contador de reproducciones de una canción

        Args:
            song_id: ID de la canción

        Returns:
            Entidad de canción actualizada o None si falla

        Raises:
            SongPlayCountException: Si hay error al incrementar el contador
        """
        try:
            self.logger.debug(f"Incrementing play count for song: {song_id}")

            success = await self.repository.increment_play_count(song_id)
            if success:
                song = await self.repository.get_by_id(song_id)
                self.logger.info(
                    f"Successfully incremented play count for song: {song_id}"
                )
                return song
            else:
                self.logger.warning(
                    f"Failed to increment play count for song: {song_id}"
                )
                return None

        except Exception as e:
            self.logger.error(
                f"Error incrementing play count for song {song_id}: {str(e)}"
            )
            raise SongPlayCountException(
                f"Error al incrementar contador de reproducciones: {str(e)}"
            )
