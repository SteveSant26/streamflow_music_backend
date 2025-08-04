from abc import ABC
from typing import Generic, Type, TypeVar

from common.interfaces.imapper import AbstractEntityModelMapper

from ...mixins.logging_mixin import LoggingMixin

EntityType = TypeVar("EntityType")
ModelType = TypeVar("ModelType")


class BaseDjangoRepositoryMixin(ABC, Generic[EntityType, ModelType], LoggingMixin):
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
