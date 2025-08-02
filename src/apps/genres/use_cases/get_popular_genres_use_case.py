"""
Caso de uso para obtener géneros populares.
"""

from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import GetPopularGenresRequestDTO
from ..domain.entities import GenreEntity
from ..domain.repository.Igenre_repository import IGenreRepository


class GetPopularGenresUseCase(
    BaseUseCase[GetPopularGenresRequestDTO, List[GenreEntity]]
):
    """Caso de uso para obtener géneros populares"""

    def __init__(self, repository: IGenreRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(
        self, request_dto: GetPopularGenresRequestDTO
    ) -> List[GenreEntity]:
        """
        Obtiene géneros populares ordenados por puntuación de popularidad.

        Args:
            request_dto: DTO con el límite de resultados

        Returns:
            Lista de géneros populares
        """
        self.logger.info(f"Getting popular genres with limit: {request_dto.limit}")
        return await self.repository.get_popular_genres(request_dto.limit)
