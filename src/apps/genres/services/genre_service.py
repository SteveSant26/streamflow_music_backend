from typing import List, Optional

from ..api.dtos import GetPopularGenresRequestDTO, SearchGenresByNameRequestDTO
from ..domain.entities import GenreEntity
from ..domain.repository.Igenre_repository import IGenreRepository
from ..infrastructure.repository.genre_repository import GenreRepository
from ..use_cases import (
    GetAllGenresUseCase,
    GetGenreUseCase,
    GetPopularGenresUseCase,
    SearchGenresByNameUseCase,
)


class GenreService:
    """Servicio para gestión de géneros musicales"""

    def __init__(self, repository: Optional[IGenreRepository] = None):
        self.repository = repository or GenreRepository()

        # Inicializar casos de uso
        self.get_all_genres_use_case = GetAllGenresUseCase(self.repository)
        self.get_genre_use_case = GetGenreUseCase(self.repository)
        self.get_popular_genres_use_case = GetPopularGenresUseCase(self.repository)
        self.search_genres_use_case = SearchGenresByNameUseCase(self.repository)

    async def get_all_genres(self) -> List[GenreEntity]:
        """Obtiene todos los géneros"""
        try:
            return await self.get_all_genres_use_case.execute()
        except Exception:
            return []

    async def get_popular_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros populares"""
        try:
            request_dto = GetPopularGenresRequestDTO(limit=limit)
            return await self.get_popular_genres_use_case.execute(request_dto)
        except Exception:
            return []

    async def search_genres(self, name: str, limit: int = 10) -> List[GenreEntity]:
        """Busca géneros por nombre"""
        try:
            request_dto = SearchGenresByNameRequestDTO(query=name, limit=limit)
            return await self.search_genres_use_case.execute(request_dto)
        except Exception:
            return []

    async def get_genre_by_id(self, genre_id: str) -> Optional[GenreEntity]:
        """Obtiene un género por ID"""
        try:
            return await self.get_genre_use_case.execute(genre_id)
        except Exception:
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
        except Exception:
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

        except Exception:
            return False
