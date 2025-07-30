from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Define type variables locally for this interface
ModelType = TypeVar("ModelType")
EntityType = TypeVar("EntityType")


class ModelToEntityMapper(ABC, Generic[ModelType, EntityType]):
    @abstractmethod
    def model_to_entity(self, model: ModelType) -> EntityType:
        """
        Convierte un modelo a una entidad del dominio.
        """
