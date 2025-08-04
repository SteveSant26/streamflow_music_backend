from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetTopArtistsByFollowersUseCase(BaseUseCase[None, List[ArtistEntity]]):
    """Caso de uso para obtener artistas con más seguidores"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, limit: int = 10) -> List[ArtistEntity]:
        """
        Obtiene artistas ordenados por número de seguidores

        Args:
            limit: Límite de resultados

        Returns:
            Lista de artistas con más seguidores
        """
        self.logger.debug(f"Getting top artists by followers with limit: {limit}")
        all_artists = await self.repository.get_all()

        # Ordenar por número de seguidores (descendente)
        sorted_artists = sorted(
            all_artists, key=lambda x: x.followers_count, reverse=True
        )

        top_artists = sorted_artists[:limit]
        self.logger.info(f"Found {len(top_artists)} top artists by followers")
        return top_artists
