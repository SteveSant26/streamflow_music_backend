from abc import ABC, abstractmethod
from typing import Generic

from ..types import EntityType, InputType, ModelType, ReturnType
from ..utils.logging_decorators import log_execution, log_performance
from .ibase_repository import IReadOnlyRepository


class BaseUseCase(ABC, Generic[InputType, ReturnType]):
    """Clase base para casos de uso."""

    def __init__(self):
        super().__init__()
        # Añadir logging sin importación circular
        from ..utils.logging_helper import add_logging_to_instance
        add_logging_to_instance(self)

    @abstractmethod
    async def execute(self, *args, **kwargs) -> ReturnType:
        """Ejecuta el caso de uso."""


class BaseGetByIdUseCase(BaseUseCase[str, EntityType], Generic[EntityType, ModelType]):
    """Clase base para casos de uso de obtener por ID."""

    def __init__(self, repository: IReadOnlyRepository[EntityType, ModelType]):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, entity_id: str) -> EntityType:
        """Obtiene una entidad por ID."""
        self.logger.debug(f"Getting entity with ID: {entity_id}")
        entity = await self.repository.get_by_id(entity_id)

        if not entity:
            self.logger.warning(f"Entity not found with ID: {entity_id}")
            raise self._get_not_found_exception(entity_id)

        self.logger.info(f"Successfully retrieved entity: {entity_id}")
        return entity

    @abstractmethod
    def _get_not_found_exception(self, entity_id: str) -> Exception:
        """Obtiene la excepción para entidad no encontrada."""


class BaseGetAllUseCase(
    BaseUseCase[None, list[EntityType]], Generic[EntityType, ModelType]
):
    """Clase base para casos de uso de obtener todas las entidades."""

    def __init__(self, repository: IReadOnlyRepository[EntityType, ModelType]):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)
    async def execute(self) -> list[EntityType]:
        """Obtiene todas las entidades."""
        self.logger.debug("Getting all entities")
        entities = await self.repository.get_all()

        if not entities:
            self.logger.warning("No entities found")
            return []

        self.logger.info(f"Successfully retrieved {len(entities)} entities")
        return entities
