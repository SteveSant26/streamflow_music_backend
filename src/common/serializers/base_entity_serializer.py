from typing import Any, Optional, Type

from rest_framework import serializers

from common.interfaces.imapper.abstract_mapper import AbstractMapper
from src.common.utils import get_logger

logger = get_logger(__name__)


class BaseEntitySerializer(serializers.Serializer):
    """
    Serializer base que maneja automáticamente la conversión entidad → DTO.
    Otros serializers pueden heredar de este para obtener la funcionalidad automática.
    """

    mapper_class: Optional[AbstractMapper] = None
    entity_class: Optional[Type] = None
    dto_class: Optional[Type] = None

    def to_representation(self, instance: Any) -> dict:
        """
        Convierte automáticamente entidades o modelos a DTOs, y luego a representación JSON.
        """
        logger.debug(f"[to_representation] instance type: {type(instance)}")

        if not self.mapper_class or not self.entity_class or not self.dto_class:
            raise NotImplementedError(
                f"{self.__class__.__name__} debe definir mapper_class, entity_class y dto_class"
            )

        try:
            if isinstance(instance, self.dto_class):
                logger.debug("Instancia es un DTO, convirtiendo a dict")
                return self._dto_to_dict(instance)

            if isinstance(instance, self.entity_class):
                logger.debug("Instancia es una entidad, mapeando a DTO")
                dto = self.mapper_class.entity_to_response_dto(instance)
                return self._dto_to_dict(dto)

            if getattr(instance, "_meta", None) and getattr(
                instance._meta, "app_label", None
            ):
                logger.debug(
                    "Instancia es un modelo de Django, mapeando a entidad y luego a DTO"
                )
                entity = self.mapper_class.model_to_entity(instance)
                dto = self.mapper_class.entity_to_response_dto(entity)
                return self._dto_to_dict(dto)

            raise TypeError(
                f"{self.__class__.__name__} no puede manejar instancia de tipo: {type(instance)}"
            )

        except Exception as e:
            logger.exception(f"[to_representation] Error: {e}")
            raise

    def _dto_to_dict(self, dto_instance: Any) -> dict:
        """Convierte un DTO a dict. Override si necesitas lógica personalizada."""
        if hasattr(dto_instance, "__dataclass_fields__"):
            return {
                field: getattr(dto_instance, field)
                for field in dto_instance.__dataclass_fields__
            }

        return getattr(dto_instance, "__dict__", {})
