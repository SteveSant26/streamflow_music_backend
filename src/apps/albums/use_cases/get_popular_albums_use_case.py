from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import GetPopularAlbumsRequestDTO
from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class GetPopularAlbumsUseCase(
    BaseUseCase[GetPopularAlbumsRequestDTO, List[AlbumEntity]]
):
    """Caso de uso para obtener álbumes populares"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(
        self, request_dto: GetPopularAlbumsRequestDTO
    ) -> List[AlbumEntity]:
        """
        Obtiene álbumes populares

        Args:
            request_dto: DTO con limit

        Returns:
            Lista de álbumes populares
        """
        self.logger.debug(f"Getting popular albums with limit: {request_dto.limit}")
        return await self.repository.get_popular_albums(request_dto.limit)
