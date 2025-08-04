from src.common.interfaces.imapper.abstract_mapper import AbstractMapper

from .genre_entity_dto_mapper import GenreEntityDTOMapper
from .genre_entity_model_mapper import GenreEntityModelMapper


class GenreMapper(GenreEntityModelMapper, GenreEntityDTOMapper, AbstractMapper):
    """Mapper completo para convertir entre modelos, entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()
