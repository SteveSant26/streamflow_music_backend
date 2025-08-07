"""
Artist entity to model mapper class for converting between ArtistEntity and ArtistModel.
"""

from typing import Any, Dict

from apps.artists.domain.entities import ArtistEntity
from apps.artists.infrastructure.models import ArtistModel
from common.interfaces.imapper import AbstractEntityModelMapper


class ArtistEntityModelMapper(AbstractEntityModelMapper[ArtistEntity, ArtistModel]):
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
<<<<<<< HEAD
            country=model.country,
            image_url=model.image_url,
            followers_count=model.followers_count,
            is_verified=model.is_verified,
            source_type=model.source_type,  # Backwards compatible
            source_id=model.source_id,  # Backwards compatible
            source_url=model.source_url,  # Backwards compatible
=======
            image_url=model.image_url,
            followers_count=model.followers_count,
            is_verified=model.is_verified,
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def entity_to_model(self, entity: ArtistEntity) -> ArtistModel:
        """
        Convierte una entidad ArtistEntity a una instancia del modelo Django ArtistModel.
        """
        self.logger.debug(f"Converting entity to model instance for artist {entity.id}")
        model_instance = ArtistModel(
            id=entity.id,
            name=entity.name,
            biography=entity.biography,
<<<<<<< HEAD
            country=entity.country,
            image_url=entity.image_url,
            source_type=entity.source_type,
            source_id=entity.source_id,
            source_url=entity.source_url,
=======
            image_url=entity.image_url,
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            followers_count=entity.followers_count,
            is_verified=entity.is_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

        return model_instance

    def entity_to_model_data(self, entity: ArtistEntity) -> Dict[str, Any]:
        """
        Convierte una entidad ArtistEntity a datos del modelo Django (diccionario).
        """
        self.logger.debug(f"Converting entity to model data for artist {entity.id}")
        model_data = {
            "name": entity.name,
            "biography": entity.biography,
<<<<<<< HEAD
            "country": entity.country,
            "source_type": entity.source_type,
            "source_id": entity.source_id,
            "source_url": entity.source_url,
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            "image_url": entity.image_url,
            "followers_count": entity.followers_count,
            "is_verified": entity.is_verified,
        }

        return model_data
