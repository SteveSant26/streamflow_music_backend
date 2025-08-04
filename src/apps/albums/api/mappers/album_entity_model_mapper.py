from typing import Any, Dict

from apps.albums.domain.entities import AlbumEntity
from apps.albums.infrastructure.models import AlbumModel
from common.interfaces.imapper import AbstractEntityModelMapper


class AlbumEntityModelMapper(AbstractEntityModelMapper[AlbumEntity, AlbumModel]):
    """Mapper para convertir entre entidades del dominio y modelos de Album."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: AlbumModel) -> AlbumEntity:
        """
        Convierte un modelo Django AlbumModel a entidad del dominio AlbumEntity.
        """
        self.logger.debug(f"Converting model to entity for album {model.id}")
        return AlbumEntity(
            id=str(model.id),
            title=model.title,
            artist_id=str(model.artist.id) if model.artist else None,
            artist_name=model.artist.name if model.artist else "",
            release_date=model.release_date,
            description=model.description,
            cover_image_url=model.cover_image_url,
            total_tracks=model.total_tracks,
            play_count=model.play_count,
            source_type=getattr(model, "source_type", "unknown"),
            source_id=getattr(model, "source_id", None),
            source_url=getattr(model, "source_url", None),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def entity_to_model(self, entity: AlbumEntity) -> AlbumModel:
        """
        Convierte una entidad AlbumEntity a una instancia del modelo Django AlbumModel.
        """
        self.logger.debug(f"Converting entity to model instance for album {entity.id}")
        return AlbumModel(
            id=entity.id,
            title=entity.title,
            artist_id=entity.artist_id,
            artist_name=entity.artist_name,
            release_date=entity.release_date,
            description=entity.description,
            cover_image_url=entity.cover_image_url,
            total_tracks=entity.total_tracks,
            play_count=entity.play_count,
            source_type=entity.source_type,
            source_id=entity.source_id,
            source_url=entity.source_url,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def entity_to_model_data(self, entity: AlbumEntity) -> Dict[str, Any]:
        """
        Convierte una entidad AlbumEntity a datos del modelo Django (diccionario).
        """
        self.logger.debug(f"Converting entity to model data for album {entity.id}")

        model_data = {
            "title": entity.title,
            "artist_id": entity.artist_id,
            "release_date": entity.release_date,
            "description": entity.description,
            "cover_image_url": entity.cover_image_url,
            "total_tracks": entity.total_tracks,
            "play_count": entity.play_count,
        }

        # Only include new fields if they exist in the entity
        if hasattr(entity, "artist_name") and entity.artist_name is not None:
            model_data["artist_name"] = entity.artist_name
        if hasattr(entity, "source_type"):
            model_data["source_type"] = entity.source_type
        if hasattr(entity, "source_id") and entity.source_id is not None:
            model_data["source_id"] = entity.source_id
        if hasattr(entity, "source_url") and entity.source_url is not None:
            model_data["source_url"] = entity.source_url

        return model_data
