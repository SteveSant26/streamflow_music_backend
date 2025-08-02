"""
Casos de uso para operaciones básicas de géneros.
"""

from typing import Any, List

from common.interfaces.ibase_use_case import (
    BaseGetAllUseCase,
    BaseGetByIdUseCase,
    BaseUseCase,
)
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import GetPopularGenresRequestDTO, SearchGenresByNameRequestDTO
from ..domain.entities import GenreEntity
from ..domain.exceptions import GenreNotFoundException
from ..domain.repository import IGenreRepository


class GetAllGenresUseCase(BaseGetAllUseCase[GenreEntity, Any]):
    """Caso de uso para obtener todos los géneros"""

    def __init__(self, repository: IGenreRepository):
        super().__init__(repository)


class GetGenreUseCase(BaseGetByIdUseCase[GenreEntity, Any]):
    """Caso de uso para obtener un género específico"""

    def __init__(self, repository: IGenreRepository):
        super().__init__(repository)

    def _get_not_found_exception(self, entity_id: str) -> Exception:
        return GenreNotFoundException(entity_id)


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


class SearchGenresByNameUseCase(
    BaseUseCase[SearchGenresByNameRequestDTO, List[GenreEntity]]
):
    """Caso de uso para buscar géneros por nombre"""

    def __init__(self, repository: IGenreRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(
        self, request_dto: SearchGenresByNameRequestDTO
    ) -> List[GenreEntity]:
        """
        Busca géneros por nombre.

        Args:
            request_dto: DTO con el término de búsqueda y límite

        Returns:
            Lista de géneros que coinciden con la búsqueda
        """
        self.logger.info(
            f"Searching genres by name: '{request_dto.query}' with limit: {request_dto.limit}"
        )
        return await self.repository.search_by_name(
            request_dto.query, request_dto.limit
        )
