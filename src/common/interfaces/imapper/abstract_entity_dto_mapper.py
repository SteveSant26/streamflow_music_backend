from abc import abstractmethod
from typing import Generic, Iterable, TypeVar

from pyparsing import ABC

<<<<<<< HEAD
from common.mixins.logging_mixin import LoggingMixin
=======
from src.common.utils.logging_config import get_logger
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

EntityType = TypeVar("EntityType")
DTOType = TypeVar("DTOType")


<<<<<<< HEAD
class AbstractEntityDtoMapper(Generic[EntityType, DTOType], ABC, LoggingMixin):
=======
class AbstractEntityDtoMapper(Generic[EntityType, DTOType], ABC):
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    """
    Mapper completo que combina las operaciones de transformación
    entre modelo, entidad y DTO.
    """

<<<<<<< HEAD
=======
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
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
