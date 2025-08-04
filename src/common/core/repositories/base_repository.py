# from abc import ABC

from ...types import EntityType, ModelType
from .base_read_only_repository import BaseReadOnlyDjangoRepository
from .base_write_only_repository import BaseWriteOnlyDjangoRepository


class BaseDjangoRepository(
    BaseReadOnlyDjangoRepository[EntityType, ModelType],
    BaseWriteOnlyDjangoRepository[EntityType, ModelType],
    # ABC,
):
    """
    Implementación base completa de repositorio para Django que combina
    operaciones de lectura y escritura.

    Esta clase hereda de ambos repositorios especializados (solo lectura y solo escritura)
    proporcionando una interfaz completa para operaciones CRUD.

    """
