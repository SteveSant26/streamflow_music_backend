from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Iterable, TypeVar


EntityType = TypeVar("EntityType")
ModelType = TypeVar("ModelType")


class AbstractEntityModelMapper(Generic[EntityType, ModelType], ABC):
    
    def __init__(self):
        # Añadir logging sin importación circular
        from common.utils.logging_helper import add_logging_to_instance
        add_logging_to_instance(self)
    
    @abstractmethod
    def model_to_entity(self, model: ModelType) -> EntityType:
        """
        Convierte un modelo a una entidad del dominio.
        """

    def models_to_entities(self, models: Iterable[ModelType]) -> list[EntityType]:
        """
        Convierte una lista de modelos a una lista de entidades del dominio.
        """
        return [self.model_to_entity(model) for model in models]

    @abstractmethod
    def entity_to_model(self, entity: EntityType) -> ModelType:
        """
        Convierte una entidad del dominio a un modelo.
        """

    def entities_to_models(self, entities: Iterable[EntityType]) -> list[ModelType]:
        """
        Convierte una lista de entidades del dominio a una lista de modelos.
        """
        return [self.entity_to_model(entity) for entity in entities]

    @abstractmethod
    def entity_to_model_data(self, entity: EntityType) -> Dict[str, Any]:
        """
        Convierte una entidad del dominio a datos del modelo (diccionario).
        """

    def entities_to_model_data(
        self, entities: list[EntityType]
    ) -> list[Dict[str, Any]]:
        """
        Convierte una lista de entidades del dominio a una lista de datos del modelo (diccionario).
        """
        return [self.entity_to_model_data(entity) for entity in entities]
