from apps.artists.domain.entities import ArtistEntity
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ..dtos import ArtistResponseDTO


class ArtistEntityDTOMapper(AbstractEntityDtoMapper[ArtistEntity, ArtistResponseDTO]):
    """Mapper para convertir entre entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: ArtistEntity) -> ArtistResponseDTO:
        """
        Convierte una entidad del dominio a DTO de respuesta.
        """
        self.logger.debug(f"Converting entity to DTO for artist {entity.id}")

        return ArtistResponseDTO(
            id=entity.id,
            name=entity.name,
            biography=entity.biography,
            image_url=entity.image_url,
            followers_count=entity.followers_count,
            is_verified=entity.is_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def dto_to_entity(self, dto: ArtistResponseDTO) -> ArtistEntity:
        """
        Convierte un DTO a entidad del dominio.
        """
        return ArtistEntity(
            id=dto.id,
            name=dto.name,
            biography=dto.biography,
            image_url=dto.image_url,
            followers_count=dto.followers_count,
            is_verified=dto.is_verified,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
