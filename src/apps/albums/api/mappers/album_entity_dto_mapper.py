from apps.albums.domain.entities import AlbumEntity
<<<<<<< HEAD
from common.mixins.logging_mixin import LoggingMixin
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from src.common.interfaces.imapper.abstract_entity_dto_mapper import (
    AbstractEntityDtoMapper,
)

from ..dtos import AlbumResponseDTO


<<<<<<< HEAD
class AlbumEntityDTOMapper(AbstractEntityDtoMapper, LoggingMixin):
=======
class AlbumEntityDTOMapper(AbstractEntityDtoMapper[AlbumEntity, AlbumResponseDTO]):
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    """Mapper para convertir entre entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: AlbumEntity) -> AlbumResponseDTO:
        """
        Convierte una entidad del dominio a DTO de respuesta.
        """
        self.logger.debug(f"Converting entity to DTO for album {entity.id}")

        return AlbumResponseDTO(
            id=entity.id,
            title=entity.title,
            artist_id=entity.artist_id,
            artist_name=entity.artist_name,
            release_date=entity.release_date,
            description=entity.description,
            cover_image_url=entity.cover_image_url,
            total_tracks=entity.total_tracks,
            play_count=entity.play_count,
<<<<<<< HEAD
=======
            source_type=entity.source_type,
            source_id=entity.source_id,
            source_url=entity.source_url,
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def dto_to_entity(self, dto: AlbumResponseDTO) -> AlbumEntity:
        """
        Convierte un DTO a entidad del dominio.
        """
        return AlbumEntity(
            id=dto.id,
            title=dto.title,
            artist_id=dto.artist_id,
            artist_name=dto.artist_name,
            release_date=dto.release_date,
            description=dto.description,
            cover_image_url=dto.cover_image_url,
            total_tracks=dto.total_tracks,
            play_count=dto.play_count,
<<<<<<< HEAD
=======
            source_type=dto.source_type,
            source_id=dto.source_id,
            source_url=dto.source_url,
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
