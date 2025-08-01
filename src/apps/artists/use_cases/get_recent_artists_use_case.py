from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetRecentArtistsUseCase(BaseUseCase[None, List[ArtistEntity]]):
    """Caso de uso para obtener artistas agregados recientemente"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, limit: int = 10) -> List[ArtistEntity]:
        """
        Obtiene artistas agregados recientemente ordenados por fecha de creación

        Args:
            limit: Límite de resultados

        Returns:
            Lista de artistas recientes
        """
        self.logger.debug(f"Getting recent artists with limit: {limit}")
        all_artists = self.repository.get_all()

        # Ordenar por fecha de creación (más recientes primero)
        from datetime import datetime

        sorted_artists = sorted(
            all_artists,
            key=lambda x: x.created_at or x.updated_at or datetime.min,
            reverse=True,
        )

        recent_artists = sorted_artists[:limit]
        self.logger.info(f"Found {len(recent_artists)} recent artists")
        return recent_artists
