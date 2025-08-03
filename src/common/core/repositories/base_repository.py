from abc import ABC

from ...interfaces import IBaseRepository
from ...types import EntityType, ModelType
from .base_read_only_repository import BaseReadOnlyDjangoRepository
from .base_write_only_repository import BaseWriteOnlyDjangoRepository


class BaseDjangoRepository(  # type: ignore
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

    No necesita definir __init__ ya que lo hereda del mixin común.
    """
