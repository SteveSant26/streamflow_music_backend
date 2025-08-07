from abc import ABC
from typing import Generic, Type, TypeVar

from common.interfaces.imapper import AbstractEntityModelMapper
<<<<<<< HEAD

from ...mixins.logging_mixin import LoggingMixin
=======
from src.common.utils.logging_config import get_logger
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

EntityType = TypeVar("EntityType")
ModelType = TypeVar("ModelType")


<<<<<<< HEAD
class BaseDjangoRepositoryMixin(ABC, Generic[EntityType, ModelType], LoggingMixin):
=======
class BaseDjangoRepositoryMixin(ABC, Generic[EntityType, ModelType]):
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
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
<<<<<<< HEAD
=======

        # Añadir logging sin importación circular
        self.logger = get_logger(self.__class__.__name__)
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
