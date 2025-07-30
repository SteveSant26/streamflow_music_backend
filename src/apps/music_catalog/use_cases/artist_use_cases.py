from typing import List, Optional
from ..domain.repository.Imusic_repository import IArtistRepository
from ..domain.entities import ArtistEntity
from ..domain.exceptions import ArtistNotFoundException
from src.common.utils import get_logger

logger = get_logger(__name__)


class ArtistUseCases:
    """Casos de uso para artistas"""
    
    def __init__(self, artist_repository: IArtistRepository):
        self.artist_repository = artist_repository
    
    def get_artist_by_id(self, artist_id: str) -> Optional[ArtistEntity]:
        """Obtiene un artista por ID"""
        logger.info(f"Getting artist with ID: {artist_id}")
        return self.artist_repository.get_by_id(artist_id)
    
    def get_all_artists(self) -> List[ArtistEntity]:
        """Obtiene todos los artistas"""
        logger.info("Getting all artists")
        return self.artist_repository.get_all()
    
    def search_artists_by_name(self, name: str) -> List[ArtistEntity]:
        """Busca artistas por nombre"""
        logger.info(f"Searching artists by name: {name}")
        return self.artist_repository.search_by_name(name)
    
    def get_popular_artists(self, limit: int = 50) -> List[ArtistEntity]:
        """Obtiene artistas populares"""
        logger.info(f"Getting popular artists with limit: {limit}")
        return self.artist_repository.get_popular_artists(limit)


class GetArtist:
    """Caso de uso para obtener un artista específico"""
    
    def __init__(self, artist_repository: IArtistRepository):
        self.artist_repository = artist_repository
    
    def execute(self, artist_id: str) -> ArtistEntity:
        """
        Obtiene un artista por ID
        
        Args:
            artist_id: ID del artista
            
        Returns:
            ArtistEntity: Artista encontrado
            
        Raises:
            ArtistNotFoundException: Si el artista no existe
        """
        logger.info(f"Getting artist with ID: {artist_id}")
        
        artist = self.artist_repository.get_by_id(artist_id)
        if not artist:
            raise ArtistNotFoundException(artist_id)
        
        logger.info(f"Artist retrieved: {artist.name}")
        return artist


class GetAllArtists:
    """Caso de uso para obtener todos los artistas"""
    
    def __init__(self, artist_repository: IArtistRepository):
        self.artist_repository = artist_repository
    
    def execute(self) -> List[ArtistEntity]:
        """
        Obtiene todos los artistas activos
        
        Returns:
            List[ArtistEntity]: Lista de artistas
        """
        logger.info("Getting all artists")
        
        artists = self.artist_repository.get_all()
        active_artists = [artist for artist in artists if artist.is_active]
        
        logger.info(f"Retrieved {len(active_artists)} active artists")
        return active_artists


class SearchArtists:
    """Caso de uso para buscar artistas por nombre"""
    
    def __init__(self, artist_repository: IArtistRepository):
        self.artist_repository = artist_repository
    
    def execute(self, query: str) -> List[ArtistEntity]:
        """
        Busca artistas por nombre
        
        Args:
            query: Término de búsqueda
            
        Returns:
            List[ArtistEntity]: Lista de artistas que coinciden con la búsqueda
        """
        logger.info(f"Searching artists with query: {query}")
        
        if not query or len(query.strip()) < 2:
            logger.warning("Search query too short")
            return []
        
        artists = self.artist_repository.search_by_name(query.strip())
        
        logger.info(f"Found {len(artists)} artists matching '{query}'")
        return artists


class GetArtistsByCountry:
    """Caso de uso para obtener artistas por país"""
    
    def __init__(self, artist_repository: IArtistRepository):
        self.artist_repository = artist_repository
    
    def execute(self, country: str) -> List[ArtistEntity]:
        """
        Obtiene artistas de un país específico
        
        Args:
            country: Nombre del país
            
        Returns:
            List[ArtistEntity]: Lista de artistas del país
        """
        logger.info(f"Getting artists from country: {country}")
        
        artists = self.artist_repository.get_by_country(country)
        
        logger.info(f"Found {len(artists)} artists from {country}")
        return artists


class GetPopularArtists:
    """Caso de uso para obtener artistas populares"""
    
    def __init__(self, artist_repository: IArtistRepository):
        self.artist_repository = artist_repository
    
    def execute(self, limit: int = 50) -> List[ArtistEntity]:
        """
        Obtiene los artistas más populares
        
        Args:
            limit: Número máximo de artistas a retornar
            
        Returns:
            List[ArtistEntity]: Lista de artistas populares
        """
        logger.info(f"Getting top {limit} popular artists")
        
        artists = self.artist_repository.get_popular_artists(limit)
        
        logger.info(f"Retrieved {len(artists)} popular artists")
        return artists
