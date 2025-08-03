"""
Genre entity to model mapper class for converting between GenreEntity and GenreModel.
"""

from apps.genres.domain.entities import GenreEntity
from apps.genres.infrastructure.models import GenreModel
from src.common.interfaces.imapper import AbstractEntityModelMapper


class GenreEntityModelMapper(AbstractEntityModelMapper[GenreModel, GenreEntity]):
    """Mapper para convertir entre entidades del dominio y modelos de Genre."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: GenreModel) -> GenreEntity:
        """
        Convierte un modelo Django GenreModel a entidad del dominio GenreEntity.
        """
        self.logger.debug(f"Converting model to entity for genre {model.id}")
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

    def entity_to_model(self, entity: GenreEntity) -> GenreModel:
        """
        Convierte una entidad GenreEntity a una instancia del modelo Django GenreModel.
        """
        self.logger.debug(f"Converting entity to model instance for genre {entity.id}")
        return GenreModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            image_url=entity.image_url,
            color_hex=entity.color_hex,
            popularity_score=entity.popularity_score,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
