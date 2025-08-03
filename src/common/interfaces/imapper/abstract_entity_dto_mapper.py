from abc import abstractmethod
from typing import Generic

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

    @abstractmethod
    def dto_to_entity(self, dto: DTOType) -> EntityType:
        """
        Convierte un DTO a una entidad del dominio.
        """
