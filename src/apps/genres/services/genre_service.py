import logging
from typing import List, Optional

from ..domain.entities import GenreEntity
from ..domain.repository.Igenre_repository import IGenreRepository
from ..infrastructure.repository.genre_repository import GenreRepository


class GenreService:
    """Servicio para gestión de géneros musicales"""

    def __init__(self, repository: Optional[IGenreRepository] = None):
        self.repository = repository or GenreRepository()
        self.logger = logging.getLogger(__name__)

    async def get_all_genres(self, include_inactive: bool = False) -> List[GenreEntity]:
        """Obtiene todos los géneros"""
        try:
            if include_inactive:
                return await self.repository.get_all()
            else:
                return await self.repository.get_active_genres(limit=100)
        except Exception as e:
            self.logger.error(f"Error obteniendo géneros: {str(e)}")
            return []

    async def get_popular_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros populares"""
        try:
            return await self.repository.get_popular_genres(limit=limit)
        except Exception as e:
            self.logger.error(f"Error obteniendo géneros populares: {str(e)}")
            return []

    async def search_genres(self, name: str, limit: int = 10) -> List[GenreEntity]:
        """Busca géneros por nombre"""
        try:
            return await self.repository.search_by_name(name, limit=limit)
        except Exception as e:
            self.logger.error(f"Error buscando géneros por nombre '{name}': {str(e)}")
            return []

    async def get_genre_by_id(self, genre_id: str) -> Optional[GenreEntity]:
        """Obtiene un género por ID"""
        try:
            return await self.repository.get_by_id(genre_id)
        except Exception as e:
            self.logger.error(f"Error obteniendo género con ID '{genre_id}': {str(e)}")
            return None

    async def get_genres_by_category(self, category: str) -> List[GenreEntity]:
        """Obtiene géneros filtrados por categoría (simulado por descripción)"""
        try:
            all_genres = await self.get_all_genres()
            return [
                genre
                for genre in all_genres
                if genre.description and category.lower() in genre.description.lower()
            ]
        except Exception as e:
            self.logger.error(
                f"Error obteniendo géneros por categoría '{category}': {str(e)}"
            )
            return []

    async def update_genre_popularity(self, genre_id: str, increment: int = 1) -> bool:
        """Actualiza la popularidad de un género"""
        try:
            genre = await self.repository.get_by_id(genre_id)
            if not genre:
                return False

            genre.popularity_score += increment
            await self.repository.update(genre_id, genre)
            return True

        except Exception as e:
            self.logger.error(
                f"Error actualizando popularidad del género '{genre_id}': {str(e)}"
            )
            return False
