from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, cast

from django.core.exceptions import ObjectDoesNotExist

from common.mixins.logging_mixin import LoggingMixin

from ...interfaces import IReadOnlyRepository
from ...types import EntityType, ModelType


class BaseReadOnlyDjangoRepository(
    Generic[EntityType, ModelType],
    IReadOnlyRepository[EntityType, ModelType],
    LoggingMixin,
    ABC,
):
    """
    Implementación base de solo lectura para Django que proporciona
    operaciones de consulta comunes para cualquier modelo de Django.
    """

    def __init__(self, model_class: Type[ModelType], *args, **kwargs):
        self.model_class = model_class

    async def get_by_id(self, entity_id: str) -> Optional[EntityType]:
        """Obtiene una entidad por ID"""
        try:
            model_instance = await self.model_class.objects.aget(
                id=entity_id, **self._get_active_filter()
            )
            return self._model_to_entity(model_instance)
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
            queryset = await self.model_class.objects.afilter(
                **self._get_active_filter()
            )
            queryset = self._apply_default_ordering(queryset)
            return [self._model_to_entity(cast(ModelType, model)) for model in queryset]
        except Exception as e:
            self.logger.error(
                f"Error getting all {self.model_class.__name__}: {str(e)}"
            )
            raise

    def exists(self, entity_id: str) -> bool:
        """Verifica si una entidad existe"""
        try:
            return self.model_class.objects.filter(
                id=entity_id, **self._get_active_filter()
            ).exists()
        except Exception as e:
            self.logger.error(
                f"Error checking existence of {self.model_class.__name__} with id {entity_id}: {str(e)}"
            )
            raise

    def count(self) -> int:
        """Cuenta el número total de entidades activas"""
        try:
            return self.model_class.objects.filter(**self._get_active_filter()).count()
        except Exception as e:
            self.logger.error(f"Error counting {self.model_class.__name__}: {str(e)}")
            raise

    # Métodos protegidos que pueden ser sobrescritos por las subclases

    def _get_active_filter(self) -> dict:
        """
        Retorna el filtro para entidades activas.
        Override este método si el modelo usa un campo diferente para soft delete.
        """
        if hasattr(self.model_class, "is_active"):
            return {"is_active": True}
        return {}

    def _apply_default_ordering(self, queryset):
        """
        Aplica el ordenamiento por defecto al queryset.
        Override este método para personalizar el ordenamiento.
        """
        if hasattr(self.model_class, "created_at"):
            return queryset.order_by("-created_at")
        return queryset

    # Método abstracto que debe ser implementado por las subclases

    @abstractmethod
    def _model_to_entity(self, model: ModelType) -> EntityType:
        """Convierte un modelo a su entidad correspondiente"""
