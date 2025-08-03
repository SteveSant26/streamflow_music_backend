from apps.albums.domain.entities import AlbumEntity
from common.mixins.logging_mixin import LoggingMixin
from src.common.interfaces.imapper.abstract_entity_dto_mapper import (
    AbstractEntityDtoMapper,
)

from ..dtos import AlbumResponseDTO


class AlbumEntityDTOMapper(
    AbstractEntityDtoMapper[AlbumEntity, AlbumResponseDTO], LoggingMixin
):
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
            is_active=entity.is_active,
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
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
