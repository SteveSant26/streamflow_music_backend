from src.common.interfaces.imapper.abstract_mapper import AbstractMapper

from .song_entity_dto_mapper import SongEntityDTOMapper
from .song_entity_model_mapper import SongEntityModelMapper


class SongMapper(AbstractMapper, SongEntityModelMapper, SongEntityDTOMapper):
    """Mapper completo para convertir entre modelos, entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()
