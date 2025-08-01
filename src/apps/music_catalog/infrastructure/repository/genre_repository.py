from typing import List, Optional

from django.db.models import Q

from apps.music_catalog.domain.entities import GenreEntity
from apps.music_catalog.domain.repository.Imusic_repository import IGenreRepository
from src.common.utils import get_logger

from ..models import Genre

logger = get_logger(__name__)


class GenreRepository(IGenreRepository):
    """Implementación del repositorio de géneros"""

    def get_by_id(self, entity_id: str) -> Optional[GenreEntity]:
        try:
            genre = Genre.objects.get(id=entity_id, is_active=True)
            return self._model_to_entity(genre)
        except Genre.DoesNotExist:
            return None

    def get_all(self) -> List[GenreEntity]:
        genres = Genre.objects.filter(is_active=True).order_by("name")
        return [self._model_to_entity(genre) for genre in genres]

    def get_active_genres(self) -> List[GenreEntity]:
        """Obtiene géneros activos"""
        return self.get_all()

    def search_by_name(self, name: str) -> List[GenreEntity]:
        genres = Genre.objects.filter(
            Q(name__icontains=name) & Q(is_active=True)
        ).order_by("name")[:50]
        return [self._model_to_entity(genre) for genre in genres]

    def get_popular_genres(self, limit: int = 50) -> List[GenreEntity]:
        genres = Genre.objects.filter(is_active=True).order_by("-song_count", "name")[
            :limit
        ]
        return [self._model_to_entity(genre) for genre in genres]

    def save(self, entity: GenreEntity) -> GenreEntity:
        genre_data = self._entity_to_model_data(entity)
        genre, created = Genre.objects.update_or_create(
            id=entity.id, defaults=genre_data
        )
        return self._model_to_entity(genre)

    def delete(self, entity_id: str) -> None:
        Genre.objects.filter(id=entity_id).update(is_active=False)

    def update(self, entity_id: str, entity: GenreEntity) -> GenreEntity:
        genre_data = self._entity_to_model_data(entity)
        Genre.objects.filter(id=entity_id).update(**genre_data)
        updated_genre = Genre.objects.get(id=entity_id)
        return self._model_to_entity(updated_genre)

    def _model_to_entity(self, model: Genre) -> GenreEntity:
        return GenreEntity(
            id=str(model.id),
            name=model.name,
            description=model.description,
            image_url=model.image_url,
            song_count=model.song_count,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model_data(self, entity: GenreEntity) -> dict:
        return {
            "name": entity.name,
            "description": entity.description,
            "image_url": entity.image_url,
            "song_count": entity.song_count,
            "is_active": entity.is_active,
        }

    def _entity_to_model(self, entity: GenreEntity) -> Genre:
        # Para compatibilidad con IBaseRepository
        pass
