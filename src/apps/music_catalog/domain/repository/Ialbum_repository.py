from abc import abstractmethod
from typing import TYPE_CHECKING, List

from apps.music_catalog.infrastructure.models.album import AlbumModel
from common.interfaces import IBaseRepository

from ..entities import AlbumEntity

if TYPE_CHECKING:
    pass


class IAlbumRepository(IBaseRepository[AlbumEntity, AlbumModel]):
    """Interface para el repositorio de álbumes"""

    @abstractmethod
    def get_by_artist(self, artist_id: str) -> List[AlbumEntity]:
        """Obtiene álbumes por artista"""

    @abstractmethod
    def get_by_genre(self, genre_id: str) -> List[AlbumEntity]:
        """Obtiene álbumes por género"""

    @abstractmethod
    def search_by_title(self, title: str) -> List[AlbumEntity]:
        """Busca álbumes por título"""

    @abstractmethod
    def get_recent_releases(self, limit: int = 20) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""
