from typing import Any, List

from apps.genres.domain.repository import IGenreRepository
from src.common.core import BaseDjangoRepository

from ...domain.entities import GenreEntity
from ..models import GenreModel


class GenreRepository(BaseDjangoRepository[GenreEntity, GenreModel], IGenreRepository):
    """Implementación del repositorio de géneros"""

    def __init__(self):
        super().__init__(GenreModel)

    def _model_to_entity(self, model: GenreModel) -> GenreEntity:
        """Convierte un modelo Django a entidad del dominio"""
        return GenreEntity(
            id=str(model.id),
            name=model.name,
            description=model.description,
            image_url=model.image_url,
            color_hex=model.color_hex,
            popularity_score=model.popularity_score,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model_data(self, entity: GenreEntity) -> dict[str, Any]:
        """Convierte una entidad a datos del modelo"""
        return {
            "name": entity.name,
            "description": entity.description,
            "image_url": entity.image_url,
            "color_hex": entity.color_hex,
            "popularity_score": entity.popularity_score,
            "is_active": entity.is_active,
        }

    def _entity_to_model(self, entity: GenreEntity) -> GenreModel:
        """Convierte una entidad GenreEntity a un modelo Django GenreModel"""
        genre_data = self._entity_to_model_data(entity)
        try:
            if hasattr(entity, "id") and entity.id:
                genre = GenreModel.objects.get(id=entity.id)
                for key, value in genre_data.items():
                    setattr(genre, key, value)
                return genre
            else:
                return GenreModel(**genre_data)
        except GenreModel.DoesNotExist:
            return GenreModel(**genre_data)

    def search_by_name(self, name: str, limit: int = 10) -> List[GenreEntity]:
        """Busca géneros por nombre"""
        self.logger.debug(f"Searching genres by name: {name} with limit: {limit}")
        models = self.model_class.objects.filter(
            name__icontains=name, is_active=True
        ).order_by("name")[:limit]
        return [self._model_to_entity(model) for model in models]

    def get_popular_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros populares"""
        self.logger.debug(f"Getting popular genres with limit: {limit}")
        models = self.model_class.objects.filter(is_active=True).order_by(
            "-popularity_score", "name"
        )[:limit]
        return [self._model_to_entity(model) for model in models]

    def get_active_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros activos"""
        self.logger.debug(f"Getting active genres with limit: {limit}")
        models = self.model_class.objects.filter(is_active=True).order_by("name")[
            :limit
        ]
        return [self._model_to_entity(model) for model in models]

    def get_genres_by_popularity_range(
        self, min_score: int, max_score: int
    ) -> List[GenreEntity]:
        """Busca géneros por rango de popularidad"""
        self.logger.debug(
            f"Getting genres by popularity range: {min_score}-{max_score}"
        )
        models = self.model_class.objects.filter(
            popularity_score__gte=min_score,
            popularity_score__lte=max_score,
            is_active=True,
        ).order_by("-popularity_score", "name")
        return [self._model_to_entity(model) for model in models]

    def get_recent_genres(self, limit: int = 10) -> List[GenreEntity]:
        """Obtiene géneros recientes"""
        self.logger.debug(f"Getting recent genres with limit: {limit}")
        models = self.model_class.objects.filter(is_active=True).order_by(
            "-created_at", "name"
        )[:limit]
        return [self._model_to_entity(model) for model in models]
