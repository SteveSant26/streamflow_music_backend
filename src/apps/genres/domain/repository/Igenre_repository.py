from abc import abstractmethod
from typing import Any, List

from src.common.interfaces.ibase_repository import IBaseRepository

from ..entities import GenreEntity


class IGenreRepository(IBaseRepository[GenreEntity, Any]):
    """Interface del repositorio de géneros"""

    @abstractmethod
    async def get_popular_genres(
        self,
    ) -> List[GenreEntity]:
        """Obtiene géneros populares"""

    @abstractmethod
    async def get_genres_by_popularity_range(
        self, min_score: int, max_score: int
    ) -> List[GenreEntity]:
        """Busca géneros por rango de popularidad"""

    @abstractmethod
    async def get_recent_genres(self) -> List[GenreEntity]:
        """Obtiene géneros recientes"""
