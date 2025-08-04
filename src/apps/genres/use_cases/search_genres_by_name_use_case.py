"""
Caso de uso para buscar géneros por nombre.
"""

from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import SearchGenresByNameRequestDTO
from ..domain.entities import GenreEntity
from ..domain.repository import IGenreRepository


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
