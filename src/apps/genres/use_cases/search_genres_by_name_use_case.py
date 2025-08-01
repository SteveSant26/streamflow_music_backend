from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import GenreEntity
from ..domain.repository import IGenreRepository


class SearchGenresByNameUseCase(BaseUseCase[str, List[GenreEntity]]):
    """Caso de uso para buscar géneros por nombre"""

    def __init__(self, repository: IGenreRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, name: str, limit: int = 10) -> List[GenreEntity]:
        """
        Busca géneros por nombre

        Args:
            name: Nombre del género a buscar
            limit: Límite de resultados

        Returns:
            Lista de géneros que coinciden con el nombre
        """
        self.logger.debug(f"Searching genres by name: {name} with limit: {limit}")
        return self.repository.search_by_name(name, limit)
