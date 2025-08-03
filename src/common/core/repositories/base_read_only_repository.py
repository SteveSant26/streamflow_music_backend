from typing import List, Optional

from django.core.exceptions import ObjectDoesNotExist

from src.common.core.repositories.base_django_repository_mixin import (
    BaseDjangoRepositoryMixin,
)
from src.common.types import EntityType, ModelType

from ...interfaces import IReadOnlyRepository


class BaseReadOnlyDjangoRepository(
    IReadOnlyRepository[EntityType, ModelType],
    BaseDjangoRepositoryMixin[EntityType, ModelType],
):
    """
    Implementación base de solo lectura para Django que proporciona

    operaciones de consulta comunes para cualquier modelo de Django.
    """

    async def get_by_id(self, entity_id: str) -> Optional[EntityType]:
        """Obtiene una entidad por ID"""
        try:
            model_instance = await self.model_class.objects.aget(id=entity_id)
            return self.mapper.model_to_entity(model_instance)
        except ObjectDoesNotExist:
            self.logger.debug(
                f"{self.model_class.__name__} with id {entity_id} not found"
            )
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting {self.model_class.__name__} by id {entity_id}: {str(e)}"
            )
            raise

    async def get_all(self) -> List[EntityType]:
        """Obtiene todas las entidades activas"""
        try:
            models = self.model_class.objects.all()
            return self.mapper.models_to_entities(models)
        except Exception as e:
            self.logger.error(
                f"Error getting all {self.model_class.__name__}: {str(e)}"
            )
            raise

    async def exists(self, entity_id: str) -> bool:
        """Verifica si una entidad existe"""
        try:
            return await self.model_class.objects.filter(id=entity_id).aexists()
        except Exception as e:
            self.logger.error(
                f"Error checking existence of {self.model_class.__name__} with id {entity_id}: {str(e)}"
            )
            raise

    async def count(self) -> int:
        """Cuenta el número total de entidades activas"""
        try:
            return await self.model_class.objects.all().acount()
        except Exception as e:
            self.logger.error(f"Error counting {self.model_class.__name__}: {str(e)}")
            raise
