from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import GetArtistsByCountryRequestDTO
from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetArtistsByCountryUseCase(
    BaseUseCase[GetArtistsByCountryRequestDTO, List[ArtistEntity]]
):
    """Caso de uso para obtener artistas por país"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)
    async def execute(
        self, request_dto: GetArtistsByCountryRequestDTO
    ) -> List[ArtistEntity]:
        """
        Obtiene artistas por país

        Args:
            request_dto: DTO con country y limit

        Returns:
            Lista de artistas del país especificado
        """
        self.logger.info(f"Getting artists by country: {request_dto.country}")
        return await self.repository.find_by_country(
            request_dto.country, request_dto.limit
        )
