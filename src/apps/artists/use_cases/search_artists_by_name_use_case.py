from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import SearchArtistsByNameRequestDTO
from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class SearchArtistsByNameUseCase(
    BaseUseCase[SearchArtistsByNameRequestDTO, List[ArtistEntity]]
):
    """Caso de uso para buscar artistas por nombre"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(
        self, request_dto: SearchArtistsByNameRequestDTO
    ) -> List[ArtistEntity]:
        """
        Busca artistas por nombre

        Args:
            request_dto: DTO con name y limit

        Returns:
            Lista de artistas encontrados
        """
        self.logger.info(f"Searching artists by name: {request_dto.name}")
        return await self.repository.search_by_name(request_dto.name, request_dto.limit)
