from typing import Any

from apps.artists.domain.entities import ArtistEntity
from apps.artists.infrastructure.models import ArtistModel
from common.interfaces.imapper.abstract_mapper import AbstractMapper
from common.mixins.logging_mixin import LoggingMixin

from ..dtos import ArtistResponseDTO, CreateArtistRequestDTO, UpdateArtistRequestDTO


class ArtistMapper(AbstractMapper, LoggingMixin):
    """Mapper para convertir entre entidades del dominio y DTOs de la API"""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: ArtistModel) -> ArtistEntity:
        """Convierte un modelo Django a entidad del dominio"""
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

    def entity_to_response_dto(self, entity: ArtistEntity) -> ArtistResponseDTO:
        """Convierte una entidad del dominio a DTO de respuesta"""
        self.logger.debug(f"Converting entity to DTO for artist {entity.id}")
        return ArtistResponseDTO(
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

    def dto_to_entity(self, dto: ArtistResponseDTO) -> ArtistEntity:
        """Convierte un DTO a entidad del dominio"""
        return ArtistEntity(
            id=dto.id,
            name=dto.name,
            biography=dto.biography,
            country=dto.country,
            image_url=dto.image_url,
            followers_count=dto.followers_count,
            is_verified=dto.is_verified,
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def create_request_dto_to_entity(
        self, dto: CreateArtistRequestDTO, artist_id: str
    ) -> ArtistEntity:
        """Convierte un DTO de creación a entidad del dominio"""
        return ArtistEntity(
            id=artist_id,
            name=dto.name,
            biography=dto.biography,
            country=dto.country,
            image_url=dto.image_url,
        )

    def update_request_dto_to_entity_data(
        self, dto: UpdateArtistRequestDTO
    ) -> dict[str, Any]:
        """Convierte un DTO de actualización a datos de entidad"""
        data: dict[str, Any] = {}
        if dto.name is not None:
            data["name"] = dto.name
        if dto.biography is not None:
            data["biography"] = dto.biography
        if dto.country is not None:
            data["country"] = dto.country
        if dto.image_url is not None:
            data["image_url"] = dto.image_url
        if dto.followers_count is not None:
            data["followers_count"] = dto.followers_count
        if dto.is_verified is not None:
            data["is_verified"] = dto.is_verified
        return data
