from src.common.interfaces.imapper.abstract_entity_dto_mapper import (
    AbstractEntityDtoMapper,
)
from src.common.interfaces.imapper.abstract_model_entity_mapper import (
    AbstractEntityModelMapper,
)
from src.common.types import DTOType, EntityType, ModelType


class AbstractMapper(
    AbstractEntityDtoMapper[EntityType, DTOType],
    AbstractEntityModelMapper[EntityType, ModelType],
):
    """
    Mapper completo que combina las operaciones de transformación
    entre modelo, entidad y DTO.
    """

    def __init__(self):
        super().__init__()
