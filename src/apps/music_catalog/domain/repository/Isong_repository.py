from abc import abstractmethod
from typing import TYPE_CHECKING, List

from apps.music_catalog.infrastructure.models.song import SongModel
from common.interfaces import IBaseRepository

from ..entities import SongEntity

if TYPE_CHECKING:
    pass


class ISongRepository(IBaseRepository[SongEntity, SongModel]):
    """Interface para el repositorio de canciones"""

    @abstractmethod
    def get_by_artist(self, artist_id: str) -> List[SongEntity]:
        """Obtiene canciones por artista"""

    @abstractmethod
    def get_by_album(self, album_id: str) -> List[SongEntity]:
        """Obtiene canciones por álbum"""

    @abstractmethod
    def get_by_genre(self, genre_id: str) -> List[SongEntity]:
        """Obtiene canciones por género"""

    @abstractmethod
    def search_by_title(self, title: str) -> List[SongEntity]:
        """Busca canciones por título"""

    @abstractmethod
    def get_popular_songs(self, limit: int = 50) -> List[SongEntity]:
        """Obtiene canciones populares ordenadas por play_count"""

    @abstractmethod
    def increment_play_count(self, song_id: str) -> bool:
        """Incrementa el contador de reproducciones"""
