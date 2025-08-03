from abc import ABC, abstractmethod
from typing import Generic

from src.common.mixins.logging_mixin import LoggingMixin
from src.common.types import EntityType, ModelType


class AbstractEntityModelMapper(LoggingMixin, ABC, Generic[ModelType, EntityType]):
    @abstractmethod
    def model_to_entity(self, model: ModelType) -> EntityType:
        """
        Convierte un modelo a una entidad del dominio.
        """

    @abstractmethod
    def entity_to_model(self, entity: EntityType) -> ModelType:
        """
        Convierte una entidad del dominio a un modelo.
        """
