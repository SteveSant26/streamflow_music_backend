from typing import List, Dict, Any
from ..domain.repository.Imusic_repository import IMusicSearchRepository
from ..domain.entities import SearchResultEntity, PaginatedResultEntity
from ..domain.exceptions import InvalidSearchQueryException
from src.common.utils import get_logger

logger = get_logger(__name__)


class SearchUseCases:
    """Casos de uso para búsquedas"""
    
    def __init__(self, search_repository: IMusicSearchRepository):
        self.search_repository = search_repository
    
    def search_all(self, query: str, page: int = 1, page_size: int = 20) -> SearchResultEntity:
        """Búsqueda general en todas las categorías"""
        logger.info(f"Searching all categories for: {query}")
        return self.search_repository.search_all(query, page, page_size)
    
    def search_songs_paginated(self, query: str, page: int = 1, page_size: int = 20) -> PaginatedResultEntity:
        """Búsqueda paginada de canciones"""
        logger.info(f"Paginated search for songs: {query}")
        return self.search_repository.search_songs_paginated(query, page, page_size)
    
    def search_artists_paginated(self, query: str, page: int = 1, page_size: int = 20) -> PaginatedResultEntity:
        """Búsqueda paginada de artistas"""
        logger.info(f"Paginated search for artists: {query}")
        return self.search_repository.search_artists_paginated(query, page, page_size)
    
    def search_albums_paginated(self, query: str, page: int = 1, page_size: int = 20) -> PaginatedResultEntity:
        """Búsqueda paginada de álbumes"""
        logger.info(f"Paginated search for albums: {query}")
        return self.search_repository.search_albums_paginated(query, page, page_size)
    
    def search_by_filters(self, filters: Dict[str, Any], page: int = 1, page_size: int = 20) -> PaginatedResultEntity:
        """Búsqueda con filtros específicos"""
        logger.info(f"Search with filters: {filters}")
        return self.search_repository.search_by_filters(filters, page, page_size)


class SearchMusic:
    """Caso de uso para búsqueda general en el catálogo"""
    
    def __init__(self, search_repository: IMusicSearchRepository):
        self.search_repository = search_repository
    
    def execute(self, query: str, limit: int = 50) -> SearchResultEntity:
        """
        Busca en canciones, artistas y álbumes
        
        Args:
            query: Término de búsqueda
            limit: Número máximo de resultados por tipo
            
        Returns:
            SearchResultEntity: Resultados de búsqueda agrupados
            
        Raises:
            InvalidSearchQueryException: Si la consulta es inválida
        """
        logger.info(f"Searching music catalog with query: {query}")
        
        # Validar consulta
        if not query or len(query.strip()) < 2:
            raise InvalidSearchQueryException(query)
        
        # Limpiar consulta
        clean_query = query.strip()
        
        # Realizar búsqueda
        results = self.search_repository.search_all(clean_query, limit)
        
        logger.info(f"Search completed. Found {results.total_results} total results")
        logger.info(f"Songs: {len(results.songs)}, Artists: {len(results.artists)}, Albums: {len(results.albums)}")
        
        return results


class GetPaginatedSongs:
    """Caso de uso para obtener canciones paginadas"""
    
    def __init__(self, search_repository: IMusicSearchRepository):
        self.search_repository = search_repository
    
    def execute(self, page: int = 1, page_size: int = 20, filters: dict = None) -> PaginatedResultEntity:
        """
        Obtiene canciones paginadas con filtros opcionales
        
        Args:
            page: Número de página (empezando en 1)
            page_size: Tamaño de página
            filters: Filtros opcionales (genre, artist, etc.)
            
        Returns:
            PaginatedResultEntity: Resultados paginados
        """
        logger.info(f"Getting paginated songs - Page: {page}, Size: {page_size}")
        
        # Validar parámetros
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        
        results = self.search_repository.get_paginated_songs(page, page_size, filters or {})
        
        logger.info(f"Retrieved {len(results.items)} songs (page {page} of {results.total_pages})")
        
        return results


class GetPaginatedArtists:
    """Caso de uso para obtener artistas paginados"""
    
    def __init__(self, search_repository: IMusicSearchRepository):
        self.search_repository = search_repository
    
    def execute(self, page: int = 1, page_size: int = 20, filters: dict = None) -> PaginatedResultEntity:
        """
        Obtiene artistas paginados con filtros opcionales
        
        Args:
            page: Número de página (empezando en 1)
            page_size: Tamaño de página
            filters: Filtros opcionales (country, genre, etc.)
            
        Returns:
            PaginatedResultEntity: Resultados paginados
        """
        logger.info(f"Getting paginated artists - Page: {page}, Size: {page_size}")
        
        # Validar parámetros
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        
        results = self.search_repository.get_paginated_artists(page, page_size, filters or {})
        
        logger.info(f"Retrieved {len(results.items)} artists (page {page} of {results.total_pages})")
        
        return results


class GetPaginatedAlbums:
    """Caso de uso para obtener álbumes paginados"""
    
    def __init__(self, search_repository: IMusicSearchRepository):
        self.search_repository = search_repository
    
    def execute(self, page: int = 1, page_size: int = 20, filters: dict = None) -> PaginatedResultEntity:
        """
        Obtiene álbumes paginados con filtros opcionales
        
        Args:
            page: Número de página (empezando en 1)
            page_size: Tamaño de página
            filters: Filtros opcionales (genre, artist, year, etc.)
            
        Returns:
            PaginatedResultEntity: Resultados paginados
        """
        logger.info(f"Getting paginated albums - Page: {page}, Size: {page_size}")
        
        # Validar parámetros
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        
        results = self.search_repository.get_paginated_albums(page, page_size, filters or {})
        
        logger.info(f"Retrieved {len(results.items)} albums (page {page} of {results.total_pages})")
        
        return results
