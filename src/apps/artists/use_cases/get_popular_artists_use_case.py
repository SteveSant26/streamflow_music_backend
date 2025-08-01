from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetPopularArtistsUseCase(BaseUseCase[None, List[ArtistEntity]]):
    """Caso de uso para obtener artistas populares"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, limit: int = 10) -> List[ArtistEntity]:
        """
        Obtiene artistas populares ordenados por seguidores

        Args:
            limit: Límite de resultados

        Returns:
            Lista de artistas populares
        """
        self.logger.info(f"Getting popular artists with limit: {limit}")
        return self.repository.get_popular_artists(limit)
