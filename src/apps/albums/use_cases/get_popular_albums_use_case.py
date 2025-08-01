from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class GetPopularAlbumsUseCase(BaseUseCase[None, List[AlbumEntity]]):
    """Caso de uso para obtener álbumes populares"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, limit: int = 10) -> List[AlbumEntity]:
        """
        Obtiene álbumes populares

        Args:
            limit: Límite de resultados

        Returns:
            Lista de álbumes populares
        """
        self.logger.debug(f"Getting popular albums with limit: {limit}")
        return self.repository.get_popular_albums(limit)
