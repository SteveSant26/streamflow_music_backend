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
            country=model.country,
            image_url=model.image_url,
            followers_count=model.followers_count,
            is_verified=model.is_verified,
            is_active=getattr(model, "is_active", True),  # Backwards compatible
            source_type=getattr(model, "source_type", "manual"),  # Backwards compatible
            source_id=getattr(model, "source_id", None),  # Backwards compatible
            source_url=getattr(model, "source_url", None),  # Backwards compatible
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
            country=entity.country,
            image_url=entity.image_url,
            followers_count=entity.followers_count,
            is_verified=entity.is_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

        # Only set new fields if they exist in the model
        if hasattr(model_instance, "is_active"):
            model_instance.is_active = getattr(entity, "is_active", True)
        if hasattr(model_instance, "source_type"):
            model_instance.source_type = getattr(entity, "source_type", "manual")
        if hasattr(model_instance, "source_id"):
            model_instance.source_id = getattr(entity, "source_id", None)
        if hasattr(model_instance, "source_url"):
            model_instance.source_url = getattr(entity, "source_url", None)

        return model_instance

    def entity_to_model_data(self, entity: ArtistEntity) -> Dict[str, Any]:
        """
        Convierte una entidad ArtistEntity a datos del modelo Django (diccionario).
        """
        self.logger.debug(f"Converting entity to model data for artist {entity.id}")
        model_data = {
            "name": entity.name,
            "biography": entity.biography,
            "country": entity.country,
            "image_url": entity.image_url,
            "followers_count": entity.followers_count,
            "is_verified": entity.is_verified,
        }

        # Only include new fields if they exist in the entity
        if hasattr(entity, "is_active"):
            model_data["is_active"] = entity.is_active
        if hasattr(entity, "source_type"):
            model_data["source_type"] = entity.source_type
        if hasattr(entity, "source_id") and entity.source_id is not None:
            model_data["source_id"] = entity.source_id
        if hasattr(entity, "source_url") and entity.source_url is not None:
            model_data["source_url"] = entity.source_url

        return model_data
