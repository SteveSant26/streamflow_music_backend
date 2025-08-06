from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import PlaylistEntity
from ..domain.exceptions import PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class GetUserPlaylistsUseCase(BaseUseCase[str, List[PlaylistEntity]]):
    """Caso de uso para obtener todas las playlists de un usuario"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, user_id: str) -> List[PlaylistEntity]:
        """
        Obtiene todas las playlists de un usuario

        Args:
            user_id: ID del usuario

        Returns:
            Lista de playlists del usuario

        Raises:
            PlaylistValidationException: Si el user_id es inválido
        """
        try:
            if not user_id:
                raise PlaylistValidationException("El ID del usuario es requerido")

            self.logger.debug(f"Getting playlists for user: {user_id}")
            return await self.repository.get_by_user_id(user_id)

        except Exception as e:
            self.logger.error(f"Error getting user playlists: {str(e)}")
            raise
