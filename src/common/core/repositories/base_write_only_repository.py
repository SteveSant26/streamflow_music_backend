from abc import ABC, abstractmethod
from typing import Generic, Type

from django.core.exceptions import ObjectDoesNotExist

from common.mixins.logging_mixin import LoggingMixin

from ...interfaces import IWriteOnlyRepository
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

    def __init__(self, model_class: Type[ModelType], *args, **kwargs):
        self.model_class = model_class

    def save(self, entity: EntityType) -> EntityType:
        """Guarda una entidad (crear o actualizar)"""
        try:
            model_data = self._entity_to_model_data(entity)
            model_instance, created = self.model_class.objects.update_or_create(
                id=getattr(entity, "id", None), defaults=model_data
            )
            action = "created" if created else "updated"
            self.logger.info(
                f"{self.model_class.__name__} {action} with id {model_instance.pk}"
            )
            return self._model_to_entity(model_instance)
        except Exception as e:
            self.logger.error(f"Error saving {self.model_class.__name__}: {str(e)}")
            raise

    def delete(self, entity_id: str) -> None:
        """Elimina lógicamente una entidad (soft delete)"""
        try:
            updated_count = self.model_class.objects.filter(id=entity_id).update(
                is_active=False
            )
            if updated_count > 0:
                self.logger.info(
                    f"{self.model_class.__name__} with id {entity_id} marked as inactive"
                )
            else:
                self.logger.warning(
                    f"{self.model_class.__name__} with id {entity_id} not found for deletion"
                )
        except Exception as e:
            self.logger.error(
                f"Error deleting {self.model_class.__name__} with id {entity_id}: {str(e)}"
            )
            raise

    def update(self, entity_id: str, entity: EntityType) -> EntityType:
        """Actualiza una entidad específica"""
        try:
            model_data = self._entity_to_model_data(entity)
            updated_count = self.model_class.objects.filter(id=entity_id).update(
                **model_data
            )

            if updated_count == 0:
                self.logger.warning(
                    f"{self.model_class.__name__} with id {entity_id} not found for update"
                )
                raise ObjectDoesNotExist(
                    f"{self.model_class.__name__} with id {entity_id} does not exist"
                )

            updated_model = self.model_class.objects.get(id=entity_id)
            self.logger.info(
                f"{self.model_class.__name__} with id {entity_id} updated successfully"
            )
            return self._model_to_entity(updated_model)
        except ObjectDoesNotExist:
            raise
        except Exception as e:
            self.logger.error(
                f"Error updating {self.model_class.__name__} with id {entity_id}: {str(e)}"
            )
            raise

    def hard_delete(self, entity_id: str) -> None:
        """Elimina físicamente una entidad de la base de datos"""
        try:
            deleted_count, _ = self.model_class.objects.filter(id=entity_id).delete()
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

    def _entity_to_model_data(self, entity: EntityType) -> dict:
        """
        Convierte una entidad a datos del modelo.
        Este método debe ser implementado por las subclases.
        """
        raise NotImplementedError(
            "Subclasses must implement _entity_to_model_data method"
        )

    # Métodos abstractos que deben ser implementados por las subclases

    @abstractmethod
    def _model_to_entity(self, model: ModelType) -> EntityType:
        """Convierte un modelo a su entidad correspondiente - requerido para operaciones de escritura"""

    @abstractmethod
    def _entity_to_model(self, entity: EntityType) -> ModelType:
        """Convierte una entidad a su modelo correspondiente"""
