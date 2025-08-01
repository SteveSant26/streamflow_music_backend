from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetArtistsByCountryUseCase(BaseUseCase[str, List[ArtistEntity]]):
    """Caso de uso para obtener artistas por país"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)
    async def execute(self, country: str, limit: int = 10) -> List[ArtistEntity]:
        """
        Obtiene artistas por país

        Args:
            country: País del artista
            limit: Límite de resultados

        Returns:
            Lista de artistas del país especificado
        """
        self.logger.info(f"Getting artists by country: {country}")
        return await self.repository.find_by_country(country, limit)
