from common.interfaces.imapper.abstract_mapper import AbstractMapper

from .artist_entity_dto_mapper import ArtistEntityDTOMapper
from .artist_entity_model_mapper import ArtistEntityModelMapper


class ArtistMapper(
    ArtistEntityModelMapper,
    ArtistEntityDTOMapper,
    AbstractMapper,
):
    """Mapper completo para convertir entre modelos, entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()
