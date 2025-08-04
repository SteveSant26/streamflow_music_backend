from abc import ABC
from typing import Generic, Type

from src.common.interfaces.imapper import AbstractEntityModelMapper
from src.common.types import EntityType, ModelType

from ...mixins.logging_mixin import LoggingMixin


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
