from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class GetAlbumsByReleaseYearUseCase(BaseUseCase[int, List[AlbumEntity]]):
    """Caso de uso para obtener álbumes por año de lanzamiento"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, year: int, limit: int = 10) -> List[AlbumEntity]:
        """
        Obtiene álbumes por año de lanzamiento

        Args:
            year: Año de lanzamiento
            limit: Límite de resultados

        Returns:
            Lista de álbumes del año especificado
        """
        self.logger.debug(f"Getting albums by release year: {year} with limit: {limit}")
        return self.repository.find_by_release_year(year, limit)
