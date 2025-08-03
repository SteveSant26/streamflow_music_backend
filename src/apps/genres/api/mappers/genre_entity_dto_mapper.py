"""
Genre entity to DTO mapper class for converting between GenreEntity and DTOs.
"""

from apps.genres.domain.entities import GenreEntity
from src.common.interfaces.imapper.abstract_entity_dto_mapper import (
    AbstractEntityDtoMapper,
)

from ..dtos import GenreResponseDTO


class GenreEntityDTOMapper(AbstractEntityDtoMapper[GenreEntity, GenreResponseDTO]):
    """Mapper para convertir entre entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: GenreEntity) -> GenreResponseDTO:
        """
        Convierte una entidad del dominio a DTO de respuesta.
        """
        self.logger.debug(f"Converting entity to DTO for genre {entity.id}")

        return GenreResponseDTO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            image_url=entity.image_url,
            color_hex=entity.color_hex,
            popularity_score=entity.popularity_score,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def dto_to_entity(self, dto: GenreResponseDTO) -> GenreEntity:
        """
        Convierte un DTO a entidad del dominio.
        """
        return GenreEntity(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            image_url=dto.image_url,
            color_hex=dto.color_hex,
            popularity_score=dto.popularity_score,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
