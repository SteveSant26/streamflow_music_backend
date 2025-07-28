from abc import ABC, abstractmethod
from typing import Generic, Optional

from .types import EntityType, ModelType


class IReadOnlyRepository(ABC, Generic[EntityType, ModelType]):
    """Repositorio de solo lectura para operaciones de consulta."""

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[EntityType]:
        """Obtiene una entidad por ID."""

    @abstractmethod
    def _model_to_entity(self, model: ModelType) -> EntityType:
        """Convierte un modelo a su entidad correspondiente."""


class IWriteOnlyRepository(ABC, Generic[EntityType, ModelType]):
    """Repositorio de escritura para operaciones de modificación."""

    @abstractmethod
    def save(self, entity: EntityType) -> EntityType:
        """Guarda una entidad."""

    @abstractmethod
    def delete(self, entity_id: str) -> None:
        """Elimina una entidad por ID."""

    @abstractmethod
    def update(self, entity_id: str, entity: EntityType) -> EntityType:
        """Actualiza una entidad."""

    @abstractmethod
    def _entity_to_model(self, entity: EntityType) -> ModelType:
        """Convierte una entidad a su modelo correspondiente."""


class IBaseRepository(
    IReadOnlyRepository[EntityType, ModelType],
    IWriteOnlyRepository[EntityType, ModelType],
    Generic[EntityType, ModelType],
):
    """Repositorio completo que combina operaciones de lectura y escritura."""
