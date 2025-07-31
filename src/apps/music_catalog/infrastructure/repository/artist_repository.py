from typing import List, cast

from django.db.models import Q

from apps.music_catalog.domain.entities import ArtistEntity
from apps.music_catalog.domain.repository.Iartist_repository import IArtistRepository
from src.common.core import BaseDjangoRepository

from ..models import ArtistModel


class ArtistRepository(
    BaseDjangoRepository[ArtistEntity, ArtistModel], IArtistRepository
):
    """
    Implementación del repositorio de artistas que combina funcionalidades
    de solo lectura y solo escritura, implementando la interfaz IArtistRepository.
    """

    def __init__(self):
        super().__init__(ArtistModel)

    # Métodos específicos del repositorio de artistas (implementación de IArtistRepository)

    def search_by_name(self, name: str) -> List[ArtistEntity]:
        """Busca artistas por nombre"""
        artists = ArtistModel.objects.filter(
            Q(name__icontains=name) & Q(is_active=True)
        ).order_by("name")[:50]
        return [self._model_to_entity(artist) for artist in artists]

    def get_by_country(self, country: str) -> List[ArtistEntity]:
        """Obtiene artistas por país"""
        artists = ArtistModel.objects.filter(
            country__iexact=country, is_active=True
        ).order_by("name")
        return [self._model_to_entity(artist) for artist in artists]

    def get_popular_artists(self, limit: int = 50) -> List[ArtistEntity]:
        """Obtiene artistas populares"""
        # Como no tenemos campo followers_count, ordenamos por fecha de creación
        artists = ArtistModel.objects.filter(is_active=True).order_by(
            "-created_at", "name"
        )[:limit]
        return [self._model_to_entity(artist) for artist in artists]

    # Implementación de métodos abstractos del repositorio base

    def _model_to_entity(self, model: ArtistModel) -> ArtistEntity:
        """Convierte un modelo Artist a entidad ArtistEntity"""
        # Cast para que el type checker entienda que model es de tipo Artist
        artist_model = cast(ArtistModel, model)
        return ArtistEntity(
            id=str(artist_model.id),
            name=artist_model.name,
            biography=artist_model.biography,
            country=artist_model.country,
            image_url=artist_model.image_url,
            followers_count=0,  # Campo no disponible en el modelo
            is_verified=False,  # Campo no disponible en el modelo
            is_active=artist_model.is_active,
            created_at=artist_model.created_at,
            updated_at=artist_model.updated_at,
        )

    def _entity_to_model_data(self, entity: ArtistEntity) -> dict:
        """Convierte una entidad ArtistEntity a datos del modelo"""
        return {
            "name": entity.name,
            "biography": entity.biography,
            "country": entity.country,
            "image_url": entity.image_url,
            "is_active": entity.is_active,
        }

    def _entity_to_model(self, entity: ArtistEntity) -> ArtistModel:
        """Para compatibilidad con IBaseRepository - implementación no requerida en la práctica"""
        # Este método existe para cumplir con la interfaz pero no se usa directamente
        # Las operaciones usan _entity_to_model_data() en su lugar
        # Para evitar errores, creamos un modelo mock (no recomendado en producción)
        return ArtistModel(
            id=entity.id,
            name=entity.name,
            biography=entity.biography,
            country=entity.country,
            image_url=entity.image_url,
            is_active=entity.is_active,
        )

    def _apply_default_ordering(self, queryset):
        """Aplica ordenamiento específico para artistas"""
        return queryset.order_by("name")
