from abc import abstractmethod
from typing import Any, List, Optional

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

    @abstractmethod
    def find_or_create_by_title_and_artist(
        self,
        title: str,
        artist_id: str,
        artist_name: str,
        cover_image_url: Optional[str] = None,
    ) -> AlbumEntity:
        """Busca un álbum por título y artista, si no existe lo crea"""

    @abstractmethod
    async def get_by_source(
        self, source_type: str, source_id: str
    ) -> Optional[AlbumEntity]:
        """Busca un álbum por fuente externa"""
