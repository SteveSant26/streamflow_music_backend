from typing import List, cast

from django.db.models import Q

from apps.music_catalog.domain.entities import GenreEntity
from apps.music_catalog.domain.repository.Igenre_repository import IGenreRepository
from src.common.core import BaseDjangoRepository

from ..models import GenreModel


class GenreRepository(BaseDjangoRepository[GenreEntity, GenreModel], IGenreRepository):
    """
    Implementación del repositorio de géneros que combina funcionalidades
    de solo lectura y solo escritura, implementando la interfaz IGenreRepository.
    """

    def __init__(self):
        super().__init__(GenreModel)

    # Métodos específicos del repositorio de géneros (implementación de IGenreRepository)

    def get_active_genres(self) -> List[GenreEntity]:
        """Obtiene géneros activos"""
        return self.get_all()

    def search_by_name(self, name: str) -> List[GenreEntity]:
        """Busca géneros por nombre"""
        genres = GenreModel.objects.filter(
            Q(name__icontains=name) & Q(is_active=True)
        ).order_by("name")[:50]
        return [self._model_to_entity(genre) for genre in genres]

    # Implementación de métodos abstractos del repositorio base

    def _model_to_entity(self, model: GenreModel) -> GenreEntity:
        """Convierte un modelo Genre a entidad GenreEntity"""
        # Cast para que el type checker entienda que model es de tipo Genre
        genre_model = cast(GenreModel, model)
        return GenreEntity(
            id=str(genre_model.id),
            name=genre_model.name,
            description=genre_model.description,
            image_url=None,  # Campo no disponible en el modelo
            song_count=0,  # Este campo podría calcularse dinámicamente si es necesario
            is_active=genre_model.is_active,
            created_at=genre_model.created_at,
            updated_at=genre_model.updated_at,
        )

    def _entity_to_model_data(self, entity: GenreEntity) -> dict:
        """Convierte una entidad GenreEntity a datos del modelo"""
        return {
            "name": entity.name,
            "description": entity.description,
            "is_active": entity.is_active,
        }

    def _entity_to_model(self, entity: GenreEntity) -> GenreModel:
        """Para compatibilidad con IBaseRepository - implementación no requerida en la práctica"""
        # Este método existe para cumplir con la interfaz pero no se usa directamente
        # Las operaciones usan _entity_to_model_data() en su lugar
        return GenreModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
        )

    def _apply_default_ordering(self, queryset):
        """Aplica ordenamiento específico para géneros"""
        return queryset.order_by("name")
