from src.common.interfaces.imapper.abstract_mapper import AbstractMapper

from .album_entity_dto_mapper import AlbumEntityDTOMapper
from .album_entity_model_mapper import AlbumEntityModelMapper


class AlbumMapper(AbstractMapper, AlbumEntityModelMapper, AlbumEntityDTOMapper):
    """Mapper completo para convertir entre modelos, entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()
