from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import GetAlbumsByArtistRequestDTO
from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class GetAlbumsByArtistUseCase(
    BaseUseCase[GetAlbumsByArtistRequestDTO, List[AlbumEntity]]
):
    """Caso de uso para obtener álbumes por artista"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)
    async def execute(
        self, request_dto: GetAlbumsByArtistRequestDTO
    ) -> List[AlbumEntity]:
        """
        Obtiene álbumes por artista

        Args:
            request_dto: DTO con artist_id y limit

        Returns:
            Lista de álbumes del artista
        """
        self.logger.debug(f"Getting albums by artist: {request_dto.artist_id}")
        return await self.repository.find_by_artist_id(
            request_dto.artist_id, request_dto.limit
        )
