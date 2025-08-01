from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import GenreEntity
from ..domain.repository import IGenreRepository


class GetRecentGenresUseCase(BaseUseCase[None, List[GenreEntity]]):
    """Caso de uso para obtener géneros recientes"""

    def __init__(self, repository: IGenreRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, limit: int = 10) -> List[GenreEntity]:
        """
        Obtiene géneros recientes

        Args:
            limit: Límite de resultados

        Returns:
            Lista de géneros recientes
        """
        self.logger.debug(f"Getting recent genres with limit: {limit}")
        return self.repository.get_recent_genres(limit)
