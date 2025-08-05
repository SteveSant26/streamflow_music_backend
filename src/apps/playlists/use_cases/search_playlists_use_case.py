from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import SearchPlaylistsRequestDTO
from ..domain.entities import PlaylistEntity
from ..domain.exceptions import PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class SearchPlaylistsUseCase(
    BaseUseCase[SearchPlaylistsRequestDTO, List[PlaylistEntity]]
):
    """Caso de uso para buscar playlists por nombre o descripción"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(
        self, request_dto: SearchPlaylistsRequestDTO
    ) -> List[PlaylistEntity]:
        """
        Busca playlists por nombre o descripción

        Args:
            request_dto: DTO con datos de búsqueda

        Returns:
            Lista de playlists encontradas

        Raises:
            PlaylistValidationException: Si los datos de búsqueda son inválidos
        """
        try:
            if not request_dto.query or not request_dto.query.strip():
                raise PlaylistValidationException("El término de búsqueda es requerido")

            if request_dto.limit <= 0 or request_dto.limit > 100:
                raise PlaylistValidationException("El límite debe estar entre 1 y 100")

            self.logger.info(f"Searching playlists with query: '{request_dto.query}'")
            return await self.repository.search_playlists(
                request_dto.query.strip(), request_dto.user_id, request_dto.limit
            )

        except Exception as e:
            self.logger.error(f"Error searching playlists: {str(e)}")
            raise
