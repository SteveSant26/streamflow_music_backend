from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Define type variables locally for this interface
EntityType = TypeVar("EntityType")
DTOType = TypeVar("DTOType")


class EntityToResponseDTOMapper(ABC, Generic[EntityType, DTOType]):
    @abstractmethod
    def entity_to_response_dto(self, entity: EntityType) -> DTOType:
        """
        Convierte una entidad del dominio a un DTO de respuesta.
        """
