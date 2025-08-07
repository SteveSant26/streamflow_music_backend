from typing import Generic, TypeVar

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from common.core.repositories.base_django_repository_mixin import (
    BaseDjangoRepositoryMixin,
)

from ...exceptions import NotFoundException
from ...interfaces import IWriteOnlyRepository

EntityType = TypeVar("EntityType")
ModelType = TypeVar("ModelType", bound=models.Model)


class BaseWriteOnlyDjangoRepository(
    IWriteOnlyRepository[EntityType, ModelType],
    BaseDjangoRepositoryMixin[EntityType, ModelType],
    Generic[EntityType, ModelType],
<<<<<<< HEAD
    # ABC,
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
):
    """
    Implementación base de solo escritura para Django que proporciona
    operaciones de modificación comunes para cualquier modelo de Django.
    """

    async def save(self, entity: EntityType) -> EntityType:
        try:
            model_data = self.mapper.entity_to_model_data(entity)

            model_instance, created = await self.model_class.objects.aupdate_or_create(
                id=getattr(entity, "id", None), defaults=model_data
            )

            action = "created" if created else "updated"
            self.logger.info(
                f"{self.model_class.__name__} {action} with id {model_instance.pk}"
            )
            return self.mapper.model_to_entity(model_instance)
        except Exception as e:
            self.logger.error(f"Error saving {self.model_class.__name__}: {str(e)}")
            raise

    async def delete(self, entity_id: str) -> bool:
        """Elimina completamente una entidad (hard delete)"""
        try:
            deleted_count, _ = await self.model_class.objects.filter(
                id=entity_id
            ).adelete()
            if deleted_count > 0:
                self.logger.info(
                    f"{self.model_class.__name__} with id {entity_id} was deleted"
                )
                return True
            else:
                self.logger.warning(
                    f"{self.model_class.__name__} with id {entity_id} not found for deletion"
                )
                return False
        except Exception as e:
            self.logger.error(
                f"Error deleting {self.model_class.__name__} with id {entity_id}: {str(e)}"
            )
            raise

    async def update(self, entity_id: str, entity: EntityType) -> EntityType:
        """Actualiza una entidad específica"""
        try:
            model_data = self.mapper.entity_to_model_data(entity)
            updated_count = await self.model_class.objects.filter(id=entity_id).aupdate(
                **model_data
            )

            if updated_count == 0:
                self.logger.warning(
                    f"{self.model_class.__name__} with id {entity_id} not found for update"
                )
                raise NotFoundException(
                    f"{self.model_class.__name__} with id {entity_id} does not exist"
                )

            updated_model = await self.model_class.objects.aget(id=entity_id)
            self.logger.info(
                f"{self.model_class.__name__} with id {entity_id} updated successfully"
            )
            return self.mapper.model_to_entity(updated_model)
        except ObjectDoesNotExist:
            raise NotFoundException(
                f"{self.model_class.__name__} with id {entity_id} does not exist"
            )
        except Exception as e:
            self.logger.error(
                f"Error updating {self.model_class.__name__} with id {entity_id}: {str(e)}"
            )
            raise
