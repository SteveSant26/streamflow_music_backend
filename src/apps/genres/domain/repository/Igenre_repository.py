from abc import abstractmethod
from typing import Any, List

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import GenreEntity


class IGenreRepository(IBaseRepository[GenreEntity, Any]):
    """Interface del repositorio de géneros"""

    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 10) -> List[GenreEntity]:
        """Busca géneros por nombre"""

    @abstractmethod
    async def get_popular_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros populares"""

    @abstractmethod
    async def get_active_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros activos"""

    @abstractmethod
    async def get_genres_by_popularity_range(
        self, min_score: int, max_score: int
    ) -> List[GenreEntity]:
        """Busca géneros por rango de popularidad"""

    @abstractmethod
    async def get_recent_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros recientes"""
