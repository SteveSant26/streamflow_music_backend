from abc import ABC
from typing import Generic, Type, TypeVar

from common.interfaces.imapper import AbstractEntityModelMapper
from src.common.utils.logging_config import get_logger

EntityType = TypeVar("EntityType")
ModelType = TypeVar("ModelType")


class BaseDjangoRepositoryMixin(ABC, Generic[EntityType, ModelType]):
    """
    Mixin base que proporciona funcionalidad común para repositorios Django.

    Define la inicialización estándar del mapper y model_class que será
    compartida por todos los repositorios Django.
    """

    def __init__(
        self,
        model_class: Type[ModelType],
        mapper: AbstractEntityModelMapper[EntityType, ModelType],
        *args,
        **kwargs,
    ):
        self.model_class = model_class
        self.mapper = mapper
        super().__init__(*args, **kwargs)

        # Añadir logging sin importación circular
        self.logger = get_logger(self.__class__.__name__)
