from abc import ABC
from typing import Generic, Type

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from src.common.interfaces.imapper import AbstractEntityModelMapper

from ...exceptions import NotFoundException
from ...interfaces import IWriteOnlyRepository
from ...mixins.logging_mixin import LoggingMixin
from ...types import EntityType, ModelType


class BaseWriteOnlyDjangoRepository(
    Generic[EntityType, ModelType],
    IWriteOnlyRepository[EntityType, ModelType],
    LoggingMixin,
    ABC,
):
    """
    Implementación base de solo escritura para Django que proporciona
    operaciones de modificación comunes para cualquier modelo de Django.
    """

    def __init__(
        self,
        model_class: Type[ModelType],
        mapper: AbstractEntityModelMapper,
        *args,
        **kwargs,
    ):
        self.model_class = model_class
        self.mapper = mapper

    async def save(self, entity: EntityType) -> EntityType:
        try:
            model_data = self.mapper.entity_to_model(entity)

            # Wrapping the sync ORM call inside sync_to_async
            model_instance, created = await sync_to_async(
                self.model_class.objects.update_or_create
            )(id=getattr(entity, "id", None), defaults=model_data)

            action = "created" if created else "updated"
            self.logger.info(
                f"{self.model_class.__name__} {action} with id {model_instance.pk}"
            )
            return self.mapper.model_to_entity(model_instance)
        except Exception as e:
            self.logger.error(f"Error saving {self.model_class.__name__}: {str(e)}")
            raise

    async def delete(self, entity_id: str) -> bool:
        """Elimina lógicamente una entidad (soft delete)"""
        try:
            updated_count = self.model_class.objects.filter(id=entity_id).update(
                is_active=False
            )
            if updated_count > 0:
                self.logger.info(
                    f"{self.model_class.__name__} with id {entity_id} marked as inactive"
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
            model_data = self.mapper.entity_to_model(entity)
            updated_count = await sync_to_async(
                self.model_class.objects.filter(id=entity_id).update
            )(**model_data)

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

    async def hard_delete(self, entity_id: str) -> None:
        """Elimina físicamente una entidad de la base de datos"""
        try:
            deleted_count, _ = await sync_to_async(
                self.model_class.objects.filter(id=entity_id).delete
            )()
            if deleted_count > 0:
                self.logger.info(
                    f"{self.model_class.__name__} with id {entity_id} permanently deleted"
                )
            else:
                self.logger.warning(
                    f"{self.model_class.__name__} with id {entity_id} not found for hard deletion"
                )
        except Exception as e:
            self.logger.error(
                f"Error hard deleting {self.model_class.__name__} with id {entity_id}: {str(e)}"
            )
            raise
