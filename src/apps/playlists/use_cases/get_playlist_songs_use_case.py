from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import PlaylistSongEntity
from ..domain.exceptions import PlaylistNotFoundException, PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class GetPlaylistSongsUseCase(BaseUseCase[str, List[PlaylistSongEntity]]):
    """Caso de uso para obtener todas las canciones de una playlist"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, playlist_id: str) -> List[PlaylistSongEntity]:
        """
        Obtiene todas las canciones de una playlist

        Args:
            playlist_id: ID de la playlist

        Returns:
            Lista de canciones de la playlist ordenadas por posición

        Raises:
            PlaylistValidationException: Si el ID es inválido
            PlaylistNotFoundException: Si la playlist no existe
        """
        try:
            if not playlist_id:
                raise PlaylistValidationException("El ID de la playlist es requerido")

            # Verificar que la playlist existe
            playlist = await self.repository.get_by_id(playlist_id)
            if not playlist:
                raise PlaylistNotFoundException(
                    f"Playlist con ID {playlist_id} no encontrada"
                )

            self.logger.debug(f"Getting songs for playlist {playlist_id}")
            return await self.repository.get_playlist_songs(playlist_id)

        except Exception as e:
            self.logger.error(f"Error getting playlist songs: {str(e)}")
            raise
