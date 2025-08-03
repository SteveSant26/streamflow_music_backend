from src.common.interfaces.imapper.abstract_mapper import AbstractMapper

from .user_profile_entity_dto_mapper import UserProfileEntityDTOMapper
from .user_profile_entity_model_mapper import UserProfileEntityModelMapper


class UserProfileMapper(
    AbstractMapper, UserProfileEntityModelMapper, UserProfileEntityDTOMapper
):
    """Mapper para convertir entre entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()
