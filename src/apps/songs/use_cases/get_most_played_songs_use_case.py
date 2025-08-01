from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository


class GetMostPlayedSongsUseCase(BaseUseCase[None, List[SongEntity]]):
    """Caso de uso para obtener las canciones más reproducidas"""

    def __init__(self, repository: ISongRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    async def execute(self, limit: int = 10) -> List[SongEntity]:
        """
        Obtiene las canciones más reproducidas en la aplicación

        Args:
            limit: Límite de resultados

        Returns:
            Lista de canciones más reproducidas
        """
        self.logger.debug(f"Getting most played songs with limit: {limit}")
        songs = await self.repository.get_most_played(limit)

        self.logger.info(f"Found {len(songs)} most played songs")
        return songs
