from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Define type variables locally for this interface
DTOType = TypeVar("DTOType")
EntityType = TypeVar("EntityType")


class DTOToEntityMapper(ABC, Generic[DTOType, EntityType]):
    @abstractmethod
    def dto_to_entity(self, dto: DTOType) -> EntityType:
        """
        Convierte un DTO a una entidad del dominio.
        """
