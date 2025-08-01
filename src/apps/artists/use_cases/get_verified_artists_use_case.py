from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import GetVerifiedArtistsRequestDTO
from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetVerifiedArtistsUseCase(
    BaseUseCase[GetVerifiedArtistsRequestDTO, List[ArtistEntity]]
):
    """Caso de uso para obtener artistas verificados"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(
        threshold_seconds=1.0
    )  # Consulta simple con filtro de verificación
    async def execute(
        self, request_dto: GetVerifiedArtistsRequestDTO
    ) -> List[ArtistEntity]:
        """
        Obtiene artistas verificados

        Args:
            request_dto: DTO con limit

        Returns:
            Lista de artistas verificados
        """
        self.logger.info(f"Getting verified artists with limit: {request_dto.limit}")
        return await self.repository.get_verified_artists(request_dto.limit)
