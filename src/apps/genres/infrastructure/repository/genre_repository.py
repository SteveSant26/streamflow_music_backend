from typing import List

from asgiref.sync import sync_to_async

from apps.genres.api.mappers import GenreEntityModelMapper
from apps.genres.domain.repository import IGenreRepository
from common.core import BaseDjangoRepository

from ...domain.entities import GenreEntity
from ..models import GenreModel


class GenreRepository(BaseDjangoRepository[GenreEntity, GenreModel], IGenreRepository):
    """Implementación del repositorio de géneros"""

    def __init__(self):
        super().__init__(GenreModel, GenreEntityModelMapper())

    async def search_by_name(self, name: str, limit: int = 10) -> List[GenreEntity]:
        """Busca géneros por nombre"""
        self.logger.debug(f"Searching genres by name: {name} with limit: {limit}")
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.filter(name__icontains=name).order_by("name")[
                    :limit
                ]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def get_popular_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros populares"""
        self.logger.debug(f"Getting popular genres with limit: {limit}")
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.all().order_by("-popularity_score", "name")[
                    :limit
                ]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def get_active_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros activos"""
        self.logger.debug(f"Getting active genres with limit: {limit}")
        models = await sync_to_async(
            lambda: list(self.model_class.objects.all().order_by("name")[:limit])
        )()
        return self.mapper.models_to_entities(models)

    async def get_genres_by_popularity_range(
        self, min_score: int, max_score: int
    ) -> List[GenreEntity]:
        """Busca géneros por rango de popularidad"""
        self.logger.debug(
            f"Getting genres by popularity range: {min_score}-{max_score}"
        )
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.filter(
                    popularity_score__gte=min_score, popularity_score__lte=max_score
                ).order_by("-popularity_score", "name")
            )
        )()
        return self.mapper.models_to_entities(models)

    async def get_recent_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros recientes"""
        self.logger.debug(f"Getting recent genres with limit: {limit}")
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.all().order_by("-created_at", "name")[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)
