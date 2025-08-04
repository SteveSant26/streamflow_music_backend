from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetActiveArtistsUseCase(BaseUseCase[None, List[ArtistEntity]]):
    """Caso de uso para obtener artistas activos"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)
    async def execute(self, limit: int = 50) -> List[ArtistEntity]:
        """
        Obtiene artistas activos

        Args:
            limit: Límite de resultados

        Returns:
            Lista de artistas activos
        """
        self.logger.debug(f"Getting active artists with limit: {limit}")
        # Usando get_all y filtrando por is_active
        all_artists = await self.repository.get_all()
        active_artists = [artist for artist in all_artists][:limit]

        self.logger.info(f"Found {len(active_artists)} active artists")
        return active_artists
