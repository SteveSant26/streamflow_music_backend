from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class SearchArtistsByNameUseCase(BaseUseCase[str, List[ArtistEntity]]):
    """Caso de uso para buscar artistas por nombre"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, name: str, limit: int = 10) -> List[ArtistEntity]:
        """
        Busca artistas por nombre

        Args:
            name: Nombre del artista a buscar
            limit: Límite de resultados

        Returns:
            Lista de artistas encontrados
        """
        self.logger.info(f"Searching artists by name: {name}")
        return self.repository.search_by_name(name, limit)
