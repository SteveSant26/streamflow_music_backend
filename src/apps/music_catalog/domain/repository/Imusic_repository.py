from abc import ABC, abstractmethod
from typing import Optional, List
from common.interfaces.IBaseRepository import IBaseRepository

from ..entities import SongEntity, ArtistEntity, AlbumEntity, GenreEntity, SearchResultEntity, PaginatedResultEntity


class ISongRepository(IBaseRepository[SongEntity, any]):
    """Interface para el repositorio de canciones"""

    @abstractmethod
    def get_by_artist(self, artist_id: str) -> List[SongEntity]:
        """Obtiene canciones por artista"""
        pass

    @abstractmethod
    def get_by_album(self, album_id: str) -> List[SongEntity]:
        """Obtiene canciones por álbum"""
        pass

    @abstractmethod
    def get_by_genre(self, genre_id: str) -> List[SongEntity]:
        """Obtiene canciones por género"""
        pass

    @abstractmethod
    def search_by_title(self, title: str) -> List[SongEntity]:
        """Busca canciones por título"""
        pass

    @abstractmethod
    def get_popular_songs(self, limit: int = 50) -> List[SongEntity]:
        """Obtiene canciones populares ordenadas por play_count"""
        pass

    @abstractmethod
    def increment_play_count(self, song_id: str) -> bool:
        """Incrementa el contador de reproducciones"""
        pass


class IArtistRepository(IBaseRepository[ArtistEntity, any]):
    """Interface para el repositorio de artistas"""

    @abstractmethod
    def search_by_name(self, name: str) -> List[ArtistEntity]:
        """Busca artistas por nombre"""
        pass

    @abstractmethod
    def get_by_country(self, country: str) -> List[ArtistEntity]:
        """Obtiene artistas por país"""
        pass

    @abstractmethod
    def get_popular_artists(self, limit: int = 50) -> List[ArtistEntity]:
        """Obtiene artistas populares"""
        pass


class IAlbumRepository(IBaseRepository[AlbumEntity, any]):
    """Interface para el repositorio de álbumes"""

    @abstractmethod
    def get_by_artist(self, artist_id: str) -> List[AlbumEntity]:
        """Obtiene álbumes por artista"""
        pass

    @abstractmethod
    def get_by_genre(self, genre_id: str) -> List[AlbumEntity]:
        """Obtiene álbumes por género"""
        pass

    @abstractmethod
    def search_by_title(self, title: str) -> List[AlbumEntity]:
        """Busca álbumes por título"""
        pass

    @abstractmethod
    def get_recent_releases(self, limit: int = 20) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""
        pass


class IGenreRepository(IBaseRepository[GenreEntity, any]):
    """Interface para el repositorio de géneros"""

    @abstractmethod
    def get_active_genres(self) -> List[GenreEntity]:
        """Obtiene géneros activos"""
        pass

    @abstractmethod
    def search_by_name(self, name: str) -> List[GenreEntity]:
        """Busca géneros por nombre"""
        pass


class IMusicSearchRepository(ABC):
    """Interface para búsqueda general en el catálogo"""

    @abstractmethod
    def search_all(self, query: str, limit: int = 50) -> SearchResultEntity:
        """Busca en canciones, artistas y álbumes"""
        pass

    @abstractmethod
    def get_paginated_songs(self, page: int, page_size: int, filters: dict = None) -> PaginatedResultEntity:
        """Obtiene canciones paginadas con filtros opcionales"""
        pass

    @abstractmethod
    def get_paginated_artists(self, page: int, page_size: int, filters: dict = None) -> PaginatedResultEntity:
        """Obtiene artistas paginados con filtros opcionales"""
        pass

    @abstractmethod
    def get_paginated_albums(self, page: int, page_size: int, filters: dict = None) -> PaginatedResultEntity:
        """Obtiene álbumes paginados con filtros opcionales"""
        pass
