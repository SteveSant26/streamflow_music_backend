from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import SearchAlbumsByTitleRequestDTO
from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class SearchAlbumsByTitleUseCase(
    BaseUseCase[SearchAlbumsByTitleRequestDTO, List[AlbumEntity]]
):
    """Caso de uso para buscar álbumes por título"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(
        self, request_dto: SearchAlbumsByTitleRequestDTO
    ) -> List[AlbumEntity]:
        """
        Busca álbumes por título

        Args:
            request_dto: DTO con title y limit

        Returns:
            Lista de álbumes encontrados
        """
        self.logger.debug(f"Searching albums by title: {request_dto.title}")
        return await self.repository.search_by_title(
            request_dto.title, request_dto.limit
        )
