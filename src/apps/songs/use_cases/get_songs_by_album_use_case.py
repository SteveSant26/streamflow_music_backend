from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import SongEntity
from ..domain.repository import ISongRepository


class GetSongsByAlbumUseCase(BaseUseCase[str, List[SongEntity]]):
    """Caso de uso para obtener canciones por álbum"""

    def __init__(self, repository: ISongRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(
        threshold_seconds=2.0
    )  # Búsqueda por álbum puede devolver varios resultados
    async def execute(self, album_title: str, limit: int = 20) -> List[SongEntity]:
        """
        Obtiene canciones de un álbum específico

        Args:
            album_title: Título del álbum
            limit: Límite de resultados

        Returns:
            Lista de canciones del álbum
        """
        self.logger.debug(f"Getting songs by album: {album_title}")
        songs = await self.repository.get_by_album(album_title, limit)

        self.logger.info(f"Found {len(songs)} songs for album: {album_title}")
        return songs
