from typing import List, Optional

from django.db.models import Q

from apps.music_catalog.domain.entities import ArtistEntity
from apps.music_catalog.domain.repository.Imusic_repository import IArtistRepository
from src.common.utils import get_logger

from ..models import Artist

logger = get_logger(__name__)


class ArtistRepository(IArtistRepository):
    """Implementación del repositorio de artistas"""

    def get_by_id(self, entity_id: str) -> Optional[ArtistEntity]:
        try:
            artist = Artist.objects.get(id=entity_id, is_active=True)
            return self._model_to_entity(artist)
        except Artist.DoesNotExist:
            return None

    def get_all(self) -> List[ArtistEntity]:
        artists = Artist.objects.filter(is_active=True).order_by("name")
        return [self._model_to_entity(artist) for artist in artists]

    def search_by_name(self, name: str) -> List[ArtistEntity]:
        artists = Artist.objects.filter(
            Q(name__icontains=name) & Q(is_active=True)
        ).order_by("name")[:50]
        return [self._model_to_entity(artist) for artist in artists]

    def get_by_country(self, country: str) -> List[ArtistEntity]:
        """Obtiene artistas por país"""
        artists = Artist.objects.filter(
            country__iexact=country, is_active=True
        ).order_by("name")
        return [self._model_to_entity(artist) for artist in artists]

    def get_popular_artists(self, limit: int = 50) -> List[ArtistEntity]:
        artists = Artist.objects.filter(is_active=True).order_by(
            "-followers_count", "name"
        )[:limit]
        return [self._model_to_entity(artist) for artist in artists]

    def save(self, entity: ArtistEntity) -> ArtistEntity:
        artist_data = self._entity_to_model_data(entity)
        artist, created = Artist.objects.update_or_create(
            id=entity.id, defaults=artist_data
        )
        return self._model_to_entity(artist)

    def delete(self, entity_id: str) -> None:
        Artist.objects.filter(id=entity_id).update(is_active=False)

    def update(self, entity_id: str, entity: ArtistEntity) -> ArtistEntity:
        artist_data = self._entity_to_model_data(entity)
        Artist.objects.filter(id=entity_id).update(**artist_data)
        updated_artist = Artist.objects.get(id=entity_id)
        return self._model_to_entity(updated_artist)

    def _model_to_entity(self, model: Artist) -> ArtistEntity:
        return ArtistEntity(
            id=str(model.id),
            name=model.name,
            biography=model.biography,
            country=model.country,
            image_url=model.image_url,
            followers_count=model.followers_count,
            is_verified=model.is_verified,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model_data(self, entity: ArtistEntity) -> dict:
        return {
            "name": entity.name,
            "biography": entity.biography,
            "country": entity.country,
            "image_url": entity.image_url,
            "followers_count": entity.followers_count,
            "is_verified": entity.is_verified,
            "is_active": entity.is_active,
        }

    def _entity_to_model(self, entity: ArtistEntity) -> Artist:
        # Para compatibilidad con IBaseRepository
        pass
