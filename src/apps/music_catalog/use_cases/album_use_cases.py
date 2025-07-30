from typing import List, Optional
from datetime import date
from ..domain.repository.Imusic_repository import IAlbumRepository
from ..domain.entities import AlbumEntity
from ..domain.exceptions import AlbumNotFoundException
from src.common.utils import get_logger

logger = get_logger(__name__)


class AlbumUseCases:
    """Casos de uso para álbumes"""
    
    def __init__(self, album_repository: IAlbumRepository):
        self.album_repository = album_repository
    
    def get_album_by_id(self, album_id: str) -> Optional[AlbumEntity]:
        """Obtiene un álbum por ID"""
        logger.info(f"Getting album with ID: {album_id}")
        return self.album_repository.get_by_id(album_id)
    
    def get_all_albums(self) -> List[AlbumEntity]:
        """Obtiene todos los álbumes"""
        logger.info("Getting all albums")
        return self.album_repository.get_all()
    
    def get_albums_by_artist(self, artist_id: str) -> List[AlbumEntity]:
        """Obtiene álbumes de un artista"""
        logger.info(f"Getting albums by artist: {artist_id}")
        return self.album_repository.get_by_artist(artist_id)
    
    def search_albums_by_title(self, title: str) -> List[AlbumEntity]:
        """Busca álbumes por título"""
        logger.info(f"Searching albums by title: {title}")
        return self.album_repository.search_by_title(title)
    
    def get_popular_albums(self, limit: int = 50) -> List[AlbumEntity]:
        """Obtiene álbumes populares"""
        logger.info(f"Getting popular albums with limit: {limit}")
        return self.album_repository.get_popular_albums(limit)
