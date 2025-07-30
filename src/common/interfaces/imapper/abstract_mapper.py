from .dto_to_entity import DTOToEntityMapper
from .entity_to_response_dto import EntityToResponseDTOMapper
from .model_to_entity import ModelToEntityMapper


class AbstractMapper(
    ModelToEntityMapper,
    EntityToResponseDTOMapper,
    DTOToEntityMapper,
):
    """
    Mapper completo que combina las operaciones de transformación
    entre modelo, entidad y DTO.
    """
