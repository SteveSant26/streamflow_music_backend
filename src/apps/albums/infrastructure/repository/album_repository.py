from typing import Any, List

from apps.albums.api.mappers import AlbumEntityModelMapper
from apps.albums.domain.repository import IAlbumRepository
from common.core import BaseDjangoRepository

from ...domain.entities import AlbumEntity
from ..models import AlbumModel


class AlbumRepository(BaseDjangoRepository[AlbumEntity, AlbumModel], IAlbumRepository):
    """Implementación del repositorio de álbumes"""

    def __init__(self):
        super().__init__(AlbumModel, AlbumEntityModelMapper())

    def _model_to_entity(self, model: AlbumModel) -> AlbumEntity:
        """Convierte un modelo Django a entidad del dominio"""
        return self.mapper.model_to_entity(model)

    def _entity_to_model(self, entity: AlbumEntity) -> dict[str, Any]:
        """Convierte una entidad a datos del modelo"""
        return self.mapper.entity_to_model(entity)

    async def find_by_artist_id(
        self, artist_id: str, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por ID del artista"""
        models = self.model_class.objects.filter(
            artist_id=artist_id, is_active=True
        ).order_by("-release_date")[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def search_by_title(self, title: str, limit: int = 10) -> List[AlbumEntity]:
        """Busca álbumes por título"""
        models = self.model_class.objects.filter(
            title__icontains=title, is_active=True
        ).order_by("-play_count")[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def get_recent_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""
        models = self.model_class.objects.filter(is_active=True).order_by(
            "-created_at"
        )[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def get_popular_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes populares"""
        models = self.model_class.objects.filter(is_active=True).order_by(
            "-play_count"
        )[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def find_by_release_year(
        self, year: int, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por año de lanzamiento"""
        models = self.model_class.objects.filter(
            release_date__year=year, is_active=True
        ).order_by("-play_count")[:limit]
        return [self._model_to_entity(model) async for model in models]
