from abc import abstractmethod
from typing import Any, List

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import AlbumEntity


class IAlbumRepository(IBaseRepository[AlbumEntity, Any]):
    """Interface del repositorio de álbumes"""

    @abstractmethod
    async def find_by_artist_id(
        self, artist_id: str, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por ID del artista"""

    @abstractmethod
    async def search_by_title(self, title: str, limit: int = 10) -> List[AlbumEntity]:
        """Busca álbumes por título"""

    @abstractmethod
    async def get_recent_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""

    @abstractmethod
    async def get_popular_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes populares"""

    @abstractmethod
    async def find_by_release_year(
        self, year: int, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por año de lanzamiento"""
