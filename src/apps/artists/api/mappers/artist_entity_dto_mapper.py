from apps.artists.domain.entities import ArtistEntity
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper
<<<<<<< HEAD
from common.mixins.logging_mixin import LoggingMixin
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

from ..dtos import ArtistResponseDTO


<<<<<<< HEAD
class ArtistEntityDTOMapper(
    AbstractEntityDtoMapper[ArtistEntity, ArtistResponseDTO], LoggingMixin
):
=======
class ArtistEntityDTOMapper(AbstractEntityDtoMapper[ArtistEntity, ArtistResponseDTO]):
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
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
<<<<<<< HEAD
            country=entity.country,
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
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
<<<<<<< HEAD
            country=dto.country,
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            image_url=dto.image_url,
            followers_count=dto.followers_count,
            is_verified=dto.is_verified,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
