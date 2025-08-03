from abc import ABC
from typing import Type

from src.common.interfaces.imapper.abstract_model_entity_mapper import (
    AbstractEntityModelMapper,
)

from ...interfaces import IBaseRepository
from ...types import EntityType, ModelType
from .base_read_only_repository import BaseReadOnlyDjangoRepository
from .base_write_only_repository import BaseWriteOnlyDjangoRepository


class BaseDjangoRepository(
    BaseReadOnlyDjangoRepository[EntityType, ModelType],
    BaseWriteOnlyDjangoRepository[EntityType, ModelType],
    IBaseRepository[EntityType, ModelType],
    ABC,
):
    """
    Implementación base completa de repositorio para Django que combina
    operaciones de lectura y escritura.

    Esta clase hereda de ambos repositorios especializados (solo lectura y solo escritura)
    proporcionando una interfaz completa para operaciones CRUD.
    """

    def __init__(self, model_class: Type[ModelType], mapper: AbstractEntityModelMapper):
        """
        Inicializa el repositorio con la clase de modelo de Django.

        Args:
            model_class: La clase del modelo de Django que este repositorio manejará
        """
        # Configurar atributos comunes una sola vez
        self.model_class = model_class
        self.mapper = mapper
