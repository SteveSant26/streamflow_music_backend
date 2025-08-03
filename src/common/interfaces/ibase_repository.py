from abc import ABC, abstractmethod
from typing import Generic, Optional

from ..types import EntityType, ModelType


class IReadOnlyRepository(ABC, Generic[EntityType, ModelType]):
    """Repositorio de solo lectura para operaciones de consulta."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[EntityType]:
        """Obtiene una entidad por ID."""

    @abstractmethod
    async def get_all(self) -> list[EntityType]:
        """Obtiene todas las entidades, opcionalmente filtradas."""


class IWriteOnlyRepository(ABC, Generic[EntityType, ModelType]):
    """Repositorio de escritura para operaciones de modificación."""

    @abstractmethod
    async def save(self, entity: EntityType) -> EntityType:
        """Guarda una entidad."""

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Elimina una entidad por ID."""

    @abstractmethod
    async def update(self, entity_id: str, entity: EntityType) -> EntityType:
        """Actualiza una entidad."""


class IBaseRepository(
    IReadOnlyRepository[EntityType, ModelType],
    IWriteOnlyRepository[EntityType, ModelType],
    Generic[EntityType, ModelType],
):
    """Repositorio completo que combina operaciones de lectura y escritura."""
