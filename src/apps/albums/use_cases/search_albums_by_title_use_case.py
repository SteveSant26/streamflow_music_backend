from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class SearchAlbumsByTitleUseCase(BaseUseCase[str, List[AlbumEntity]]):
    """Caso de uso para buscar álbumes por título"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, title: str, limit: int = 10) -> List[AlbumEntity]:
        """
        Busca álbumes por título

        Args:
            title: Título a buscar
            limit: Límite de resultados

        Returns:
            Lista de álbumes encontrados
        """
        self.logger.debug(f"Searching albums by title: {title}")
        return self.repository.search_by_title(title, limit)
