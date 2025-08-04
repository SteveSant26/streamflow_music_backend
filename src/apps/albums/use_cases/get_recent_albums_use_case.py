from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class GetRecentAlbumsUseCase(BaseUseCase[None, List[AlbumEntity]]):
    """Caso de uso para obtener álbumes recientes"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, limit: int = 10) -> List[AlbumEntity]:
        """
        Obtiene álbumes recientes

        Args:
            limit: Límite de resultados

        Returns:
            Lista de álbumes recientes
        """
        self.logger.debug(f"Getting recent albums with limit: {limit}")
        return await self.repository.get_recent_albums(limit)
