from abc import abstractmethod
from typing import Generic, Iterable, TypeVar

from pyparsing import ABC

EntityType = TypeVar("EntityType")
DTOType = TypeVar("DTOType")


class AbstractEntityDtoMapper(Generic[EntityType, DTOType], ABC):
    """
    Mapper completo que combina las operaciones de transformación
    entre modelo, entidad y DTO.
    """

    def __init__(self):
        # Importación local para evitar importación circular
        from common.mixins.logging_mixin import LoggingMixin
        # Aplicar LoggingMixin manualmente
        LoggingMixin.__init__(self)

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
