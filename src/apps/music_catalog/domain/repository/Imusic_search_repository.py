from abc import ABC, abstractmethod
from typing import Optional

from ..entities import PaginatedResultEntity, SearchResultEntity


class IMusicSearchRepository(ABC):
    """Interface para búsqueda general en el catálogo"""

    @abstractmethod
    def search_all(self, query: str, limit: int = 50) -> SearchResultEntity:
        """Busca en canciones, artistas y álbumes"""

    @abstractmethod
    def get_paginated_songs(
        self, page: int, page_size: int, filters: Optional[dict] = None
    ) -> PaginatedResultEntity:
        """Obtiene canciones paginadas con filtros opcionales"""

    @abstractmethod
    def get_paginated_artists(
        self, page: int, page_size: int, filters: Optional[dict] = None
    ) -> PaginatedResultEntity:
        """Obtiene artistas paginados con filtros opcionales"""

    @abstractmethod
    def get_paginated_albums(
        self, page: int, page_size: int, filters: Optional[dict] = None
    ) -> PaginatedResultEntity:
        """Obtiene álbumes paginados con filtros opcionales"""
