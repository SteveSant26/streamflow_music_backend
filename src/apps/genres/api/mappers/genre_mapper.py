from apps.genres.domain.entities import GenreEntity
from apps.genres.infrastructure.models.genre_model import GenreModel
from common.interfaces.imapper.abstract_mapper import AbstractMapper
from common.mixins.logging_mixin import LoggingMixin

from ..dtos import GenreResponseDTO


class GenreMapper(AbstractMapper, LoggingMixin):
    """Mapper para convertir entre entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: GenreModel) -> GenreEntity:
        """
        Convierte un modelo de Django a entidad del dominio.
        """
        self.logger.debug(f"Converting model to entity for genre {model.id}")
        return GenreEntity(
            id=str(model.id),
            name=model.name,
            description=model.description,
            image_url=model.image_url,
            color_hex=model.color_hex,
            popularity_score=model.popularity_score,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def entity_to_response_dto(self, entity: GenreEntity) -> GenreResponseDTO:
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
            is_active=entity.is_active,
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
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
