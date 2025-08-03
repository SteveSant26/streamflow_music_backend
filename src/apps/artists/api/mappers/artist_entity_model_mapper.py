"""
Artist entity to model mapper class for converting between ArtistEntity and ArtistModel.
"""

from apps.artists.domain.entities import ArtistEntity
from apps.artists.infrastructure.models import ArtistModel
from src.common.interfaces.imapper import AbstractEntityModelMapper


class ArtistEntityModelMapper(AbstractEntityModelMapper[ArtistModel, ArtistEntity]):
    """Mapper para convertir entre entidades del dominio y modelos de Artist."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: ArtistModel) -> ArtistEntity:
        """
        Convierte un modelo Django ArtistModel a entidad del dominio ArtistEntity.
        """
        self.logger.debug(f"Converting model to entity for artist {model.id}")
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

    def entity_to_model(self, entity: ArtistEntity) -> ArtistModel:
        """
        Convierte una entidad ArtistEntity a una instancia del modelo Django ArtistModel.
        """
        self.logger.debug(f"Converting entity to model instance for artist {entity.id}")
        return ArtistModel(
            id=entity.id,
            name=entity.name,
            biography=entity.biography,
            country=entity.country,
            image_url=entity.image_url,
            followers_count=entity.followers_count,
            is_verified=entity.is_verified,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
