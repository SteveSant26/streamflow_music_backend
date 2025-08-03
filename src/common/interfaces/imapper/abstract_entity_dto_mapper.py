from abc import abstractmethod
from typing import Generic, Iterable

from pyparsing import ABC

from src.common.mixins.logging_mixin import LoggingMixin
from src.common.types import DTOType, EntityType


class AbstractEntityDtoMapper(LoggingMixin, ABC, Generic[EntityType, DTOType]):
    """
    Mapper completo que combina las operaciones de transformación
    entre modelo, entidad y DTO.
    """

    @abstractmethod
    def entity_to_dto(self, entity: EntityType) -> DTOType:
        """
        Convierte una entidad del dominio a un DTO.
        """

    def entities_to_dtos(self, entities: Iterable[EntityType]) -> list[DTOType]:
        """
        Convierte una lista de entidades del dominio a una lista de DTOs.
        """
        return [self.entity_to_dto(entity) for entity in entities]

    @abstractmethod
    def dto_to_entity(self, dto: DTOType) -> EntityType:
        """
        Convierte un DTO a una entidad del dominio.
        """

    def dtos_to_entities(self, dtos: Iterable[DTOType]) -> list[EntityType]:
        """
        Convierte una lista de DTOs a una lista de entidades del dominio.
        """
        return [self.dto_to_entity(dto) for dto in dtos]
