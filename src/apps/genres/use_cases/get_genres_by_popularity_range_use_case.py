from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import GenreEntity
from ..domain.repository import IGenreRepository


class GetGenresByPopularityRangeUseCase(BaseUseCase[tuple, List[GenreEntity]]):
    """Caso de uso para obtener géneros por rango de popularidad"""

    def __init__(self, repository: IGenreRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, min_score: int, max_score: int) -> List[GenreEntity]:
        """
        Obtiene géneros por rango de popularidad

        Args:
            min_score: Puntuación mínima de popularidad
            max_score: Puntuación máxima de popularidad

        Returns:
            Lista de géneros en el rango de popularidad especificado
        """
        self.logger.debug(
            f"Getting genres by popularity range: {min_score}-{max_score}"
        )
        return await self.repository.get_genres_by_popularity_range(
            min_score, max_score
        )
