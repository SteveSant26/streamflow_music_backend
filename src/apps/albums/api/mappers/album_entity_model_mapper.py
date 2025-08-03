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
            artist_id=str(model.artist_id),
            artist_name=model.artist_name,
            release_date=model.release_date,
            description=model.description,
            cover_image_url=model.cover_image_url,
            total_tracks=model.total_tracks,
            play_count=model.play_count,
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
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def entity_to_model_data(self, entity: AlbumEntity) -> Dict[str, Any]:
        """
        Convierte una entidad AlbumEntity a datos del modelo Django (diccionario).
        """
        self.logger.debug(f"Converting entity to model data for album {entity.id}")
        return {
            "title": entity.title,
            "artist_id": entity.artist_id,
            "artist_name": entity.artist_name,
            "release_date": entity.release_date,
            "description": entity.description,
            "cover_image_url": entity.cover_image_url,
            "total_tracks": entity.total_tracks,
            "play_count": entity.play_count,
        }
