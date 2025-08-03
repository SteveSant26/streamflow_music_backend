from typing import Any, List, Optional

from apps.artists.api.mappers import ArtistEntityModelMapper
from apps.artists.domain.repository import IArtistRepository
from common.core import BaseDjangoRepository

from ...domain.entities import ArtistEntity
from ..models import ArtistModel


class ArtistRepository(
    BaseDjangoRepository[ArtistEntity, ArtistModel], IArtistRepository
):
    """Implementación del repositorio de artistas"""

    def __init__(self):
        super().__init__(ArtistModel, ArtistEntityModelMapper())

    def _model_to_entity(self, model: ArtistModel) -> ArtistEntity:
        """Convierte un modelo Django a entidad del dominio"""
        return self.mapper.model_to_entity(model)

    def _entity_to_model(self, entity: ArtistEntity) -> dict[str, Any]:
        """Convierte una entidad a datos del modelo"""
        return self.mapper.entity_to_model(entity)

    async def find_by_name(self, name: str) -> Optional[ArtistEntity]:
        """Busca un artista por nombre exacto"""
        try:
            model = await self.model_class.objects.aget(
                name__iexact=name, is_active=True
            )
            return self._model_to_entity(model)
        except self.model_class.DoesNotExist:
            return None

    async def search_by_name(self, name: str, limit: int = 10) -> List[ArtistEntity]:
        """Busca artistas por nombre (búsqueda parcial)"""
        models = self.model_class.objects.filter(
            name__icontains=name, is_active=True
        ).order_by("-followers_count")[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def find_by_country(
        self, country: str, limit: int = 10
    ) -> List[ArtistEntity]:
        """Busca artistas por país"""
        models = self.model_class.objects.filter(
            country__iexact=country, is_active=True
        ).order_by("-followers_count")[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def get_popular_artists(self, limit: int = 10) -> List[ArtistEntity]:
        """Obtiene los artistas más populares"""
        models = self.model_class.objects.filter(is_active=True).order_by(
            "-followers_count"
        )[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def get_verified_artists(self, limit: int = 10) -> List[ArtistEntity]:
        """Obtiene artistas verificados"""
        models = self.model_class.objects.filter(
            is_verified=True, is_active=True
        ).order_by("-followers_count")[:limit]
        return [self._model_to_entity(model) async for model in models]
