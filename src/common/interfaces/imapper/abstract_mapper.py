from abc import ABC

from src.common.interfaces.imapper.abstract_entity_dto_mapper import (
    AbstractEntityDtoMapper,
)
from src.common.interfaces.imapper.abstract_model_entity_mapper import (
    AbstractEntityModelMapper,
)
from src.common.mixins.logging_mixin import LoggingMixin
from src.common.types import DTOType, EntityType, ModelType


class AbstractMapper(
    AbstractEntityDtoMapper[EntityType, DTOType],
    AbstractEntityModelMapper[ModelType, EntityType],
    LoggingMixin,
    ABC,
):
    """
    Mapper completo que combina las operaciones de transformación
    entre modelo, entidad y DTO.
    """

    def __init__(self):
        super().__init__()
