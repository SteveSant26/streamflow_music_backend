from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository


class GetSongsByArtistUseCase(BaseUseCase[str, List[SongEntity]]):
    """Caso de uso para obtener canciones por artista"""

    def __init__(self, repository: ISongRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    async def execute(self, artist_name: str, limit: int = 20) -> List[SongEntity]:
        """
        Obtiene canciones de un artista específico

        Args:
            artist_name: Nombre del artista
            limit: Límite de resultados

        Returns:
            Lista de canciones del artista
        """
        self.logger.debug(f"Getting songs by artist: {artist_name}")
        songs = await self.repository.get_by_artist(artist_name, limit)

        self.logger.info(f"Found {len(songs)} songs for artist: {artist_name}")
        return songs
