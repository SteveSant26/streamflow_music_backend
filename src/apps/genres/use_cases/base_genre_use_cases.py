"""
Casos de uso base para operaciones comunes de géneros.

Este módulo contiene clases base y utilidades comunes que pueden ser
reutilizadas por otros casos de uso específicos de géneros.
"""

from typing import List, Optional

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import GenreEntity
from ..domain.repository import IGenreRepository


class BaseGenreUseCase(BaseUseCase):
    """Clase base para casos de uso de géneros con funcionalidades comunes"""

    def __init__(self, repository: IGenreRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=False, include_result=False, log_level="DEBUG")
    async def _validate_genre_exists(self, genre_id: str) -> GenreEntity:
        """
        Valida que un género existe y lo retorna.

        Args:
            genre_id: ID del género a validar

        Returns:
            GenreEntity: El género encontrado

        Raises:
            GenreNotFoundException: Si el género no existe
        """
        from ..domain.exceptions import GenreNotFoundException

        genre = await self.repository.get_by_id(genre_id)
        if not genre:
            raise GenreNotFoundException(genre_id)
        return genre

    @log_performance(threshold_seconds=0.5)
    async def _get_genres_by_ids(self, genre_ids: List[str]) -> List[GenreEntity]:
        """
        Obtiene múltiples géneros por sus IDs.

        Args:
            genre_ids: Lista de IDs de géneros

        Returns:
            Lista de géneros encontrados
        """
        genres = []
        for genre_id in genre_ids:
            try:
                genre = await self._validate_genre_exists(genre_id)
                genres.append(genre)
            except Exception as e:
                self.logger.warning(f"Genre {genre_id} not found: {e}")
                continue
        return genres

    async def _search_genres_with_pagination(
        self,
        query: Optional[str] = None,
        limit: int = 10,
    ) -> List[GenreEntity]:
        """
        Busca géneros con límite.

        Args:
            query: Término de búsqueda opcional
            limit: Límite de resultados

        Returns:
            Lista de géneros
        """
        if query:
            return await self.repository.search_by_name(query, limit)
        else:
            return await self.repository.get_all()
