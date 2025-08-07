from abc import abstractmethod
from typing import Any, List, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import SongEntity


class ISongRepository(IBaseRepository[SongEntity, Any]):
    """Interface para el repositorio de canciones"""

    # Métodos específicos del dominio de canciones

    @abstractmethod
    async def save(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, song_entity: SongEntity
    ) -> Optional[SongEntity]:
        """Guarda una canción en la base de datos"""

    @abstractmethod
    async def get_by_source(
        self, source_type: str, source_id: str
    ) -> Optional[SongEntity]:
        """Obtiene una canción por fuente y ID de fuente"""

    @abstractmethod
    async def get_random(self, limit: int = 6) -> List[SongEntity]:
        """Obtiene canciones aleatorias"""

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> List[SongEntity]:
        """Busca canciones por título o artista"""

    @abstractmethod
    async def get_by_artist(
        self, artist_name: str, limit: int = 20
    ) -> List[SongEntity]:
        """Obtiene canciones por artista"""

    @abstractmethod
    async def get_by_album(self, album_title: str, limit: int = 20) -> List[SongEntity]:
        """Obtiene canciones por álbum"""

    @abstractmethod
    async def get_most_played(self, limit: int = 10) -> List[SongEntity]:
        """Obtiene las canciones más reproducidas"""

    @abstractmethod
    async def increment_play_count(self, song_id: str) -> bool:
        """Incrementa el contador de reproducciones"""

    @abstractmethod
    async def increment_favorite_count(self, song_id: str) -> bool:
        """Incrementa el contador de favoritos"""

    @abstractmethod
    async def increment_download_count(self, song_id: str) -> bool:
        """Incrementa el contador de descargas"""
